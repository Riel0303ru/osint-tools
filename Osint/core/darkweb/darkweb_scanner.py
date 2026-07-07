# core/darkweb/darkweb_scanner.py
from __future__ import annotations

from typing import List, Dict
from core.darkweb.providers.dehashed_provider import DehashedProvider
from core.darkweb.leak_parser import LeakParser
from core.darkweb.breach_engine import BreachEngine
from core.darkweb.exposure_engine import ExposureEngine
from core.darkweb.risk_engine import RiskEngine
from core.darkweb.identity_correlator import IdentityCorrelator
from core.darkweb.timeline_engine import TimelineEngine
from core.darkweb.confidence_engine import ConfidenceEngine
from core.base.scan_result import ScanResult
from utils.logger import Logger


class DarkwebScanner:
    """Scanner utama Dark Web Intelligence."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.provider = DehashedProvider(base_dir)

    async def scan(self, target: str) -> List[ScanResult]:
        self.logger.info(f"Scanning dark web intelligence -> {target}")
        results = []

        # 1. Search DeHashed
        raw = await self.provider.search(target, de_dupe=True)
        entries = raw.get("entries", [])

        if not entries:
            return [
                ScanResult(
                    platform="DeHashed Search",
                    username=target,
                    status="NOT_FOUND",
                    status_code=404,
                    url="",
                    confidence=0.9,
                    extra={"message": "No results found in DeHashed", "error": raw.get("error")},
                )
            ]

        # 2. Parse entries
        parsed = LeakParser.parse(entries)

        # 3. Breach Analysis
        breach_analysis = BreachEngine.analyze(entries)
        results.append(ScanResult(
            platform="Breach Analysis",
            username=target,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.95,
            extra=breach_analysis,
        ))

        # 4. Exposure Analysis
        exposure = ExposureEngine.analyze(parsed)
        results.append(ScanResult(
            platform="Exposure Analysis",
            username=target,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.95,
            extra=exposure,
        ))

        # 5. Risk Assessment
        risk = RiskEngine.calculate(breach_analysis, exposure)
        results.append(ScanResult(
            platform="Risk Assessment",
            username=target,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.9,
            extra=risk,
        ))

        # 6. Identity Correlation
        correlation = IdentityCorrelator.correlate(parsed)
        results.append(ScanResult(
            platform="Identity Correlation",
            username=target,
            status="FOUND" if correlation["total_correlations"] > 0 else "NOT_FOUND",
            status_code=200 if correlation["total_correlations"] > 0 else 404,
            url="",
            confidence=0.85,
            extra=correlation,
        ))

        # 7. Timeline
        timeline = TimelineEngine.build(entries)
        results.append(ScanResult(
            platform="Breach Timeline",
            username=target,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.9,
            extra=timeline,
        ))

        # 8. Confidence
        confidence = ConfidenceEngine.calculate(breach_analysis, exposure)
        results.append(ScanResult(
            platform="Confidence Assessment",
            username=target,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.9,
            extra=confidence,
        ))

        self.logger.success(f"Dark web scan completed -> {target}")
        return results