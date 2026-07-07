# core/ip/providers/abstract_provider.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
import aiohttp
from dotenv import load_dotenv

from core.base.scan_result import ScanResult
from utils.logger import Logger

ENV_PATH = Path(__file__).resolve().parents[3] / ".env.local"
load_dotenv(ENV_PATH)


class AbstractIPProvider:
    """Provider utama untuk Abstract IP Intelligence API."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key: Optional[str] = os.getenv("ABSTRACT_IP_KEY")

    async def lookup(self, ip: str) -> ScanResult:
        if not self.api_key:
            return ScanResult(
                platform="Abstract IP Intelligence",
                username=ip,
                status="NOT_AVAILABLE",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"message": "Abstract IP key not configured"},
            )

        url = f"https://ip-intelligence.abstractapi.com/v1/?api_key={self.api_key}&ip_address={ip}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._build_result(ip, data)
                    elif resp.status == 204:
                        return ScanResult(
                            platform="Abstract IP Intelligence",
                            username=ip,
                            status="NOT_FOUND",
                            status_code=204,
                            url="",
                            confidence=0.5,
                            extra={"message": "No data for this IP"},
                        )
                    else:
                        return ScanResult(
                            platform="Abstract IP Intelligence",
                            username=ip,
                            status="ERROR",
                            status_code=resp.status,
                            url="",
                            confidence=0.0,
                            extra={"error": f"HTTP {resp.status}"},
                        )
        except Exception as e:
            return ScanResult(
                platform="Abstract IP Intelligence",
                username=ip,
                status="ERROR",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"error": str(e)},
            )

    def _build_result(self, ip: str, data: dict) -> ScanResult:
        security = data.get("security", {})
        asn = data.get("asn", {})
        company = data.get("company", {})
        location = data.get("location", {})
        timezone = data.get("timezone", {})
        flag = data.get("flag", {})
        currency = data.get("currency", {})

        extra = {
            "ip_address": data.get("ip_address", ip),
            "is_private": False,
            "is_vpn": security.get("is_vpn", False),
            "is_proxy": security.get("is_proxy", False),
            "is_tor": security.get("is_tor", False),
            "is_hosting": security.get("is_hosting", False),
            "is_relay": security.get("is_relay", False),
            "is_mobile": security.get("is_mobile", False),
            "is_abuse": security.get("is_abuse", False),
            "asn": asn.get("asn"),
            "asn_name": asn.get("name"),
            "asn_domain": asn.get("domain"),
            "asn_type": asn.get("type"),
            "company_name": company.get("name"),
            "company_domain": company.get("domain"),
            "company_type": company.get("type"),
            "city": location.get("city"),
            "region": location.get("region"),
            "region_iso_code": location.get("region_iso_code"),
            "postal_code": location.get("postal_code"),
            "country": location.get("country"),
            "country_code": location.get("country_code"),
            "continent": location.get("continent"),
            "continent_code": location.get("continent_code"),
            "longitude": location.get("longitude"),
            "latitude": location.get("latitude"),
            "is_country_eu": location.get("is_country_eu", False),
            "timezone_name": timezone.get("name"),
            "timezone_abbreviation": timezone.get("abbreviation"),
            "utc_offset": timezone.get("utc_offset"),
            "local_time": timezone.get("local_time"),
            "is_dst": timezone.get("is_dst", False),
            "flag_emoji": flag.get("emoji"),
            "flag_png": flag.get("png"),
            "currency_name": currency.get("name"),
            "currency_code": currency.get("code"),
            "currency_symbol": currency.get("symbol"),
        }
        return ScanResult(
            platform="Abstract IP Intelligence",
            username=ip,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.95,
            extra=extra,
        )