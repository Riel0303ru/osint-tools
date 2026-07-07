# core/darkweb/providers/dehashed_provider.py
from __future__ import annotations

import os
import asyncio
from typing import Dict
import aiohttp
from utils.logger import Logger


class DehashedProvider:
    """Provider untuk DeHashed API v2."""

    BASE_URL = "https://api.dehashed.com/v2"

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key = os.getenv("DEHASHED_API_KEY")
        if not self.api_key:
            self.logger.warning("DEHASHED_API_KEY tidak ditemukan. Dark Web Intelligence akan nonaktif.")

    async def search(self, query: str, page: int = 1, size: int = 100,
                     wildcard: bool = False, regex: bool = False,
                     de_dupe: bool = True) -> Dict:
        """
        Melakukan pencarian di DeHashed.
        """
        if not self.api_key:
            return {"error": "API key not configured", "entries": [], "total": 0}

        url = f"{self.BASE_URL}/search"
        payload = {
            "query": query,
            "page": page,
            "size": min(size, 10000),
            "wildcard": wildcard,
            "regex": regex,
            "de_dupe": de_dupe,
        }
        headers = {
            "Content-Type": "application/json",
            "DeHashed-Api-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=30) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 403:
                        # Coba parse body
                        try:
                            error_data = await resp.json()
                        except Exception:
                            error_data = {"error": "Insufficient Credits or Search Subscription required"}
                        return {
                            "error": error_data.get("error", "Access denied. You may need a search subscription and API credits."),
                            "entries": [],
                            "total": 0,
                        }
                    elif resp.status == 429:
                        self.logger.warning("DeHashed rate limit, retrying in 2s...")
                        await asyncio.sleep(2)
                        return await self.search(query, page, size, wildcard, regex, de_dupe)
                    else:
                        error_data = {}
                        try:
                            error_data = await resp.json()
                        except Exception:
                            pass
                        return {
                            "error": error_data.get("error", f"HTTP {resp.status}"),
                            "entries": [],
                            "total": 0,
                        }
        except Exception as e:
            self.logger.error(f"DeHashed API error: {e}")
            return {"error": str(e), "entries": [], "total": 0}