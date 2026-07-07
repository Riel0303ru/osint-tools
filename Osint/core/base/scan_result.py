# core/base/scan_result.py
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any

@dataclass
class ScanResult:
    platform: str
    username: str
    status: str                  # "FOUND", "NOT_FOUND", "ERROR"
    status_code: int
    url: str
    confidence: float = 1.0
    intelligence_score: float = 0.0   # dari enrichment module
    extra: Dict[str, Any] = field(default_factory=dict)  # metadata tambahan

    def to_dict(self) -> dict:
        """Ubah ke dictionary (digunakan oleh formatter lama jika perlu)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ScanResult":
        """Buat objek dari dictionary (untuk konversi dari scanner lama)."""
        return cls(**data)