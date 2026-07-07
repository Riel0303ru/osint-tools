# core/username/async_username_scanner.py
from __future__ import annotations

import asyncio
import random
import re
import time
from typing import Dict, List, Optional, Tuple

import httpx
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)

from core.username.username_scanner import UsernameScanner
from core.username.username_variations import UsernameVariations
from core.username.platforms import PLATFORMS


class AsyncUsernameScanner(UsernameScanner):
    """Advanced async username scanner with metadata extraction and confidence enrichment."""

    # Pola regex untuk ekstraksi metadata dari halaman profil
    META_NAME_RE = re.compile(r'<meta[^>]+name="([^"]+)"[^>]+content="([^"]+)"', re.IGNORECASE)
    META_PROPERTY_RE = re.compile(r'<meta[^>]+property="([^"]+)"[^>]+content="([^"]+)"', re.IGNORECASE)
    TITLE_RE = re.compile(r'<title>(.*?)</title>', re.IGNORECASE)
    OG_TITLE_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', re.IGNORECASE)
    OG_IMAGE_RE = re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', re.IGNORECASE)
    OG_DESCRIPTION_RE = re.compile(r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"', re.IGNORECASE)
    TWITTER_IMAGE_RE = re.compile(r'<meta[^>]+name="twitter:image"[^>]+content="([^"]+)"', re.IGNORECASE)
    LOCATION_RE = re.compile(r'<meta[^>]+name="twitter:data2"[^>]+content="([^"]+)"', re.IGNORECASE)

    def __init__(self, base_dir: str = "Osint"):
        super().__init__(base_dir=base_dir)
        self.variations_engine = UsernameVariations()

        self.max_concurrent_tasks = 40
        self.enable_stealth = True
        self.delay_min = 0.05
        self.delay_max = 0.25

        self.platforms = PLATFORMS

    def build_variations(self, username: str) -> List[str]:
        variations = self.variations_engine.generate(username)
        return variations[:300]

    def sort_platforms(
        self,
        platforms: List[Dict],
        priority: List[str]
    ) -> List[Dict]:
        priority_set = set(priority or [])
        return sorted(
            platforms,
            key=lambda p: 0 if p["name"] in priority_set else 1
        )

    def get_platform_data(self, platform_name: str) -> Optional[Dict]:
        for p in self.platforms:
            if p["name"] == platform_name:
                return p
        return None

    def build_profile_url(self, platform: str, username: str) -> str:
        data = self.get_platform_data(platform)
        if not data:
            return ""
        return data["url"].replace("{}", username)

    def get_available_platforms(self) -> List[str]:
        return [p["name"] for p in self.platforms]

    async def request(self, client: httpx.AsyncClient, url: str, method: str) -> Dict:
        try:
            res = await client.request(method, url)
            return {
                "ok": True,
                "status": res.status_code,
                "url": str(res.url),
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "url": url,
            }

    @staticmethod
    def _classify_status(status_code: int, expected_codes: List[int]) -> str:
        if status_code in expected_codes:
            return "FOUND"
        if status_code == 404:
            return "NOT_FOUND"
        return "UNKNOWN"

    def build_tasks(
        self,
        variations: List[str],
        platforms: List[Dict],
        budget: int
    ) -> List[Tuple[Dict, str]]:
        tasks: List[Tuple[Dict, str]] = []
        if not variations or not platforms:
            return tasks

        v_idx = 0
        p_idx = 0
        while len(tasks) < budget:
            platform_data = platforms[p_idx % len(platforms)]
            variation = variations[v_idx % len(variations)]
            tasks.append((platform_data, variation))

            p_idx += 1
            if p_idx % len(platforms) == 0:
                v_idx += 1

        return tasks

    async def scan_one(
        self,
        client: httpx.AsyncClient,
        sem: asyncio.Semaphore,
        platform_data: Dict,
        username: str
    ) -> Dict:
        async with sem:
            if self.enable_stealth:
                await asyncio.sleep(
                    random.uniform(self.delay_min, self.delay_max)
                )

            platform_name = platform_data["name"]
            url = platform_data["url"].replace("{}", username)

            has_content_rules = bool(
                platform_data.get("content_required") or platform_data.get("content_forbidden")
            )
            method = "GET" if has_content_rules else platform_data.get("method", "HEAD")

            try:
                response = await client.request(method, url)
                status_code = response.status_code
                final_url = str(response.url)
                text = response.text if method == "GET" else ""
            except Exception as e:
                return {
                    "platform": platform_name,
                    "username": username,
                    "status": "ERROR",
                    "status_code": None,
                    "url": url,
                    "confidence": 0.0,
                    "extra": {"error": str(e)}
                }

            expected_codes = platform_data.get("status_codes", [200])
            status = self._classify_status(status_code, expected_codes)
            confidence = 1.0
            extra = {}

            if status == "FOUND" and has_content_rules and text:
                # Validasi content_required
                required = platform_data.get("content_required")
                if required:
                    required_str = required.replace("{}", username)
                    if required_str not in text:
                        status = "NOT_FOUND"
                        confidence = 0.9
                        extra["validation_failed"] = "content_required_not_found"

                # Validasi content_forbidden
                if status == "FOUND":
                    forbidden = platform_data.get("content_forbidden")
                    if forbidden and forbidden in text:
                        status = "NOT_FOUND"
                        confidence = 0.95
                        extra["validation_failed"] = "content_forbidden_found"

            if status == "FOUND" and has_content_rules:
                confidence = 1.0
                extra["content_validated"] = True

                # ============================================================
                # EKSTRAKSI METADATA UNTUK KORELASI IDENTITAS
                # ============================================================
                extra["bio"] = self._extract_bio(text)
                extra["display_name"] = self._extract_display_name(text)
                extra["avatar_url"] = self._extract_avatar_url(text)
                extra["location"] = self._extract_location(text)
                extra["website"] = self._extract_website(text)
                extra["description"] = self._extract_og_description(text)
                extra["page_title"] = self._extract_title(text)

                # Hapus None
                extra = {k: v for k, v in extra.items() if v is not None}

            # ============================================================
            # KOREKSI CONFIDENCE BERDASARKAN STATUS CODE
            # ============================================================
            if status == "ERROR":
                confidence = 0.0
            elif status == "NOT_FOUND":
                confidence = 0.8
            elif status == "UNKNOWN":
                confidence = 0.3

            return {
                "platform": platform_name,
                "username": username,
                "status": status,
                "status_code": status_code,
                "url": final_url,
                "confidence": confidence,
                "extra": extra,
            }

    # ============================================================
    # METADATA EXTRACTION HELPERS
    # ============================================================

    @staticmethod
    def _extract_bio(html: str) -> Optional[str]:
        """Ekstrak bio dari meta tag description / og:description."""
        match = AsyncUsernameScanner.OG_DESCRIPTION_RE.search(html)
        if match:
            desc = match.group(1)
            if len(desc) > 10:
                return desc[:500]
        match = AsyncUsernameScanner.META_NAME_RE.search(html)
        if match and match.group(1).lower() == "description":
            return match.group(2)[:500]
        return None

    @staticmethod
    def _extract_display_name(html: str) -> Optional[str]:
        """Ekstrak display name dari og:title."""
        match = AsyncUsernameScanner.OG_TITLE_RE.search(html)
        if match:
            title = match.group(1)
            # Bersihkan sufiks platform jika ada
            for suffix in [" | LinkedIn", " | Twitter", " · GitHub", " (@", " | Facebook",
                           " | Instagram", " | TikTok", " - YouTube", " | Twitch"]:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            return title[:200]
        return None

    @staticmethod
    def _extract_avatar_url(html: str) -> Optional[str]:
        """Ekstrak avatar dari og:image atau twitter:image."""
        match = AsyncUsernameScanner.OG_IMAGE_RE.search(html)
        if match:
            return match.group(1)[:500]
        match = AsyncUsernameScanner.TWITTER_IMAGE_RE.search(html)
        if match:
            return match.group(1)[:500]
        return None

    @staticmethod
    def _extract_location(html: str) -> Optional[str]:
        """Ekstrak lokasi dari berbagai meta tag."""
        # Twitter data2
        match = AsyncUsernameScanner.LOCATION_RE.search(html)
        if match:
            return match.group(1)[:200]
        # Meta name="location"
        for pattern in [
            re.compile(r'<meta[^>]+name="location"[^>]+content="([^"]+)"', re.IGNORECASE),
            re.compile(r'<meta[^>]+property="og:locality"[^>]+content="([^"]+)"', re.IGNORECASE),
        ]:
            match = pattern.search(html)
            if match:
                return match.group(1)[:200]
        return None

    @staticmethod
    def _extract_website(html: str) -> Optional[str]:
        """Ekstrak website dari meta tag atau link."""
        for pattern in [
            re.compile(r'<meta[^>]+property="og:url"[^>]+content="([^"]+)"', re.IGNORECASE),
            re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', re.IGNORECASE),
        ]:
            match = pattern.search(html)
            if match:
                return match.group(1)[:300]
        return None

    @staticmethod
    def _extract_title(html: str) -> Optional[str]:
        """Ekstrak title halaman."""
        match = AsyncUsernameScanner.TITLE_RE.search(html)
        if match:
            return match.group(1).strip()[:300]
        return None

    @staticmethod
    def _extract_og_description(html: str) -> Optional[str]:
        """Ekstrak og:description."""
        match = AsyncUsernameScanner.OG_DESCRIPTION_RE.search(html)
        if match:
            return match.group(1)[:500]
        return None

    async def scan_username_async(
        self,
        username: str,
        budget: int = 100,
        priority_platforms: Optional[List[str]] = None
    ) -> List[Dict]:
        start = time.perf_counter()
        priority_platforms = priority_platforms or []

        sem = asyncio.Semaphore(self.max_concurrent_tasks)

        variations = self.build_variations(username)
        platforms_sorted = self.sort_platforms(self.platforms, priority_platforms)

        if not variations or not platforms_sorted:
            return []

        budget = max(1, budget)
        tasks = self.build_tasks(variations, platforms_sorted, budget)

        async with httpx.AsyncClient(
            timeout=self.timeout,
            verify=self.verify_ssl,
            headers=self.default_headers,
            follow_redirects=True
        ) as client:

            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]Scanning username..."),
                BarColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task_id = progress.add_task("scan", total=len(tasks))

                async def runner(p_data: Dict, uname: str):
                    res = await self.scan_one(client, sem, p_data, uname)
                    progress.advance(task_id)
                    return res

                results = await asyncio.gather(
                    *[runner(p, v) for p, v in tasks]
                )

        self.logger.info(
            f"Completed {len(results)} checks in {round(time.perf_counter() - start, 2)}s"
        )
        return results

    def scan_username(
        self,
        username: str,
        budget: int = 100,
        priority_platforms: Optional[List[str]] = None
    ) -> List[Dict]:
        return asyncio.run(
            self.scan_username_async(username, budget, priority_platforms)
        )