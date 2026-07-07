# core/ip/ip_scanner.py
from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any

import aiohttp
import dns.asyncresolver
import dns.exception
from dotenv import load_dotenv

from core.base.scan_result import ScanResult
from utils.logger import Logger

ENV_PATH = Path(__file__).resolve().parents[2] / ".env.local"
load_dotenv(ENV_PATH)


class IPScanner:
    """
    Advanced IP Intelligence Scanner.
    Multi-source: Abstract API (primary), ip-api.com (fallback geolocation),
    AbuseIPDB (reputation), plus built-in reverse DNS & ASN/cloud enrichment.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.abstract_key: Optional[str] = os.getenv("ABSTRACT_IP_KEY")
        self.abuseipdb_key: Optional[str] = os.getenv("ABUSEIPDB_API_KEY")

        if not self.abstract_key:
            self.logger.warning(
                "ABSTRACT_IP_KEY tidak ditemukan. Fallback ke ip-api.com untuk geolokasi."
            )

    async def scan_ip(self, ip_address: str) -> List[ScanResult]:
        self.logger.info(f"Scanning IP -> {ip_address}")

        # Validasi format
        if not ip_address or not self._is_valid_ip(ip_address):
            return [
                ScanResult(
                    platform="IP Validation",
                    username=ip_address,
                    status="ERROR",
                    status_code=0,
                    url="",
                    confidence=0.0,
                    extra={"error": "Invalid IP address format"},
                )
            ]

        # Deteksi IP privat
        if self._is_private_ip(ip_address):
            return [
                ScanResult(
                    platform="IP Intelligence",
                    username=ip_address,
                    status="FOUND",
                    status_code=200,
                    url="",
                    confidence=1.0,
                    extra={
                        "ip_address": ip_address,
                        "is_private": True,
                        "message": "IP privat (lokal) – tidak dapat dianalisis lebih lanjut.",
                    },
                )
            ]

        # Jalankan semua enrichment secara paralel
        results: List[ScanResult] = []
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._geolocation_lookup(session, ip_address),
                self._reverse_dns_lookup(ip_address),
                self._reputation_check(session, ip_address),
            ]
            enrichment_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Proses hasil geolokasi (prioritas Abstract > ip-api)
        geo_result = enrichment_results[0] if not isinstance(enrichment_results[0], Exception) else None
        if isinstance(geo_result, Exception):
            self.logger.warning(f"Geolocation failed: {geo_result}")
            geo_result = None
        results.append(geo_result if geo_result else ScanResult(
            platform="Geolocation",
            username=ip_address,
            status="ERROR",
            status_code=0,
            url="",
            confidence=0.0,
            extra={"error": "Geolocation failed entirely"}
        ))

        # Reverse DNS
        rdns_result = enrichment_results[1] if not isinstance(enrichment_results[1], Exception) else None
        if isinstance(rdns_result, Exception):
            self.logger.warning(f"Reverse DNS failed: {rdns_result}")
            rdns_result = None
        if rdns_result:
            results.append(rdns_result)

        # Reputation
        rep_result = enrichment_results[2] if not isinstance(enrichment_results[2], Exception) else None
        if isinstance(rep_result, Exception):
            self.logger.warning(f"Reputation check failed: {rep_result}")
            rep_result = None
        if rep_result:
            results.append(rep_result)

        # Tambahan: Infrastruktur gabungan (dari geolokasi dan rdns)
        combined_extra = (geo_result.extra if geo_result else {}) | (rdns_result.extra if rdns_result else {})
        if combined_extra:
            results.append(ScanResult(
                platform="Infrastructure Analysis",
                username=ip_address,
                status="FOUND",
                status_code=200,
                url="",
                confidence=0.85,
                extra={
                    "cloud_provider": self._detect_cloud_provider(combined_extra),
                    "hosting_provider": self._detect_hosting_provider(combined_extra),
                    "infrastructure_type": self._classify_infrastructure(combined_extra),
                }
            ))

        self.logger.success(f"IP scan completed -> {ip_address}")
        return results

    # ------------------------------------------------------------------
    # Validasi
    # ------------------------------------------------------------------
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))

    @staticmethod
    def _is_private_ip(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            octets = [int(p) for p in parts]
        except ValueError:
            return False
        if octets[0] == 10:
            return True
        if octets[0] == 172 and 16 <= octets[1] <= 31:
            return True
        if octets[0] == 192 and octets[1] == 168:
            return True
        if octets[0] == 127:
            return True
        return False

    # ------------------------------------------------------------------
    # Geolocation (Abstract + Fallback ip-api.com)
    # ------------------------------------------------------------------
    async def _geolocation_lookup(self, session: aiohttp.ClientSession, ip: str) -> ScanResult:
        """Menggabungkan Abstract API dan ip-api.com."""
        # Coba Abstract dulu
        if self.abstract_key:
            abstract_result = await self._abstract_lookup(session, ip)
            if abstract_result and abstract_result.status == "FOUND":
                return abstract_result

        # Fallback ke ip-api.com
        self.logger.info("Abstract API tidak tersedia/gagal, fallback ke ip-api.com")
        return await self._ipapi_lookup(session, ip)

    async def _abstract_lookup(self, session: aiohttp.ClientSession, ip: str) -> Optional[ScanResult]:
        url = f"https://ip-intelligence.abstractapi.com/v1/?api_key={self.abstract_key}&ip_address={ip}"
        try:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._parse_abstract_response(ip, data)
        except Exception as e:
            self.logger.warning(f"Abstract API error: {e}")
        return None

    async def _ipapi_lookup(self, session: aiohttp.ClientSession, ip: str) -> ScanResult:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,as,reverse,query"
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status") == "success":
                        return self._parse_ipapi_response(ip, data)
                    else:
                        return ScanResult(
                            platform="Geolocation",
                            username=ip,
                            status="NOT_FOUND",
                            status_code=404,
                            url="",
                            confidence=0.0,
                            extra={"message": data.get("message", "IP not found")}
                        )
        except Exception as e:
            self.logger.error(f"ip-api.com error: {e}")
        return ScanResult(
            platform="Geolocation",
            username=ip,
            status="ERROR",
            status_code=0,
            url="",
            confidence=0.0,
            extra={"error": "Geolocation failed"}
        )

    def _parse_abstract_response(self, ip: str, data: Dict[str, Any]) -> ScanResult:
        security = data.get("security", {})
        asn = data.get("asn", {})
        company = data.get("company", {})
        location = data.get("location", {})
        timezone = data.get("timezone", {})
        flag = data.get("flag", {})
        currency = data.get("currency", {})

        extra = {
            "ip_address": ip,
            "source": "AbstractAPI",
            # Security
            "is_vpn": security.get("is_vpn", False),
            "is_proxy": security.get("is_proxy", False),
            "is_tor": security.get("is_tor", False),
            "is_hosting": security.get("is_hosting", False),
            "is_relay": security.get("is_relay", False),
            "is_mobile": security.get("is_mobile", False),
            "is_abuse": security.get("is_abuse", False),
            # ASN
            "asn": asn.get("asn"),
            "asn_name": asn.get("name"),
            "asn_domain": asn.get("domain"),
            "asn_type": asn.get("type"),
            # Company
            "company_name": company.get("name"),
            "company_domain": company.get("domain"),
            "company_type": company.get("type"),
            # Location
            "city": location.get("city"),
            "region": location.get("region"),
            "country": location.get("country"),
            "country_code": location.get("country_code"),
            "continent": location.get("continent"),
            "longitude": location.get("longitude"),
            "latitude": location.get("latitude"),
            "timezone_name": timezone.get("name"),
            "local_time": timezone.get("local_time"),
            "flag_emoji": flag.get("emoji"),
            "currency_code": currency.get("code"),
            "currency_symbol": currency.get("symbol"),
        }
        return ScanResult(
            platform="Geolocation",
            username=ip,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.95,
            extra=extra,
        )

    def _parse_ipapi_response(self, ip: str, data: Dict[str, Any]) -> ScanResult:
        asn_str = data.get("as", "")
        asn_parts = asn_str.split(" ", 1)
        extra = {
            "ip_address": ip,
            "source": "ip-api.com",
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "longitude": data.get("lon"),
            "latitude": data.get("lat"),
            "isp": data.get("isp"),
            "org": data.get("org"),
            "reverse_dns": data.get("reverse"),
            "asn": asn_parts[0] if asn_parts else None,
            "asn_name": asn_parts[1] if len(asn_parts) > 1 else None,
        }
        return ScanResult(
            platform="Geolocation",
            username=ip,
            status="FOUND",
            status_code=200,
            url="",
            confidence=0.85,
            extra=extra,
        )

    # ------------------------------------------------------------------
    # Reverse DNS & ASN (mandiri)
    # ------------------------------------------------------------------
    async def _reverse_dns_lookup(self, ip: str) -> ScanResult:
        try:
            answers = await dns.asyncresolver.resolve_address(ip)
            hostnames = [str(r) for r in answers]
            return ScanResult(
                platform="Reverse DNS",
                username=ip,
                status="FOUND" if hostnames else "NOT_FOUND",
                status_code=200 if hostnames else 404,
                url="",
                confidence=0.95 if hostnames else 0.5,
                extra={"reverse_dns": hostnames, "source": "DNS"},
            )
        except dns.exception.DNSException:
            return ScanResult(
                platform="Reverse DNS",
                username=ip,
                status="NOT_FOUND",
                status_code=404,
                url="",
                confidence=0.4,
                extra={"reverse_dns": [], "source": "DNS"},
            )
        except Exception as e:
            return ScanResult(
                platform="Reverse DNS",
                username=ip,
                status="ERROR",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"error": str(e)},
            )

    # ------------------------------------------------------------------
    # Reputation (AbuseIPDB)
    # ------------------------------------------------------------------
    async def _reputation_check(self, session: aiohttp.ClientSession, ip: str) -> ScanResult:
        if not self.abuseipdb_key:
            return ScanResult(
                platform="Reputation",
                username=ip,
                status="NOT_AVAILABLE",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"message": "AbuseIPDB key not configured"},
            )
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": self.abuseipdb_key, "Accept": "application/json"}
        params = {"ipAddress": ip, "maxAgeInDays": "90"}
        try:
            async with session.get(url, headers=headers, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    score = data.get("data", {}).get("abuseConfidenceScore", 0)
                    return ScanResult(
                        platform="Reputation",
                        username=ip,
                        status="FOUND",
                        status_code=200,
                        url=f"https://www.abuseipdb.com/check/{ip}",
                        confidence=0.9,
                        extra={
                            "abuse_score": score,
                            "total_reports": data.get("data", {}).get("totalReports"),
                            "is_abusive": score > 80,
                        },
                    )
        except Exception as e:
            self.logger.warning(f"AbuseIPDB error: {e}")
        return ScanResult(
            platform="Reputation",
            username=ip,
            status="ERROR",
            status_code=0,
            url="",
            confidence=0.0,
            extra={"error": "Reputation check failed"},
        )

    # ------------------------------------------------------------------
    # Cloud / Hosting Detection
    # ------------------------------------------------------------------
    def _detect_cloud_provider(self, extra: Dict) -> Optional[str]:
        rdns = " ".join(extra.get("reverse_dns", [])).lower()
        asn_name = extra.get("asn_name", "").lower()
        isp = extra.get("isp", "").lower()
        org = extra.get("org", "").lower()
        combined = f"{rdns} {asn_name} {isp} {org}"
        if any(w in combined for w in ["amazon", "aws", "amazonaws"]):
            return "AWS"
        if any(w in combined for w in ["microsoft", "azure", "msft"]):
            return "Azure"
        if any(w in combined for w in ["google", "gcp", "google cloud"]):
            return "GCP"
        if any(w in combined for w in ["cloudflare", "cf"]):
            return "Cloudflare"
        if any(w in combined for w in ["digitalocean"]):
            return "DigitalOcean"
        if any(w in combined for w in ["hetzner"]):
            return "Hetzner"
        if any(w in combined for w in ["ovh", "ovhcloud"]):
            return "OVH"
        if any(w in combined for w in ["vultr"]):
            return "Vultr"
        if any(w in combined for w in ["linode"]):
            return "Linode"
        return None

    def _detect_hosting_provider(self, extra: Dict) -> Optional[str]:
        asn_name = extra.get("asn_name", "")
        isp = extra.get("isp", "")
        org = extra.get("org", "")
        return asn_name or isp or org or None

    def _classify_infrastructure(self, extra: Dict) -> str:
        if extra.get("is_vpn"):
            return "VPN"
        if extra.get("is_tor"):
            return "TOR Exit Node"
        if extra.get("is_proxy"):
            return "Proxy"
        if extra.get("is_mobile"):
            return "Mobile Network"
        cloud = self._detect_cloud_provider(extra)
        if cloud:
            return f"Cloud ({cloud})"
        if extra.get("is_hosting") or extra.get("asn_type") == "hosting":
            return "Hosting/Data Center"
        if extra.get("isp") and "residential" in extra.get("isp", "").lower():
            return "Residential"
        return "Business/Corporate"