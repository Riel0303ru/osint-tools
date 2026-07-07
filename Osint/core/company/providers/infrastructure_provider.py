# core/company/providers/infrastructure_provider.py
from __future__ import annotations

import asyncio
from typing import Dict, Any, List
import aiohttp
import dns.asyncresolver
import dns.exception
from utils.logger import Logger


class InfrastructureProvider:
    """Infrastructure analysis: IP, ASN, hosting, CDN, geolocation."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def analyze(self, domain: str) -> Dict[str, Any]:
        result = {
            "status": "NOT_FOUND",
            "ip_addresses": [],
            "asn": None,
            "asn_name": None,
            "hosting_provider": None,
            "cloud_provider": None,
            "cdn_provider": None,
            "geolocation": {},
            "reverse_dns": [],
        }

        try:
            # Resolve IP
            answers = await dns.asyncresolver.resolve(domain, 'A')
            ip_addresses = [str(r) for r in answers]
            result["ip_addresses"] = ip_addresses
            result["status"] = "FOUND"

            if ip_addresses:
                ip = ip_addresses[0]
                # Geolocation via ip-api.com (gratis)
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"http://ip-api.com/json/{ip}", timeout=10) as resp:
                            if resp.status == 200:
                                geo = await resp.json()
                                if geo.get("status") == "success":
                                    result["geolocation"] = {
                                        "country": geo.get("country"),
                                        "region": geo.get("regionName"),
                                        "city": geo.get("city"),
                                        "isp": geo.get("isp"),
                                        "org": geo.get("org"),
                                        "asn": geo.get("as"),
                                        "lat": geo.get("lat"),
                                        "lon": geo.get("lon"),
                                    }
                                    # Parse ASN
                                    asn_str = geo.get("as", "")
                                    if asn_str:
                                        parts = asn_str.split(" ", 1)
                                        result["asn"] = parts[0] if parts else None
                                        result["asn_name"] = parts[1] if len(parts) > 1 else None

                                    # Deteksi hosting/cloud provider dari ISP/Org
                                    isp_org = (geo.get("isp", "") + " " + geo.get("org", "")).lower()
                                    result["hosting_provider"] = self._detect_hosting(isp_org)
                                    result["cloud_provider"] = self._detect_cloud(isp_org)
                                else:
                                    result["geolocation"] = {"message": "Private IP or not found"}
                except Exception:
                    pass

                # Reverse DNS
                try:
                    rev_answers = await dns.asyncresolver.resolve_address(ip)
                    result["reverse_dns"] = [str(r) for r in rev_answers]
                except Exception:
                    pass

            # Deteksi CDN dari CNAME / NS (diserahkan ke DNS Provider)
            result["cdn_detection_note"] = "CDN detection dilakukan oleh DNS Provider"

        except Exception as e:
            result["error"] = str(e)

        return result

    @staticmethod
    def _detect_hosting(isp_org: str) -> str:
        hosting_patterns = {
            "Amazon": ["amazon", "aws"],
            "Google Cloud": ["google cloud", "google llc"],
            "Microsoft Azure": ["microsoft azure", "microsoft corporation"],
            "DigitalOcean": ["digitalocean"],
            "OVH": ["ovh"],
            "Hetzner": ["hetzner"],
            "Linode": ["linode"],
            "Vultr": ["vultr"],
            "GoDaddy": ["godaddy"],
            "Cloudflare": ["cloudflare"],
        }
        for provider, patterns in hosting_patterns.items():
            if any(p in isp_org for p in patterns):
                return provider
        return None

    @staticmethod
    def _detect_cloud(isp_org: str) -> str:
        cloud_patterns = {
            "AWS": ["amazon", "aws"],
            "GCP": ["google cloud", "google llc"],
            "Azure": ["microsoft azure", "microsoft corporation"],
        }
        for provider, patterns in cloud_patterns.items():
            if any(p in isp_org for p in patterns):
                return provider
        return None