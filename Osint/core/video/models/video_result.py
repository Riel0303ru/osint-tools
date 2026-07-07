from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .video_entity import VideoEntity  # tambahkan ini
# ...


@dataclass
class VideoResult:
    """Hasil analisis video lengkap."""

    file_path: str
    file_name: str
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    resolution: str = ""
    codec: str = ""
    frame_rate: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)
    frames: List[Dict[str, Any]] = field(default_factory=list)
    ocr_findings: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)
    objects: List[Dict[str, Any]] = field(default_factory=list)
    landmarks: List[Dict[str, Any]] = field(default_factory=list)
    audio_transcript: str = ""
    audio_language: str = ""
    audio_events: List[Dict[str, Any]] = field(default_factory=list)
    location_candidates: List[Dict[str, Any]] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[VideoEntity] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    ai_summary: str = ""
    scan_time: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "resolution": self.resolution,
            "codec": self.codec,
            "frame_rate": self.frame_rate,
            "metadata": self.metadata,
            "frames_count": len(self.frames),
            "ocr_findings": self.ocr_findings,
            "faces": self.faces,
            "objects": self.objects,
            "landmarks": self.landmarks,
            "audio_transcript": self.audio_transcript,
            "audio_language": self.audio_language,
            "audio_events": self.audio_events,
            "location_candidates": self.location_candidates,
            "timeline": self.timeline,
            "entities": [e.to_dict() for e in self.entities],
            "risk_assessment": self.risk_assessment,
            "ai_summary": self.ai_summary,
            "scan_time": self.scan_time,
        }