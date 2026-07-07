# core/company/providers/tech_provider.py
from __future__ import annotations

from typing import Dict, Any
import aiohttp
from utils.logger import Logger


class TechProvider:
    """Technology fingerprinting sederhana."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def fingerprint(self, domain: str) -> Dict[str, Any]:
        result = {
            "technologies": [],
            "categories": {},
            "confidence": 0,
        }

        url = f"https://{domain}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    headers = dict(resp.headers)
                    body = await resp.text()

                    tech = []

                    # Server header
                    server = headers.get("server", "").lower()
                    if "cloudflare" in server:
                        tech.append("Cloudflare")
                    if "nginx" in server:
                        tech.append("nginx")
                    if "apache" in server:
                        tech.append("Apache")

                    # Powered-By
                    powered = headers.get("x-powered-by", "").lower()
                    if "php" in powered:
                        tech.append("PHP")
                    if "express" in powered:
                        tech.append("Express.js")
                    if "next.js" in powered:
                        tech.append("Next.js")

                    # Body detection sederhana
                    body_lower = body.lower()
                    if "wp-content" in body_lower:
                        tech.append("WordPress")
                    if "shopify" in body_lower:
                        tech.append("Shopify")
                    if "react" in body_lower:
                        tech.append("React")
                    if "vue" in body_lower:
                        tech.append("Vue.js")
                    if "google-analytics" in body_lower or "gtag" in body_lower:
                        tech.append("Google Analytics")

                    result["technologies"] = list(set(tech))
                    result["confidence"] = 0.7 if tech else 0.2

        except Exception as e:
            result["error"] = str(e)

        return result