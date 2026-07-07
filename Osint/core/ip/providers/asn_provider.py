# core/ip/providers/asn_provider.py
from __future__ import annotations

from typing import Dict, Any
import aiohttp
from core.base.scan_result import ScanResult
from utils.logger import Logger


class ASNProvider:
    """ASN intelligence menggunakan API gratis ip-api.com dan peeringdb."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def lookup(self, ip: str) -> ScanResult:
        url = f"http://ip-api.com/json/{ip}?fields=as,asname,org,isp,query"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "success":
                            asn_str = data.get("as", "")
                            asn_number = None
                            asn_name = None
                            if asn_str:
                                parts = asn_str.split(" ", 1)
                                asn_number = parts[0] if parts else None
                                asn_name = parts[1] if len(parts) > 1 else None
                            return ScanResult(
                                platform="ASN Intelligence",
                                username=ip,
                                status="FOUND",
                                status_code=200,
                                url="",
                                confidence=0.9,
                                extra={
                                    "asn": asn_number,
                                    "asn_name": asn_name,
                                    "organization": data.get("org"),
                                    "isp": data.get("isp"),
                                    "ip": data.get("query"),
                                },
                            )
                    return ScanResult(
                        platform="ASN Intelligence",
                        username=ip,
                        status="ERROR",
                        status_code=resp.status,
                        url="",
                        confidence=0.0,
                        extra={"error": f"HTTP {resp.status}"},
                    )
        except Exception as e:
            return ScanResult(
                platform="ASN Intelligence",
                username=ip,
                status="ERROR",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"error": str(e)},
            )