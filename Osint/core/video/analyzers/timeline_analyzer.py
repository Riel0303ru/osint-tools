# core/video/analyzers/timeline_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
from core.base.scan_result import ScanResult
from core.video.models.timeline_event import TimelineEvent
from utils.logger import Logger


class TimelineAnalyzer:
    """
    Membangun timeline terpadu dari semua event yang terdeteksi.
    Event dari frame, wajah, objek, OCR, dan audio digabungkan
    ke dalam kronologi terstruktur.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(
        self,
        frame_results: ScanResult | None = None,
        face_results: ScanResult | None = None,
        object_results: ScanResult | None = None,
        ocr_results: ScanResult | None = None,
        audio_results: ScanResult | None = None,
        env_results: ScanResult | None = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Gabungkan semua event dari hasil analyzer yang berbeda
        ke dalam satu timeline.

        Returns:
            ScanResult dengan list TimelineEvent terurut.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        all_events: List[TimelineEvent] = []

        # 1. Frame events (scene changes / keyframes)
        all_events.extend(self._extract_frame_events(frame_results))

        # 2. Face events
        all_events.extend(self._extract_face_events(face_results))

        # 3. Object events
        all_events.extend(self._extract_object_events(object_results))

        # 4. OCR events
        all_events.extend(self._extract_ocr_events(ocr_results))

        # 5. Audio events
        all_events.extend(self._extract_audio_events(audio_results))

        # 6. Environment events
        all_events.extend(self._extract_environment_events(env_results))

        # Urutkan berdasarkan timestamp
        all_events.sort(key=lambda e: e.timestamp)

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Timeline Analysis",
            username=filename,
            status="FOUND" if all_events else "NOT_FOUND",
            status_code=200 if all_events else 404,
            url=file_path,
            confidence=0.95 if all_events else 0.5,
            extra={
                "total_events": len(all_events),
                "events": [e.to_dict() for e in all_events],
                "analysis_time_seconds": analysis_time,
            },
        )

    # ---------- Event Extractors ----------

    def _extract_frame_events(self, result: ScanResult | None) -> List[TimelineEvent]:
        """Ekstrak event dari frame extraction."""
        events: List[TimelineEvent] = []
        if not result or result.status != "FOUND":
            return events

        frames = result.extra.get("frames", []) if result.extra else []
        for f in frames:
            ts = f.get("timestamp_seconds", 0)
            events.append(TimelineEvent(
                timestamp=ts,
                event_type="frame",
                description=f"Keyframe extracted",
                confidence=1.0,
                source="Frame Extraction",
                frame_index=f.get("index"),
                extra={"frame_path": f.get("path", "")},
            ))
        return events

    def _extract_face_events(self, result: ScanResult | None) -> List[TimelineEvent]:
        """Ekstrak event dari face detection."""
        events: List[TimelineEvent] = []
        if not result or result.status != "FOUND":
            return events

        faces = result.extra.get("findings", []) if result.extra else []
        for f in faces:
            ts = f.get("timestamp", 0)
            count = 1  # setiap finding = 1 wajah
            events.append(TimelineEvent(
                timestamp=ts,
                event_type="face",
                description=f"Face detected (confidence: {f.get('confidence', 0.9):.2f})",
                confidence=f.get("confidence", 0.9),
                source="Face Detection",
                frame_index=f.get("frame_index"),
                extra={"bounding_box": f.get("bounding_box", [])},
            ))
        return events

    def _extract_object_events(self, result: ScanResult | None) -> List[TimelineEvent]:
        """Ekstrak event dari object detection."""
        events: List[TimelineEvent] = []
        if not result or result.status != "FOUND":
            return events

        objects = result.extra.get("findings", []) if result.extra else []
        for obj in objects:
            ts = obj.get("timestamp", 0)
            obj_name = obj.get("object", "unknown")
            events.append(TimelineEvent(
                timestamp=ts,
                event_type="object",
                description=f"Object detected: {obj_name} (confidence: {obj.get('confidence', 0):.2f})",
                confidence=obj.get("confidence", 0.5),
                source="Object Detection",
                frame_index=obj.get("frame_index"),
                extra={"object": obj_name},
            ))
        return events

    def _extract_ocr_events(self, result: ScanResult | None) -> List[TimelineEvent]:
        """Ekstrak event dari OCR analysis."""
        events: List[TimelineEvent] = []
        if not result or result.status != "FOUND":
            return events

        findings = result.extra.get("findings", []) if result.extra else []
        for f in findings:
            ts = f.get("timestamp", 0)
            text = f.get("text", "")[:100]
            if text:
                events.append(TimelineEvent(
                    timestamp=ts,
                    event_type="ocr",
                    description=f"OCR text: '{text}'",
                    confidence=f.get("confidence", 0.8),
                    source="OCR Analysis",
                    frame_index=f.get("frame_index"),
                    extra={"text": text},
                ))
        return events

    def _extract_audio_events(self, result: ScanResult | None) -> List[TimelineEvent]:
        """Ekstrak event dari audio analysis (transkrip)."""
        events: List[TimelineEvent] = []
        if not result or result.status not in ("FOUND", "SUCCESS"):
            return events

        segments = result.extra.get("segments", []) if result.extra else []
        for seg in segments[:30]:  # batasi 30 segmen
            start = seg.get("start", 0)
            text = seg.get("text", "")[:200]
            if text:
                events.append(TimelineEvent(
                    timestamp=start,
                    event_type="audio",
                    description=f"Spoken: '{text}'",
                    confidence=0.85,
                    source="Audio Analysis",
                    extra={"text": text, "end": seg.get("end", start)},
                ))
        return events

    def _extract_environment_events(self, result: ScanResult | None) -> List[TimelineEvent]:
        """Ekstrak event dari environment analysis."""
        events: List[TimelineEvent] = []
        if not result or result.status != "FOUND":
            return events

        # Ambil evidence sebagai event di awal timeline (timestamp 0)
        evidence = result.extra.get("evidence", []) if result.extra else []
        for hint in evidence:
            events.append(TimelineEvent(
                timestamp=0.0,
                event_type="environment",
                description=f"Environment: {hint}",
                confidence=0.8,
                source="Environment Analysis",
                extra={"hint": hint},
            ))
        return events