# core/username/correlators/profile_matcher.py
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple
from core.base.scan_result import ScanResult


class ProfileMatcher:
    """
    Mencocokkan profil berdasarkan bio, avatar, lokasi, dan tautan eksternal.
    """

    def match(self, results: List[ScanResult]) -> List[Dict]:
        """
        Mengembalikan daftar pasangan profil yang cocok dengan skor kemiripan.
        """
        matches = []
        found = [r for r in results if r.status == "FOUND"]
        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                score, reasons = self._score_pair(found[i], found[j])
                if score > 0.4:
                    matches.append({
                        "platform_a": found[i].platform,
                        "platform_b": found[j].platform,
                        "similarity_score": round(score, 3),
                        "reasons": reasons,
                    })
        return sorted(matches, key=lambda x: x["similarity_score"], reverse=True)

    def _score_pair(self, a: ScanResult, b: ScanResult) -> Tuple[float, List[str]]:
        reasons = []
        score = 0.0
        extra_a = a.extra or {}
        extra_b = b.extra or {}

        # Nama display
        name_a = extra_a.get("name", "").lower().strip()
        name_b = extra_b.get("name", "").lower().strip()
        if name_a and name_b and name_a == name_b:
            score += 0.35
            reasons.append("display_name_match")

        # Bio
        bio_a = extra_a.get("bio", "")
        bio_b = extra_b.get("bio", "")
        if bio_a and bio_b:
            common = self._word_overlap(bio_a, bio_b)
            if common > 0.6:
                score += common * 0.25
                reasons.append(f"bio_overlap_{common:.2f}")

        # Lokasi
        loc_a = extra_a.get("location", "").lower().strip()
        loc_b = extra_b.get("location", "").lower().strip()
        if loc_a and loc_b and loc_a == loc_b:
            score += 0.15
            reasons.append("location_match")

        # Website/blog
        links_a = set(extra_a.get(k, "") for k in ("website", "blog") if extra_a.get(k))
        links_b = set(extra_b.get(k, "") for k in ("website", "blog") if extra_b.get(k))
        shared = links_a.intersection(links_b)
        if shared:
            score += 0.2
            reasons.append("shared_website")

        # Avatar
        avatar_a = extra_a.get("avatar_url", "")
        avatar_b = extra_b.get("avatar_url", "")
        if avatar_a and avatar_b and self._same_avatar_filename(avatar_a, avatar_b):
            score += 0.3
            reasons.append("avatar_filename_match")

        return min(score, 1.0), reasons

    @staticmethod
    def _word_overlap(text_a: str, text_b: str) -> float:
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / min(len(words_a), len(words_b))

    @staticmethod
    def _same_avatar_filename(url_a: str, url_b: str) -> bool:
        return url_a.rsplit("/", 1)[-1] == url_b.rsplit("/", 1)[-1]