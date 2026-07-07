# core/company/providers/whois_provider.py
from __future__ import annotations

import asyncio
from typing import Dict, Optional
import whois
import aiohttp

from utils.logger import Logger

class WhoisProvider:
    """Multi-provider WHOIS dengan fallback."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def lookup(self, domain: str) -> Dict:
        """
        Lakukan WHOIS lookup dengan beberapa provider secara berurutan.
        Mengembalikan dictionary terstruktur.
        """
        result = await self._primary_whois(domain)
        if result.get("status") == "ERROR":
            self.logger.warning("Primary WHOIS failed, trying fallback...")
            result = await self._fallback_whois(domain)
        return result

    async def _primary_whois(self, domain: str) -> Dict:
        """Provider utama: python-whois (offline)."""
        try:
            w = await asyncio.to_thread(whois.whois, domain)
            if w.domain_name:
                return self._normalize_whois(w, domain)
            return {"status": "NOT_FOUND", "domain": domain}
        except Exception as e:
            return {"status": "ERROR", "domain": domain, "error": str(e)}

    async def _fallback_whois(self, domain: str) -> Dict:
        """Provider fallback: whois.com API (gratis, tanpa key)."""
        url = f"https://www.whois.com/whois/{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        # Parsing sederhana (bisa ditingkatkan)
                        return self._parse_whois_html(text, domain)
        except Exception as e:
            return {"status": "ERROR", "domain": domain, "error": str(e)}
        return {"status": "ERROR", "domain": domain, "error": "All providers failed"}

    def _normalize_whois(self, w, domain: str) -> Dict:
        """Normalisasi hasil WHOIS ke format seragam."""
        return {
            "status": "FOUND",
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date) if w.creation_date else None,
            "expiration_date": str(w.expiration_date) if w.expiration_date else None,
            "updated_date": str(w.updated_date) if w.updated_date else None,
            "name_servers": w.name_servers[:5] if w.name_servers else [],
            "org": w.org,
            "country": w.country,
            "dnssec": w.dnssec,
            "emails": w.emails,
        }

    def _parse_whois_html(self, html: str, domain: str) -> Dict:
        """Parse HTML whois.com (sederhana)."""
        import re
        result = {"status": "FOUND", "domain": domain}
        patterns = {
            "registrar": r"Registrar:\s*(.+)",
            "creation_date": r"Creation Date:\s*(.+)",
            "expiration_date": r"Registrar Registration Expiration Date:\s*(.+)",
            "name_servers": r"Name Server:\s*(.+)",
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()
        return result