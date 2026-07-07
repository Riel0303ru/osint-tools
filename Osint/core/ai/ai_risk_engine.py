# core/ai/ai_risk_engine.py
from typing import List, Dict, Union
from core.base.scan_result import ScanResult


class AIRiskEngine:
    def calculate(self, results: List[Union[ScanResult, Dict]]) -> float:
        score = 0
        for r in results:
            if isinstance(r, ScanResult):
                status = r.status
                extra = r.extra or {}
                platform = r.platform
            else:
                status = r.get("status", "")
                extra = r.get("extra", {})
                platform = r.get("platform", "")

            if status == "FOUND":
                score += 2
            if "breach" in str(extra).lower() or "breach" in platform.lower():
                score += 10
            if "gps" in str(extra).lower() or "coordinates" in str(extra).lower():
                score += 15
            if "suspicious" in str(extra).lower():
                score += 8
            if status == "ERROR":
                score += 0.5
        return min(score, 100.0)