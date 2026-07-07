# core/correlation/entity_extractor.py
from __future__ import annotations

import re
from typing import List, Dict, Set
from core.base.scan_result import ScanResult


class EntityExtractor:
    """Mengekstrak entitas unik dari semua hasil scan."""

    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_REGEX = re.compile(r"\+?\d{7,15}")
    URL_REGEX = re.compile(r"https?://[^\s,;]+")
    DOMAIN_REGEX = re.compile(r"\b([a-z0-9-]+\.)+[a-z]{2,}\b", re.IGNORECASE)

    @classmethod
    def extract(cls, results: List[ScanResult]) -> Dict[str, Set[str]]:
        """
        Mengembalikan dictionary dengan kategori entitas:
        - usernames
        - emails
        - phones
        - domains
        - ips
        - social_links
        - avatar_urls
        - locations
        """
        entities = {
            "usernames": set(),
            "emails": set(),
            "phones": set(),
            "domains": set(),
            "ips": set(),
            "social_links": set(),
            "avatar_urls": set(),
            "locations": set(),
            "bios": set(),
        }

        for r in results:
            entities["usernames"].add(r.username)
            extra = r.extra or {}

            # Email
            if "email" in extra:
                entities["emails"].add(str(extra["email"]).lower())
            for key in ("emails", "email_addresses", "public_emails"):
                for val in extra.get(key, []) if isinstance(extra.get(key), list) else [extra.get(key)]:
                    if val and "@" in str(val):
                        entities["emails"].add(str(val).lower())

            # Phone
            if "phone" in extra:
                entities["phones"].add(str(extra["phone"]))
            for key in ("phone_numbers", "phones"):
                for val in extra.get(key, []) if isinstance(extra.get(key), list) else [extra.get(key)]:
                    if val:
                        entities["phones"].add(str(val))

            # Domain / Website
            for key in ("website", "blog", "domain", "url"):
                if key in extra and isinstance(extra[key], str):
                    domain = cls._extract_domain(extra[key])
                    if domain:
                        entities["domains"].add(domain)

            # IP
            for key in ("ip_address", "ip"):
                if key in extra and isinstance(extra[key], str):
                    entities["ips"].add(extra[key])

            # Social links
            for key in ("linkedin_url", "facebook_url", "twitter_url", "instagram_url",
                        "youtube_url", "github_url", "crunchbase_url", "profile_url"):
                if key in extra and isinstance(extra[key], str) and extra[key]:
                    entities["social_links"].add(extra[key])

            # Avatar
            for key in ("avatar_url", "logo", "flag_png"):
                if key in extra and isinstance(extra[key], str) and extra[key]:
                    entities["avatar_urls"].add(extra[key])

            # Location
            for key in ("location", "city", "country", "region"):
                if key in extra and isinstance(extra[key], str) and extra[key]:
                    entities["locations"].add(extra[key].lower())

            # Bio
            if "bio" in extra and isinstance(extra["bio"], str) and extra["bio"]:
                entities["bios"].add(extra["bio"][:200])

        return entities

    @classmethod
    def _extract_domain(cls, url: str) -> str:
        """Ekstrak domain dari URL."""
        if not url:
            return ""
        url = url.lower().replace("https://", "").replace("http://", "").replace("www.", "")
        url = url.split("/")[0].split(":")[0]
        return url