# core/company/analyzers/security_analyzer.py
from __future__ import annotations

import asyncio
from typing import Dict, Any
import aiohttp
from utils.logger import Logger


class SecurityAnalyzer:
    """Analisis security headers dan email security."""

    SECURITY_HEADERS = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy",
        "X-XSS-Protection",
        "Cross-Origin-Resource-Policy",
        "Cross-Origin-Opener-Policy",
        "Cross-Origin-Embedder-Policy",
    ]

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def analyze(self, domain: str) -> Dict[str, Any]:
        result = {
            "headers_found": [],
            "headers_missing": [],
            "cookie_security": {},
            "score": 0,
        }

        try:
            url = f"https://{domain}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10, allow_redirects=True) as resp:
                    headers = resp.headers

                    for header in self.SECURITY_HEADERS:
                        if header in headers:
                            result["headers_found"].append(header)
                        else:
                            result["headers_missing"].append(header)

                    # Cookie security
                    set_cookie = headers.get("Set-Cookie", "")
                    result["cookie_security"] = {
                        "http_only": "HttpOnly" in set_cookie,
                        "secure": "Secure" in set_cookie,
                        "same_site": "SameSite" in set_cookie,
                    }

                    result["score"] = len(result["headers_found"])
        except Exception as e:
            result["error"] = str(e)

        return result