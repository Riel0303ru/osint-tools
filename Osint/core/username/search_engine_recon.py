from __future__ import annotations

import webbrowser

from urllib.parse import quote_plus

from typing import Dict, List


class SearchEngineRecon:
    """
    Search engine reconnaissance engine.

    Features:
    - Google reconnaissance
    - Bing reconnaissance
    - DuckDuckGo reconnaissance
    - automatic browser opening
    - search dork generation
    - footprint intelligence
    """

    def __init__(self):

        # ==========================================
        # SEARCH ENGINES
        # ==========================================
        self.search_engines = {
            "google": (
                "https://www.google.com/search?q={}"
            ),

            "bing": (
                "https://www.bing.com/search?q={}"
            ),

            "duckduckgo": (
                "https://duckduckgo.com/?q={}"
            ),
        }

    # =========================================================
    # QUERY NORMALIZATION
    # =========================================================

    def normalize_query(
        self,
        query: str
    ) -> str:
        """
        Normalize search query.
        """

        return query.strip()

    # =========================================================
    # DORK GENERATORS
    # =========================================================

    def generate_basic_dorks(
        self,
        target: str
    ) -> List[str]:
        """
        Generate basic reconnaissance dorks.
        """

        target = self.normalize_query(
            target
        )

        dorks = [

            # direct username
            f'"{target}"',

            # social media
            f'"{target}" social media',

            # github
            f'site:github.com "{target}"',

            # reddit
            f'site:reddit.com "{target}"',

            # linkedin
            f'site:linkedin.com "{target}"',

            # instagram
            f'site:instagram.com "{target}"',

            # twitter/x
            f'site:x.com "{target}"',

            # facebook
            f'site:facebook.com "{target}"',

            # tiktok
            f'site:tiktok.com "{target}"',

            # youtube
            f'site:youtube.com "{target}"',

            # discord mentions
            f'"{target}" discord',

            # leaks / breaches
            f'"{target}" leak',

            f'"{target}" breach',

            # forum mentions
            f'"{target}" forum',

            # paste sites
            f'"{target}" pastebin',

        ]

        return dorks

    # =========================================================
    # SEARCH URL BUILDER
    # =========================================================

    def build_search_url(
        self,
        engine_name: str,
        query: str
    ) -> str:
        """
        Build search URL.
        """

        engine = self.search_engines.get(
            engine_name.lower()
        )

        if not engine:

            raise ValueError(
                (
                    f"Search engine "
                    f"'{engine_name}' not found."
                )
            )

        encoded_query = quote_plus(
            query
        )

        return engine.format(
            encoded_query
        )

    # =========================================================
    # BROWSER SEARCH
    # =========================================================

    def open_search(
        self,
        engine_name: str,
        query: str
    ):
        """
        Open search query in browser.
        """

        search_url = self.build_search_url(
            engine_name,
            query
        )

        webbrowser.open_new_tab(
            search_url
        )

    # =========================================================
    # MULTIPLE SEARCHES
    # =========================================================

    def run_recon(
        self,
        target: str,
        engine_name: str = "google",
        auto_open: bool = True,
        limit: int = 5
    ) -> List[Dict]:
        """
        Run reconnaissance queries.
        """

        dorks = self.generate_basic_dorks(
            target
        )

        results = []

        selected_dorks = dorks[:limit]

        for dork in selected_dorks:

            search_url = self.build_search_url(
                engine_name,
                dork
            )

            result = {
                "engine": engine_name,
                "query": dork,
                "url": search_url,
            }

            results.append(
                result
            )

            if auto_open:

                webbrowser.open_new_tab(
                    search_url
                )

        return results