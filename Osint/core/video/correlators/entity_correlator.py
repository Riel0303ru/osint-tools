# core/video/correlators/entity_correlator.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.models.video_entity import VideoEntity
from utils.logger import Logger


class EntityCorrelator:
    """
    Mengumpulkan semua entitas yang diekstrak dari video (email, telepon, URL,
    username, lokasi) dan menyiapkannya untuk dikirim ke Correlation Engine global.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def collect_entities(
        self,
        metadata_result: Optional[ScanResult] = None,
        ocr_result: Optional[ScanResult] = None,
        audio_analysis: Optional[ScanResult] = None,
        language_result: Optional[ScanResult] = None,
        geolocation_result: Optional[ScanResult] = None,
        risk_result: Optional[ScanResult] = None,
        file_path: str = "",
    ) -> List[VideoEntity]:
        """
        Kumpulkan semua entitas dari hasil analisis video.
        Mengembalikan list VideoEntity yang siap dikorelasikan.
        """
        entities: List[VideoEntity] = []

        # 1. Dari OCR
        if ocr_result and ocr_result.status == "FOUND":
            entities.extend(self._from_ocr(ocr_result))

        # 2. Dari Audio Transkrip
        if audio_analysis and audio_analysis.status in ("FOUND", "SUCCESS"):
            entities.extend(self._from_audio(audio_analysis))

        # 3. Dari Metadata (GPS)
        if metadata_result and metadata_result.status == "FOUND":
            entities.extend(self._from_metadata(metadata_result))

        # 4. Dari Geolocation
        if geolocation_result and geolocation_result.status == "FOUND":
            entities.extend(self._from_geolocation(geolocation_result))

        # 5. Dari Language
        if language_result and language_result.status == "FOUND":
            entities.extend(self._from_language(language_result))

        # Deduplikasi berdasarkan (entity_type, value)
        unique = {}
        for e in entities:
            key = (e.entity_type, e.value.lower())
            if key not in unique or e.confidence > unique[key].confidence:
                unique[key] = e

        self.logger.info(f"Collected {len(unique)} unique entities from video")
        return list(unique.values())

    def correlate_and_report(
        self,
        entities: List[VideoEntity],
        file_path: str = "",
    ) -> ScanResult:
        """
        Buat ScanResult yang berisi entitas terkumpul, siap untuk
        diumpankan ke core/correlation.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        # Kategorikan entitas
        by_type = {}
        for e in entities:
            by_type.setdefault(e.entity_type, []).append(e.value)

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Entity Correlation",
            username=filename,
            status="FOUND" if entities else "NOT_FOUND",
            status_code=200 if entities else 404,
            url=file_path,
            confidence=0.9 if entities else 0.0,
            extra={
                "total_entities": len(entities),
                "entities_by_type": {k: len(v) for k, v in by_type.items()},
                "entities": [e.to_dict() for e in entities],
                "analysis_time_seconds": analysis_time,
                "ready_for_correlation": True,
            },
        )

    # ---------- Private Helpers ----------

    def _from_ocr(self, result: ScanResult) -> List[VideoEntity]:
        entities = []
        extra = result.extra or {}
        for email in extra.get("emails", []):
            entities.append(VideoEntity("email", email, 0.85, "ocr"))
        for phone in extra.get("phones", []):
            entities.append(VideoEntity("phone", phone, 0.80, "ocr"))
        for url in extra.get("urls", []):
            entities.append(VideoEntity("url", url, 0.80, "ocr"))
            # Ekstrak domain dari URL
            domain = self._extract_domain(url)
            if domain:
                entities.append(VideoEntity("domain", domain, 0.75, "ocr"))
        for username in extra.get("usernames", []):
            entities.append(VideoEntity("username", username, 0.80, "ocr"))
        return entities

    def _from_audio(self, result: ScanResult) -> List[VideoEntity]:
        entities = []
        extra = result.extra or {}
        ent = extra.get("entities", {})
        for email in ent.get("emails", []):
            entities.append(VideoEntity("email", email, 0.70, "audio_transcript"))
        for phone in ent.get("phones", []):
            entities.append(VideoEntity("phone", phone, 0.65, "audio_transcript"))
        for url in ent.get("urls", []):
            entities.append(VideoEntity("url", url, 0.65, "audio_transcript"))
        return entities

    def _from_metadata(self, result: ScanResult) -> List[VideoEntity]:
        entities = []
        extra = result.extra or {}
        gps = extra.get("gps", {})
        if gps and gps.get("raw"):
            # Coba parse koordinat
            import re
            numbers = re.findall(r"[-+]?\d+\.\d+", str(gps["raw"]))
            if len(numbers) >= 2:
                entities.append(VideoEntity(
                    "location",
                    f"{numbers[0]},{numbers[1]}",
                    0.90,
                    "metadata_gps",
                ))
        return entities

    def _from_geolocation(self, result: ScanResult) -> List[VideoEntity]:
        entities = []
        cands = result.extra.get("candidates", []) if result.extra else []
        for c in cands:
            country = c.get("country", "")
            if country and country != "Unknown":
                entities.append(VideoEntity(
                    "location",
                    country,
                    c.get("country_confidence", 0.5),
                    "geolocation_inference",
                ))
        return entities

    def _from_language(self, result: ScanResult) -> List[VideoEntity]:
        entities = []
        extra = result.extra or {}
        lang = extra.get("combined_language")
        if lang:
            entities.append(VideoEntity(
                "language",
                lang,
                extra.get("combined_confidence", 0.5),
                "language_detection",
            ))
        return entities

    @staticmethod
    def _extract_domain(url: str) -> Optional[str]:
        import re
        match = re.search(r"https?://([^/:]+)", url)
        return match.group(1) if match else None