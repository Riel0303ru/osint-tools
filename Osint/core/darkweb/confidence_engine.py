# core/darkweb/confidence_engine.py
from __future__ import annotations

from typing import Dict


class ConfidenceEngine:
    """Menghitung confidence score berdasarkan kualitas data."""

    @staticmethod
    def calculate(breach_analysis: Dict, exposure: Dict) -> Dict:
        score = 0.0
        factors = []

        if breach_analysis.get("total_breaches", 0) > 0:
            score += 0.4
            factors.append("breach_data_available")

        if breach_analysis.get("total_entries", 0) > 10:
            score += 0.2
            factors.append("significant_data_volume")

        if breach_analysis.get("plaintext_password_exposure"):
            score += 0.2
            factors.append("plaintext_password")

        if exposure.get("email_exposure", 0) > 0:
            score += 0.1
            factors.append("email_verified")

        if exposure.get("phone_exposure", 0) > 0:
            score += 0.1
            factors.append("phone_verified")

        return {
            "confidence_score": min(score, 1.0),
            "confidence_level": (
                "VERY_HIGH" if score >= 0.8
                else "HIGH" if score >= 0.6
                else "MEDIUM" if score >= 0.4
                else "LOW"
            ),
            "factors": factors,
        }