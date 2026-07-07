from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
# ...

@dataclass
class LocationCandidate:
    """Kandidat lokasi yang diestimasi dari video."""

    country: str = ""
    country_confidence: float = 0.0
    region: str = ""
    region_confidence: float = 0.0
    city: str = ""
    city_confidence: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gps_source: str = ""  # metadata, visual, audio
    evidence: List[str] = field(default_factory=list)
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "country_confidence": self.country_confidence,
            "region": self.region,
            "region_confidence": self.region_confidence,
            "city": self.city,
            "city_confidence": self.city_confidence,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "gps_source": self.gps_source,
            "evidence": self.evidence,
            "reasoning": self.reasoning,
        }