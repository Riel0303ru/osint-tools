# core/darkweb/darkweb_intelligence.py
from __future__ import annotations

from typing import List
from core.base.scan_result import ScanResult


class DarkwebIntelligence:
    """Scoring untuk Dark Web Intelligence."""

    @classmethod
    def score(cls, target: str, results: List[ScanResult]) -> float:
        score = 0.0

        for r in results:
            if r.platform == "Breach Analysis" and r.status == "FOUND":
                breaches = r.extra.get("total_breaches", 0)
                score += min(breaches * 10, 40)
                if r.extra.get("plaintext_password_exposure"):
                    score += 30

            if r.platform == "Exposure Analysis" and r.status == "FOUND":
                exposure = r.extra
                if exposure.get("email_exposure", 0) > 0:
                    score += 15
                if exposure.get("password_exposure", 0) > 0:
                    score += 20
                if exposure.get("phone_exposure", 0) > 0:
                    score += 10

            if r.platform == "Risk Assessment" and r.status == "FOUND":
                score += r.extra.get("risk_score", 0) * 0.1

        return min(score, 100.0)