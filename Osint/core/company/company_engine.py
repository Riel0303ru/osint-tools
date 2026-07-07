# core/company/company_engine.py
from __future__ import annotations

import asyncio
from typing import Dict, List
from datetime import datetime, timezone

from core.company.company_scanner import CompanyScanner
from core.company.providers.whois_provider import WhoisProvider
from core.company.providers.dns_provider import DNSProvider
from core.company.providers.subdomain_provider import SubdomainProvider
from core.company.providers.ssl_provider import SSLProvider
from core.company.providers.tech_provider import TechProvider
from core.company.providers.infrastructure_provider import InfrastructureProvider
from core.company.analyzers.exposure_analyzer import ExposureAnalyzer
from core.company.analyzers.security_analyzer import SecurityAnalyzer
from core.company.fingerprints.saas_detector import SaaSDetector
from core.company.correlators.company_correlator import CompanyCorrelator
from core.company.scoring.risk_engine import RiskEngine
from core.base.scan_result import ScanResult
from core.base.storage import Storage
from utils.logger import Logger


class CompanyEngine:
    """
    Orchestrator utama Company Intelligence.
    Menggabungkan semua provider, analyzer, correlator, dan risk engine.
    """

    def __init__(self, storage: Storage, base_dir: str = "Osint"):
        self.storage = storage
        self.logger = Logger(base_dir=base_dir)

        # API
        self.company_scanner = CompanyScanner(base_dir=base_dir)

        # Providers (passive)
        self.whois_provider = WhoisProvider(base_dir=base_dir)
        self.dns_provider = DNSProvider(base_dir=base_dir)
        self.subdomain_provider = SubdomainProvider(base_dir=base_dir)
        self.tech_provider = TechProvider(base_dir=base_dir)

        # Analyzers
        self.exposure_analyzer = ExposureAnalyzer(base_dir=base_dir)
        self.security_analyzer = SecurityAnalyzer(base_dir=base_dir)

        # Correlator & Risk
        self.correlator = CompanyCorrelator()
        self.risk_engine = RiskEngine()

    async def execute_full(self, domain: str) -> Dict:
        """
        Jalankan investigasi lengkap terhadap domain perusahaan.
        Mengembalikan dictionary hasil gabungan.
        """
        self.logger.divider()
        self.logger.info(f"Starting Company Intelligence Engine -> {domain}")

        start_time = datetime.now(timezone.utc)

        # 1. Jalankan semua provider secara paralel
        self.logger.info("Running all intelligence providers...")

        company_task = self.company_scanner.scan_company(domain)
        whois_task = self.whois_provider.lookup(domain)
        dns_task = self.dns_provider.analyze(domain)
        subdomain_task = self.subdomain_provider.enumerate(domain)
        tech_task = self.tech_provider.fingerprint(domain)

        company_results, whois_data, dns_data, subdomain_data, tech_data = await asyncio.gather(
            company_task, whois_task, dns_task, subdomain_task, tech_task
        )

        # 2. Jalankan analyzers
        self.logger.info("Running security analyzers...")
        exposure_data = await self.exposure_analyzer.scan(domain)

        # Ambil data company dari API (jika berhasil)
        company_api_data = {}
        for r in company_results:
            if r.platform == "Company Enrichment" and r.status == "FOUND":
                company_api_data = r.extra or {}
                break

        # 3. Deteksi SaaS dari DNS
        saas_from_txt = SaaSDetector.detect_from_txt(dns_data.get("records", {}).get("TXT", []))
        saas_from_mx = SaaSDetector.detect_from_mx(dns_data.get("records", {}).get("MX", []))
        spf_record = dns_data.get("email_security", {}).get("spf_record", "")
        saas_from_spf = SaaSDetector.detect_from_spf(spf_record)

        # Gabungkan semua SaaS detection
        all_saas = {}
        for source in [saas_from_txt, saas_from_mx, saas_from_spf]:
            for k, v in source.items():
                if k not in all_saas:
                    all_saas[k] = v

        # 4. Correlate
        self.logger.info("Correlating findings...")
        correlation = self.correlator.correlate(
            domain=domain,
            company_data=company_api_data,
            whois_data=whois_data,
            dns_data=dns_data,
            ssl_data={},  # SSL provider bisa ditambahkan nanti
            tech_data=tech_data,
            subdomain_data=subdomain_data,
        )

        # 5. Risk Scoring
        self.logger.info("Calculating risk scores...")
        risk_assessment = self.risk_engine.calculate(
            domain=domain,
            company_data=company_api_data,
            whois_data=whois_data,
            dns_data=dns_data,
            ssl_data={},
            tech_data=tech_data,
            subdomain_data=subdomain_data,
            security_data={"headers_found": [], "missing": []},
        )

        # 6. Gabungkan semua
        end_time = datetime.now(timezone.utc)
        duration_seconds = (end_time - start_time).total_seconds()

        full_report = {
            "target": domain,
            "scan_time": start_time.isoformat(),
            "duration_seconds": duration_seconds,
            "company_api": company_api_data,
            "whois": whois_data,
            "dns": dns_data,
            "subdomains": subdomain_data,
            "technologies": tech_data,
            "saas_detected": all_saas,
            "exposure": exposure_data,
            "correlation": correlation,
            "risk_assessment": risk_assessment,
        }

        # 7. Simpan ke storage (sebagai ScanResult)
        self._save_to_storage(domain, full_report)

        # 8. Konversi ke list ScanResult untuk kompatibilitas pipeline
        scan_results = self._to_scan_results(domain, full_report)

        self.logger.success(f"Company Engine completed -> {domain} in {duration_seconds:.1f}s")
        self.logger.divider()

        return scan_results, full_report

    def _save_to_storage(self, domain: str, report: Dict) -> None:
        """Simpan ringkasan ke database history."""
        scan_results = self._to_scan_results(domain, report)
        timestamp = self.storage.save_scan(domain, scan_results)
        self.logger.info(f"Company report saved to history with timestamp {timestamp}")

    def _to_scan_results(self, domain: str, report: Dict) -> List[ScanResult]:
        """Konversi full report ke list ScanResult untuk kompatibilitas."""
        results = []

        # Company Enrichment API
        if report.get("company_api"):
            results.append(ScanResult(
                platform="Company Enrichment",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.95,
                extra=report["company_api"],
            ))

        # WHOIS
        whois = report.get("whois", {})
        if whois.get("status") == "FOUND":
            results.append(ScanResult(
                platform="WHOIS",
                username=domain,
                status="FOUND",
                status_code=200,
                url=f"https://www.whois.com/whois/{domain}",
                confidence=0.9,
                extra=whois,
            ))

        # DNS
        dns = report.get("dns", {})
        if dns.get("records"):
            results.append(ScanResult(
                platform="DNS Intelligence",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.95,
                extra=dns,
            ))

        # Subdomains
        sub = report.get("subdomains", {})
        if sub.get("subdomains"):
            results.append(ScanResult(
                platform="Subdomain Intelligence",
                username=domain,
                status="FOUND" if sub.get("count", 0) > 0 else "NOT_FOUND",
                status_code=200,
                url="",
                confidence=0.9,
                extra=sub,
            ))

        # Technologies
        tech = report.get("technologies", {})
        if tech.get("technologies"):
            results.append(ScanResult(
                platform="Technology Stack",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.85,
                extra=tech,
            ))

        # SaaS Detected
        saas = report.get("saas_detected", {})
        if saas:
            results.append(ScanResult(
                platform="SaaS Detection",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.9,
                extra={"saas_detected": saas},
            ))

        # Exposure
        exp = report.get("exposure", {})
        if exp.get("findings"):
            results.append(ScanResult(
                platform="Exposure Analysis",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.95,
                extra=exp,
            ))

        # Risk Assessment
        risk = report.get("risk_assessment", {})
        if risk:
            results.append(ScanResult(
                platform="Risk Assessment",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.9,
                extra=risk,
            ))

        # Correlation
        corr = report.get("correlation", {})
        if corr:
            results.append(ScanResult(
                platform="Correlation Analysis",
                username=domain,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.85,
                extra=corr,
            ))

        return results