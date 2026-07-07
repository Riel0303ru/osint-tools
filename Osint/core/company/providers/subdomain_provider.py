# core/company/providers/subdomain_provider.py
from __future__ import annotations

from typing import Dict, Any, List
import aiohttp
from utils.logger import Logger


class SubdomainProvider:
    """Subdomain enumeration dari crt.sh."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def enumerate(self, domain: str) -> Dict[str, Any]:
        result = {
            "subdomains": [],
            "count": 0,
            "sources": [],
            "classification": {},
        }

        subdomains = set()

        # crt.sh
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://crt.sh/?q=%25.{domain}&output=json", timeout=20
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for entry in data:
                            name_value = entry.get("name_value", "")
                            for name in name_value.split("\n"):
                                name = name.strip().lower()
                                if name.endswith(f".{domain}") or name == domain:
                                    subdomains.add(name)
                        result["sources"].append("crt.sh")
        except Exception:
            pass

        subdomain_list = sorted(list(subdomains))
        result["subdomains"] = subdomain_list
        result["count"] = len(subdomain_list)

        return result