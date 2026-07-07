# core/ip/providers/cloud_provider.py
from __future__ import annotations

from typing import Dict, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger

CLOUD_PATTERNS = {
    "AWS": ["amazon", "aws", "ec2", "compute.amazonaws.com"],
    "Azure": ["microsoft corporation", "azure", "cloudapp.net"],
    "Google Cloud": ["google cloud", "google llc", "google inc."],
    "Cloudflare": ["cloudflare", "cloudflare inc."],
    "Akamai": ["akamai", "akamaitechnologies"],
    "Fastly": ["fastly", "fastly inc."],
    "DigitalOcean": ["digitalocean", "digital ocean"],
    "Hetzner": ["hetzner", "hetzner online"],
    "OVH": ["ovh", "ovh sas"],
    "Oracle Cloud": ["oracle", "oracle corporation"],
    "Vultr": ["vultr", "choopa"],
    "Linode": ["linode", "linode llc"],
}

class CloudProvider:
    """Deteksi cloud provider berdasarkan ASN, organisasi, dan ISP."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def detect(self, asn_data: Optional[Dict] = None, abstract_data: Optional[Dict] = None) -> ScanResult:
        evidence = []
        cloud_provider = None
        confidence = 0.0

        # Gabungkan data dari berbagai sumber
        org_name = ""
        isp_name = ""
        asn_name = ""

        if asn_data:
            org_name = (asn_data.get("organization") or "").lower()
            isp_name = (asn_data.get("isp") or "").lower()
            asn_name = (asn_data.get("asn_name") or "").lower()

        if abstract_data:
            if not org_name:
                org_name = (abstract_data.get("company_name") or "").lower()
            if not isp_name:
                isp_name = (abstract_data.get("asn_name") or "").lower()

        combined = f"{org_name} {isp_name} {asn_name}"

        for provider, patterns in CLOUD_PATTERNS.items():
            for pattern in patterns:
                if pattern in combined:
                    cloud_provider = provider
                    evidence.append(f"Pattern '{pattern}' found in organization/ISP data")
                    break
            if cloud_provider:
                break

        if cloud_provider:
            confidence = 0.85
        else:
            # Cek dari flag hosting
            if abstract_data and abstract_data.get("is_hosting"):
                cloud_provider = "Hosting Provider (Unknown)"
                confidence = 0.6
                evidence.append("Flagged as hosting provider by Abstract API")

        status = "FOUND" if cloud_provider else "NOT_FOUND"
        return ScanResult(
            platform="Cloud Provider Detection",
            username="",  # akan diisi oleh workflow
            status=status,
            status_code=200 if cloud_provider else 404,
            url="",
            confidence=confidence,
            extra={
                "cloud_provider": cloud_provider,
                "evidence": evidence,
                "combined_org_info": combined[:200],
            },
        )