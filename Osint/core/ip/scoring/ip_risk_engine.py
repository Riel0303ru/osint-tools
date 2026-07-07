# core/ip/scoring/ip_risk_engine.py
from __future__ import annotations

from typing import Dict, List
from core.base.scan_result import ScanResult


class IPRiskEngine:
    """Weighted risk scoring untuk IP."""

    WEIGHTS = {
        "infrastructure_risk": 0.25,
        "exposure_risk": 0.30,
        "threat_reputation": 0.20,
        "service_risk": 0.15,
        "cloud_misconfiguration": 0.10,
    }

    @classmethod
    def calculate(cls, ip: str, results: List[ScanResult]) -> Dict:
        scores = {
            "infrastructure_risk": cls._infrastructure_risk(results),
            "exposure_risk": cls._exposure_risk(results),
            "threat_reputation": cls._threat_reputation(results),
            "service_risk": cls._service_risk(results),
            "cloud_misconfiguration": cls._cloud_misconfiguration(results),
        }
        total = sum(scores[cat] * cls.WEIGHTS[cat] for cat in scores)

        threat_level = (
            "CRITICAL" if total >= 70
            else "HIGH" if total >= 50
            else "MEDIUM" if total >= 30
            else "LOW" if total >= 15
            else "MINIMAL"
        )

        return {
            "ip": ip,
            "category_scores": scores,
            "total_risk_score": round(total, 1),
            "threat_level": threat_level,
            "confidence": cls._confidence(results),
        }

    @classmethod
    def _infrastructure_risk(cls, results: List[ScanResult]) -> float:
        score = 0.0
        for r in results:
            if r.platform == "Abstract IP Intelligence" and r.status == "FOUND":
                extra = r.extra or {}
                if extra.get("is_vpn"):
                    score += 20
                if extra.get("is_proxy"):
                    score += 20
                if extra.get("is_tor"):
                    score += 30
                if extra.get("is_hosting"):
                    score += 10
                if extra.get("is_abuse"):
                    score += 15
        return min(score, 100.0)

    @classmethod
    def _exposure_risk(cls, results: List[ScanResult]) -> float:
        score = 0.0
        for r in results:
            if r.platform == "Service Analysis" and r.status == "FOUND":
                extra = r.extra or {}
                open_ports = extra.get("open_ports", 0)
                score += min(open_ports * 3, 30)
                findings = extra.get("findings", [])
                for f in findings:
                    service = f.get("service", "")
                    if service in ["Elasticsearch", "MongoDB", "Redis", "Kubernetes API"]:
                        score += 15
                    elif service in ["RDP", "SSH", "Telnet"]:
                        score += 10
        return min(score, 100.0)

    @classmethod
    def _threat_reputation(cls, results: List[ScanResult]) -> float:
        for r in results:
            if r.platform == "Threat Reputation" and r.status == "FOUND":
                return 50.0
        return 0.0

    @classmethod
    def _service_risk(cls, results: List[ScanResult]) -> float:
        score = 0.0
        for r in results:
            if r.platform == "Service Analysis":
                extra = r.extra or {}
                findings = extra.get("findings", [])
                for f in findings:
                    if f.get("status_code") == 200:
                        score += 5
        return min(score, 100.0)

    @classmethod
    def _cloud_misconfiguration(cls, results: List[ScanResult]) -> float:
        score = 0.0
        for r in results:
            if r.platform == "Cloud Provider Detection" and r.status == "FOUND":
                extra = r.extra or {}
                if extra.get("cloud_provider") in ["AWS", "Azure", "Google Cloud"]:
                    # Cek apakah ada exposure bersamaan
                    exposure = next((x for x in results if x.platform == "Service Analysis"), None)
                    if exposure and exposure.extra.get("open_ports", 0) > 5:
                        score += 20
        return min(score, 100.0)

    @classmethod
    def _confidence(cls, results: List[ScanResult]) -> float:
        found = sum(1 for r in results if r.status == "FOUND")
        total = len(results)
        return min(found / max(total, 1), 1.0)