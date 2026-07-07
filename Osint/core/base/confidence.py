# core/base/confidence.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from core.base.scan_result import ScanResult


@dataclass
class ConfidenceEvidence:

    source: str

    score: float

    description: str

    weight: float = 1.0


@dataclass
class ConfidenceFactors:

    source_reputation: float = 0.0

    status_validation: float = 0.0

    content_validation: float = 0.0

    metadata_validation: float = 0.0

    cross_validation: float = 0.0

    historical_consistency: float = 0.0

    correlation_strength: float = 0.0

    ai_verification: float = 0.0

    timeline_consistency: float = 0.0

    geolocation_consistency: float = 0.0

    risk_alignment: float = 0.0

    evidence_count: int = 0

    conflict_count: int = 0


@dataclass
class ConfidenceReport:

    final_score: float

    grade: str

    explanation: str

    evidence_count: int

    conflict_count: int

    evidence: List[ConfidenceEvidence] = field(default_factory=list)

    factors: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "final_score": self.final_score,
            "grade": self.grade,
            "explanation": self.explanation,
            "evidence_count": self.evidence_count,
            "conflict_count": self.conflict_count,
            "evidence": [
                {
                    "source": e.source,
                    "score": e.score,
                    "description": e.description,
                    "weight": e.weight
                }
                for e in self.evidence
            ],
            "factors": self.factors
        }


class ConfidenceEngine:

    def __init__(self):

        self.source_reputation = {

            "HaveIBeenPwned": 0.95,
            "VirusTotal": 0.95,
            "Shodan": 0.93,
            "Hunter": 0.92,
            "WHOIS": 0.90,
            "crt.sh": 0.88,
            "Gravatar": 0.85,
            "Telegram": 0.65,
            "WhatsApp": 0.70,

            "EXIF": 0.95,
            "OCR": 0.90,
            "FaceDetector": 0.85,
            "YOLO": 0.85,
            "ReverseImageSearch": 0.88,

            "FFmpeg": 0.95,
            "MetadataExtractor": 0.90,

            "AI": 0.80
        }

    def calculate(
        self,
        result: ScanResult,
        factors: Optional[ConfidenceFactors] = None,
        evidence: Optional[List[ConfidenceEvidence]] = None
    ) -> ConfidenceReport:

        evidence = evidence or []

        base_confidence = result.confidence

        source_weight = self.source_reputation.get(
            result.platform,
            0.75
        )

        score = base_confidence * source_weight

        if factors:

            score += factors.status_validation * 0.08

            score += factors.content_validation * 0.10

            score += factors.metadata_validation * 0.08

            score += factors.cross_validation * 0.12

            score += factors.historical_consistency * 0.08

            score += factors.correlation_strength * 0.12

            score += factors.ai_verification * 0.08

            score += factors.timeline_consistency * 0.06

            score += factors.geolocation_consistency * 0.08

            score += factors.risk_alignment * 0.05

            score += min(
                factors.evidence_count * 0.01,
                0.10
            )

            score -= min(
                factors.conflict_count * 0.03,
                0.20
            )

        score = max(
            0.0,
            min(
                score,
                1.0
            )
        )

        grade = self._grade(score)

        explanation = self._build_explanation(
            score,
            grade,
            evidence,
            factors
        )

        return ConfidenceReport(

            final_score=round(score, 4),

            grade=grade,

            explanation=explanation,

            evidence_count=(
                factors.evidence_count
                if factors else 0
            ),

            conflict_count=(
                factors.conflict_count
                if factors else 0
            ),

            evidence=evidence,

            factors=self._factor_dict(factors)
        )

    def _grade(
        self,
        score: float
    ) -> str:

        if score >= 0.95:
            return "A+"

        if score >= 0.90:
            return "A"

        if score >= 0.80:
            return "B"

        if score >= 0.70:
            return "C"

        if score >= 0.50:
            return "D"

        return "F"

    def _factor_dict(
        self,
        factors: Optional[ConfidenceFactors]
    ) -> Dict[str, float]:

        if not factors:
            return {}

        return {

            "source_reputation":
                factors.source_reputation,

            "status_validation":
                factors.status_validation,

            "content_validation":
                factors.content_validation,

            "metadata_validation":
                factors.metadata_validation,

            "cross_validation":
                factors.cross_validation,

            "historical_consistency":
                factors.historical_consistency,

            "correlation_strength":
                factors.correlation_strength,

            "ai_verification":
                factors.ai_verification,

            "timeline_consistency":
                factors.timeline_consistency,

            "geolocation_consistency":
                factors.geolocation_consistency,

            "risk_alignment":
                factors.risk_alignment
        }

    def _build_explanation(
        self,
        score: float,
        grade: str,
        evidence: List[ConfidenceEvidence],
        factors: Optional[ConfidenceFactors]
    ) -> str:

        lines = [

            f"Confidence Score: {round(score * 100, 2)}%",

            f"Intelligence Grade: {grade}"
        ]

        if factors:

            lines.append(
                f"Evidence Count: {factors.evidence_count}"
            )

            lines.append(
                f"Conflict Count: {factors.conflict_count}"
            )

        if evidence:

            lines.append(
                f"Supporting Evidence: {len(evidence)}"
            )

        return " | ".join(lines)

    def cross_validate(
        self,
        results: List[ScanResult]
    ) -> Dict[str, Any]:

        found = 0

        not_found = 0

        error = 0

        for result in results:

            if result.status == "FOUND":

                found += 1

            elif result.status == "NOT_FOUND":

                not_found += 1

            else:

                error += 1

        total = len(results)

        agreement = (
            found / total
            if total > 0
            else 0
        )

        return {

            "total_sources": total,

            "found": found,

            "not_found": not_found,

            "error": error,

            "agreement_score": round(
                agreement,
                4
            )
        }