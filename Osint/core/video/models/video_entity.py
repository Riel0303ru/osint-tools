# core/video/models/video_entity.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class VideoEntity:
    """Entitas yang diekstrak dari video (orang, organisasi, lokasi, dll.)."""

    entity_type: str  # person, organization, location, email, phone, domain, etc.
    value: str
    confidence: float = 1.0
    source: str = ""  # OCR, audio, metadata, etc.
    timestamp: Optional[float] = None  # detik dalam video
    frame_index: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
            "frame_index": self.frame_index,
            "extra": self.extra,
        }