from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
# ...

@dataclass
class TimelineEvent:
    """Satu event dalam timeline video."""

    timestamp: float  # detik dalam video
    event_type: str  # face, object, ocr, audio, scene, location
    description: str
    confidence: float = 1.0
    source: str = ""
    frame_index: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "description": self.description,
            "confidence": self.confidence,
            "source": self.source,
            "frame_index": self.frame_index,
            "extra": self.extra,
        }