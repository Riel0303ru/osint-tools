# core/darkweb/risk_engine.py
from __future__ import annotations

from typing import Dict


class RiskEngine:
    """Menghitung risk score berdasarkan hasil breach."""

    @staticmethod
    def calculate(breach_analysis: Dict, exposure: Dict) -> Dict:
        score = 0

        # Faktor breach
        total_breaches = breach_analysis.get("total_breaches", 0)
        score += min(total_breaches * 10, 40)

        # Plaintext password exposure
        if breach_analysis.get("plaintext_password_exposure"):
            score += 30

        # Email exposure
        if exposure.get("email_exposure", 0) > 0:
            score += min(exposure["email_exposure"] * 2, 15)

        # Phone exposure
        if exposure.get("phone_exposure", 0) > 0:
            score += min(exposure["phone_exposure"] * 5, 10)

        # Name exposure
        if exposure.get("name_exposure", 0) > 0:
            score += 5

        # Risk level
        if score >= 70:
            level = "CRITICAL"
        elif score >= 50:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        elif score >= 10:
            level = "LOW"
        else:
            level = "MINIMAL"

        return {
            "risk_score": min(score, 100),
            "risk_level": level,
            "factors": {
                "breaches_count": total_breaches,
                "plaintext_password": breach_analysis.get("plaintext_password_exposure", False),
                "email_exposure": exposure.get("email_exposure", 0),
                "phone_exposure": exposure.get("phone_exposure", 0),
                "name_exposure": exposure.get("name_exposure", 0),
            },
        }