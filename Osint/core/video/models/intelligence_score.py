# core/video/models/intelligence_score.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class IntelligenceScore:
    """Skor intelijen hasil analisis video."""

    total_score: float = 0.0
    metadata_score: float = 0.0
    ocr_score: float = 0.0
    face_score: float = 0.0
    object_score: float = 0.0
    landmark_score: float = 0.0
    location_score: float = 0.0
    audio_score: float = 0.0
    correlation_score: float = 0.0
    risk_level: str = "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "metadata_score": self.metadata_score,
            "ocr_score": self.ocr_score,
            "face_score": self.face_score,
            "object_score": self.object_score,
            "landmark_score": self.landmark_score,
            "location_score": self.location_score,
            "audio_score": self.audio_score,
            "correlation_score": self.correlation_score,
            "risk_level": self.risk_level,
        }