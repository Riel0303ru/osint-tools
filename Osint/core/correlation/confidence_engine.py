# core/correlation/confidence_engine.py
from __future__ import annotations

from typing import List, Dict


class ConfidenceEngine:
    """Menghitung confidence score untuk setiap hubungan."""

    FACTORS = {
        "exact_username": 0.4,
        "shared_email": 0.5,
        "shared_phone": 0.5,
        "shared_domain": 0.3,
        "shared_social_link": 0.35,
        "shared_avatar": 0.25,
        "shared_location": 0.15,
        "similar_bio": 0.2,
        "fuzzy_username": 0.25,
    }

    @classmethod
    def calculate(cls, matches: List[str], num_entities: int = 0) -> Dict:
        """
        Hitung confidence berdasarkan jumlah dan tipe kecocokan.
        Mengembalikan skor, level, dan faktor yang digunakan.
        """
        score = 0.0
        used_factors = []

        for match in matches:
            category = match.split(":")[0].strip()
            for factor, weight in cls.FACTORS.items():
                if factor in category or category in factor:
                    score += weight
                    used_factors.append(factor)
                    break

        # Batasi maksimum
        score = min(score, 1.0)

        # Tentukan level
        if score >= 0.8:
            level = "VERY_HIGH"
        elif score >= 0.6:
            level = "HIGH"
        elif score >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "confidence_score": round(score, 3),
            "confidence_level": level,
            "factors": list(set(used_factors)),
        }