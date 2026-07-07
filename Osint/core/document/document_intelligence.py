# core/document/document_intelligence.py
from __future__ import annotations

from typing import List, Dict
from core.base.scan_result import ScanResult


class DocumentIntelligence:
    """Scoring untuk Document Intelligence."""

    @classmethod
    def score(cls, file_path: str, results: List[ScanResult]) -> float:
        score = 0.0

        for r in results:
            if r.platform == "Metadata Analysis" and r.status == "FOUND":
                if r.extra.get("has_author"):
                    score += 15
                if r.extra.get("has_company"):
                    score += 10
                if r.extra.get("suspicious_metadata"):
                    score += 10

            if r.platform == "Sensitive Data Detection" and r.status == "FOUND":
                sensitive = r.extra or {}
                if sensitive.get("emails"):
                    score += min(len(sensitive["emails"]) * 5, 20)
                if sensitive.get("phones"):
                    score += min(len(sensitive["phones"]) * 5, 15)
                if sensitive.get("api_keys"):
                    score += min(len(sensitive["api_keys"]) * 10, 25)
                if sensitive.get("tokens"):
                    score += min(len(sensitive["tokens"]) * 10, 25)
                if sensitive.get("urls"):
                    score += min(len(sensitive["urls"]) * 3, 10)

            if r.platform == "Security Analysis" and r.status == "FOUND":
                findings = r.extra.get("security_findings", [])
                score += min(len(findings) * 5, 15)

        return min(score, 100.0)