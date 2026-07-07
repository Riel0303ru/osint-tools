# core/company/providers/dns_provider.py
from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Optional, Tuple
import dns.asyncresolver
import dns.exception

from core.base.scan_result import ScanResult
from utils.logger import Logger

# Database TXT verification patterns untuk SaaS detection
SAAS_TXT_PATTERNS = {
    "Google Workspace": ["google-site-verification", "globalsign-domain-verification"],
    "Microsoft 365": ["MS=ms", "microsoft-domain-verification"],
    "Atlassian": ["atlassian-domain-verification"],
    "Slack": ["slack-domain-verification"],
    "GitHub": ["github-domain-verification"],
    "Stripe": ["stripe-verification"],
    "Twilio": ["twilio-domain-verification"],
    "Figma": ["figma-domain-verification"],
    "Canva": ["canva-domain-verification"],
    "Postman": ["postman-domain-verification"],
    "Docker": ["docker-verification"],
    "Tailscale": ["tailscale-domain-verification"],
    "Cloudflare": ["cloudflare-verify"],
    "Vercel": ["vercel-dns"],
    "Netlify": ["netlify-domain-verification"],
    "Heroku": ["heroku-domain-verification"],
    "Zendesk": ["zendesk-domain-verification"],
    "HubSpot": ["hubspot-domain-verification"],
    "Mailchimp": ["mailchimp-domain-verification"],
    "Sentry": ["sentry-domain-verification"],
}

CDN_CNAME_PATTERNS = {
    "Cloudflare": [".cloudflare.net", ".cdn.cloudflare.net"],
    "Fastly": [".fastly.net", ".fastlylb.net"],
    "Akamai": [".akamaiedge.net", ".edgekey.net", ".edgesuite.net"],
    "Amazon CloudFront": [".cloudfront.net"],
    "Vercel": [".vercel-dns.com"],
    "Netlify": [".netlify.com", ".netlify.app"],
    "Google Cloud CDN": [".googleapis.com"],
    "Azure CDN": [".azureedge.net"],
    "StackPath": [".stackpathcdn.com"],
    "KeyCDN": [".kxcdn.com"],
    "BunnyCDN": [".b-cdn.net"],
}

class DNSProvider:
    """DNS intelligence dengan SaaS detection, CDN detection, dan analisis keamanan."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def analyze(self, domain: str) -> Dict:
        """
        Kembalikan dictionary lengkap hasil analisis DNS.
        """
        result = {
            "records": {},
            "saas_detected": [],
            "cdn_detected": [],
            "email_security": {},
            "suspicious_txt": [],
            "dangling_cname": [],
            "provider_identified": None,
        }

        # 1. Ambil semua record
        record_types = ["A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME", "SRV", "PTR", "CAA"]
        for rtype in record_types:
            try:
                answers = await dns.asyncresolver.resolve(domain, rtype)
                result["records"][rtype] = [str(r) for r in answers]
            except (dns.exception.DNSException, Exception):
                result["records"][rtype] = []

        # 2. Deteksi SaaS dari TXT records
        txt_records = result["records"].get("TXT", [])
        for txt in txt_records:
            txt_clean = txt.strip('"')
            for saas_name, patterns in SAAS_TXT_PATTERNS.items():
                for pattern in patterns:
                    if pattern in txt_clean and saas_name not in result["saas_detected"]:
                        result["saas_detected"].append(saas_name)

        # 3. Deteksi CDN dari CNAME records
        cname_records = result["records"].get("CNAME", [])
        for cname in cname_records:
            cname_lower = cname.lower().strip('.')
            for cdn_name, patterns in CDN_CNAME_PATTERNS.items():
                for pattern in patterns:
                    if pattern in cname_lower and cdn_name not in result["cdn_detected"]:
                        result["cdn_detected"].append(cdn_name)

        # 4. Analisis Email Security
        result["email_security"] = self._analyze_email_security(txt_records, domain)

        # 5. Deteksi TXT mencurigakan
        result["suspicious_txt"] = self._detect_suspicious_txt(txt_records)

        # 6. Deteksi Dangling CNAME
        result["dangling_cname"] = await self._detect_dangling_cname(cname_records)

        # 7. Identifikasi provider dari NS records
        result["provider_identified"] = self._identify_provider(result["records"].get("NS", []))

        return result

    def _analyze_email_security(self, txt_records: List[str], domain: str) -> Dict:
        spf = False
        dmarc = False
        dkim = False
        spf_record = ""
        dmarc_record = ""

        for txt in txt_records:
            txt_clean = txt.strip('"')
            if txt_clean.startswith("v=spf1"):
                spf = True
                spf_record = txt_clean
                # Deteksi kelemahan SPF
                if "+all" in txt_clean or "?all" in txt_clean:
                    spf_weak = True
                else:
                    spf_weak = False
            if txt_clean.startswith("v=DMARC1"):
                dmarc = True
                dmarc_record = txt_clean

        # Cek DKIM secara terpisah (simplified)
        try:
            # Coba selector umum
            import asyncio
            loop = asyncio.get_event_loop()
            try:
                answers = loop.run_until_complete(
                    dns.asyncresolver.resolve(f"default._domainkey.{domain}", 'TXT')
                )
                for r in answers:
                    if "v=DKIM1" in r.to_text():
                        dkim = True
                        break
            except Exception:
                pass
        except Exception:
            pass

        return {
            "spf": spf,
            "spf_record": spf_record,
            "spf_weak": spf_weak if spf else None,
            "dmarc": dmarc,
            "dmarc_record": dmarc_record,
            "dkim": dkim,
            "score": sum([spf, dmarc, dkim])  # 0-3
        }

    def _detect_suspicious_txt(self, txt_records: List[str]) -> List[str]:
        suspicious = []
        suspicious_keywords = [
            "password", "secret", "token", "api_key", "api-key",
            "private", "credential", "pwd", "passwd", "admin",
        ]
        for txt in txt_records:
            txt_clean = txt.strip('"').lower()
            for keyword in suspicious_keywords:
                if keyword in txt_clean:
                    suspicious.append(f"Suspicious keyword '{keyword}' in TXT: {txt[:80]}")
                    break
        return suspicious

    async def _detect_dangling_cname(self, cname_records: List[str]) -> List[str]:
        dangling = []
        for cname in cname_records:
            cname_clean = cname.strip('.').lower()
            # Cek apakah CNAME target bisa di-resolve
            try:
                await dns.asyncresolver.resolve(cname_clean, 'A')
            except dns.exception.DNSException:
                # CNAME target tidak resolve → mungkin dangling
                try:
                    await dns.asyncresolver.resolve(cname_clean, 'CNAME')
                except dns.exception.DNSException:
                    dangling.append(f"Dangling CNAME detected: {cname} → {cname_clean} (no resolution)")
        return dangling

    def _identify_provider(self, ns_records: List[str]) -> Optional[str]:
        provider_patterns = {
            "Cloudflare": ["cloudflare.com", "ns.cloudflare.com"],
            "AWS Route53": ["awsdns-", "amazonaws.com"],
            "Google Cloud DNS": ["googledomains.com"],
            "Azure DNS": ["azure-dns.com"],
            "GoDaddy": ["domaincontrol.com"],
            "Namecheap": ["registrar-servers.com"],
            "DigitalOcean": ["digitalocean.com"],
        }
        for ns in ns_records:
            ns_lower = ns.lower()
            for provider, patterns in provider_patterns.items():
                for pattern in patterns:
                    if pattern in ns_lower:
                        return provider
        return None