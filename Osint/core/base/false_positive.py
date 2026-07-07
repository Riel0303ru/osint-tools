# core/base/false_positive.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from core.base.scan_result import ScanResult


@dataclass
class ValidationIssue:

    severity: str
    category: str
    message: str
    score_penalty: float

    def to_dict(self) -> Dict[str, Any]:

        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "score_penalty": self.score_penalty
        }


@dataclass
class ValidationReport:

    is_false_positive: bool

    validation_score: float

    issues: List[ValidationIssue] = field(
        default_factory=list
    )

    evidence_count: int = 0

    contradiction_count: int = 0

    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:

        return {

            "is_false_positive":
                self.is_false_positive,

            "validation_score":
                self.validation_score,

            "evidence_count":
                self.evidence_count,

            "contradiction_count":
                self.contradiction_count,

            "summary":
                self.summary,

            "issues": [
                i.to_dict()
                for i in self.issues
            ]
        }


class FalsePositiveDetector:

    def __init__(self):

        self.always_200_platforms = {

            "Facebook",
            "LinkedIn",
            "Pinterest",
            "Tumblr"
        }

        self.body_validation_platforms = {

            "Instagram",
            "TikTok",
            "Reddit",
            "X"
        }

        self.low_reputation_sources = {

            "Telegram",
            "WhatsApp"
        }

    def validate(
        self,
        result: ScanResult
    ) -> ValidationReport:

        issues: List[
            ValidationIssue
        ] = []

        score = 1.0

        score -= self._validate_http(
            result,
            issues
        )

        score -= self._validate_redirect(
            result,
            issues
        )

        score -= self._validate_content(
            result,
            issues
        )

        score -= self._validate_metadata(
            result,
            issues
        )

        score -= self._validate_platform(
            result,
            issues
        )

        score = max(
            0.0,
            min(
                score,
                1.0
            )
        )

        is_fp = score < 0.50

        summary = self._build_summary(
            score,
            issues
        )

        return ValidationReport(

            is_false_positive=is_fp,

            validation_score=round(
                score,
                4
            ),

            issues=issues,

            evidence_count=self._count_evidence(
                result
            ),

            contradiction_count=0,

            summary=summary
        )

    def validate_many(
        self,
        results: List[ScanResult]
    ) -> Dict[str, ValidationReport]:

        reports = {}

        for result in results:

            reports[
                result.result_id
            ] = self.validate(
                result
            )

        return reports

    def apply(
        self,
        result: ScanResult
    ) -> ScanResult:

        report = self.validate(
            result
        )

        result.validation_score = (
            report.validation_score
        )

        result.false_positive = (
            report.is_false_positive
        )

        result.validation_report = (
            report.to_dict()
        )

        if report.is_false_positive:

            result.confidence *= 0.5

        return result

    def cross_validate(
        self,
        results: List[ScanResult]
    ) -> Dict[str, Any]:

        found = 0

        not_found = 0

        error = 0

        for item in results:

            if item.status == "FOUND":

                found += 1

            elif item.status == "NOT_FOUND":

                not_found += 1

            else:

                error += 1

        contradictions = min(
            found,
            not_found
        )

        return {

            "total_results":
                len(results),

            "found":
                found,

            "not_found":
                not_found,

            "error":
                error,

            "contradictions":
                contradictions
        }

    def _validate_http(
        self,
        result: ScanResult,
        issues: List[
            ValidationIssue
        ]
    ) -> float:

        penalty = 0.0

        if (
            result.status == "FOUND"
            and result.status_code >= 400
        ):

            penalty += 0.30

            issues.append(

                ValidationIssue(

                    severity="HIGH",

                    category="HTTP",

                    message=(
                        "FOUND status "
                        "with invalid "
                        "HTTP code"
                    ),

                    score_penalty=0.30
                )
            )

        return penalty

    def _validate_redirect(
        self,
        result: ScanResult,
        issues: List[
            ValidationIssue
        ]
    ) -> float:

        extra = result.extra or {}

        if not extra.get(
            "redirected_to_login",
            False
        ):
            return 0.0

        issues.append(

            ValidationIssue(

                severity="MEDIUM",

                category="REDIRECT",

                message=(
                    "Redirected to "
                    "login page"
                ),

                score_penalty=0.20
            )
        )

        return 0.20

    def _validate_content(
        self,
        result: ScanResult,
        issues: List[
            ValidationIssue
        ]
    ) -> float:

        penalty = 0.0

        extra = result.extra or {}

        if (
            result.platform
            in self.body_validation_platforms
        ):

            if not extra.get(
                "body_contains_target",
                False
            ):

                penalty += 0.20

                issues.append(

                    ValidationIssue(

                        severity="HIGH",

                        category="CONTENT",

                        message=(
                            "Target not "
                            "present in body"
                        ),

                        score_penalty=0.20
                    )
                )

        return penalty

    def _validate_metadata(
        self,
        result: ScanResult,
        issues: List[
            ValidationIssue
        ]
    ) -> float:

        penalty = 0.0

        extra = result.extra or {}

        response_time = extra.get(
            "response_time",
            None
        )

        if (
            response_time is not None
            and response_time < 0.05
        ):

            penalty += 0.10

            issues.append(

                ValidationIssue(

                    severity="LOW",

                    category="METADATA",

                    message=(
                        "Suspiciously "
                        "fast response"
                    ),

                    score_penalty=0.10
                )
            )

        return penalty

    def _validate_platform(
        self,
        result: ScanResult,
        issues: List[
            ValidationIssue
        ]
    ) -> float:

        penalty = 0.0

        extra = result.extra or {}

        if (
            result.platform
            in self.always_200_platforms
        ):

            if not extra.get(
                "body_checked",
                False
            ):

                penalty += 0.25

                issues.append(

                    ValidationIssue(

                        severity="HIGH",

                        category="PLATFORM",

                        message=(
                            "Always-200 "
                            "platform without "
                            "body verification"
                        ),

                        score_penalty=0.25
                    )
                )

        return penalty

    def _count_evidence(
        self,
        result: ScanResult
    ) -> int:

        count = 0

        if result.extra:

            for value in result.extra.values():

                if value:

                    count += 1

        return count

    def _build_summary(
        self,
        score: float,
        issues: List[
            ValidationIssue
        ]
    ) -> str:

        if score >= 0.90:

            return (
                "High confidence "
                "validation"
            )

        if score >= 0.75:

            return (
                "Good validation "
                "quality"
            )

        if score >= 0.50:

            return (
                "Validation requires "
                "manual review"
            )

        return (
            "Potential false "
            "positive detected"
        )