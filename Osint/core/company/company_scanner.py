# core/company/company_scanner.py
from __future__ import annotations

import asyncio 
import os
from pathlib import Path
from typing import List, Optional
import requests
from dotenv import load_dotenv

from core.base.scan_result import ScanResult
from utils.logger import Logger

ENV_PATH = Path(__file__).resolve().parents[2] / ".env.local"
load_dotenv(ENV_PATH)


class CompanyScanner:
    """Company Enrichment scanner menggunakan AbstractAPI."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key: Optional[str] = os.getenv("ABSTRACT_COMPANY_KEY")

        if not self.api_key:
            self.logger.warning(
                "ABSTRACT_COMPANY_KEY tidak ditemukan. "
                "Fitur Company Intelligence akan nonaktif. "
                "Pastikan .env.local berisi ABSTRACT_COMPANY_KEY=..."
            )

    async def scan_company(self, domain: str) -> List[ScanResult]:
        self.logger.info(f"Scanning company -> {domain}")

        domain = self._clean_domain(domain)
        if not domain:
            return [
                ScanResult(
                    platform="Company Validation",
                    username=domain,
                    status="ERROR",
                    status_code=0,
                    url="",
                    confidence=0.0,
                    extra={"error": "Invalid domain format"},
                )
            ]

        results = []
        try:
            # Gunakan requests (sinkron) di dalam async method – aman karena dipanggil via thread pool
            enrich_result = await asyncio.get_running_loop().run_in_executor(
                None, self._company_enrichment_sync, domain
            )
            results.append(enrich_result)
        except Exception as e:
            self.logger.error(f"Company scan error: {e}")
            results.append(
                ScanResult(
                    platform="Company Enrichment",
                    username=domain,
                    status="ERROR",
                    status_code=0,
                    url="",
                    confidence=0.0,
                    extra={"error": str(e)},
                )
            )

        self.logger.success(f"Company scan completed -> {domain}")
        return results

    @staticmethod
    def _clean_domain(domain: str) -> str:
        domain = domain.strip().lower()
        for prefix in ["https://", "http://"]:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]
        if domain.startswith("www."):
            domain = domain[4:]
        if "." not in domain or len(domain) < 3:
            return ""
        return domain

    def _company_enrichment_sync(self, domain: str) -> ScanResult:
        if not self.api_key:
            return ScanResult(
                platform="Company Enrichment",
                username=domain,
                status="NOT_AVAILABLE",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"message": "Company Enrichment key not configured"},
            )

        # URL dan header IDENTIK dengan curl yang berhasil
        url = f"https://companyenrichment.abstractapi.com/v2/?api_key={self.api_key}&domain={domain}"
        headers = {
            "User-Agent": "curl/8.0.0",
            "Accept": "*/*",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return self._build_scan_result(domain, data)
            elif resp.status_code == 422:
                return ScanResult(
                    platform="Company Enrichment",
                    username=domain,
                    status="ERROR",
                    status_code=422,
                    url="",
                    confidence=0.0,
                    extra={"message": "Quota reached"},
                )
            else:
                return ScanResult(
                    platform="Company Enrichment",
                    username=domain,
                    status="ERROR",
                    status_code=resp.status_code,
                    url="",
                    confidence=0.0,
                    extra={"error": f"HTTP {resp.status_code}"},
                )
        except Exception:
            raise

    def _build_scan_result(self, domain: str, data: dict) -> ScanResult:
        extra = {
            "domain": data.get("domain", domain),
            "company_name": data.get("company_name"),
            "description": data.get("description"),
            "logo": data.get("logo"),
            "year_founded": data.get("year_founded"),
            "street_address": data.get("street_address"),
            "city": data.get("city"),
            "state": data.get("state"),
            "country": data.get("country"),
            "country_iso_code": data.get("country_iso_code"),
            "postal_code": data.get("postal_code"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "sic_code": data.get("sic_code"),
            "naics_code": data.get("naics_code"),
            "industry": data.get("industry"),
            "employee_count": data.get("employee_count"),
            "employee_range": data.get("employee_range"),
            "annual_revenue": data.get("annual_revenue"),
            "revenue_range": data.get("revenue_range"),
            "phone_numbers": data.get("phone_numbers", []),
            "email_addresses": data.get("email_addresses", []),
            "type": data.get("type"),
            "ticker": data.get("ticker"),
            "exchange": data.get("exchange"),
            "global_ranking": data.get("global_ranking"),
            "tags": data.get("tags", []),
            "technologies": data.get("technologies", []),
            "linkedin_url": data.get("linkedin_url"),
            "facebook_url": data.get("facebook_url"),
            "twitter_url": data.get("twitter_url"),
            "instagram_url": data.get("instagram_url"),
            "crunchbase_url": data.get("crunchbase_url"),
        }
        return ScanResult(
            platform="Company Enrichment",
            username=domain,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.95,
            extra=extra,
        )