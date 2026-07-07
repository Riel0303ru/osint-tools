# core/correlation/match_engine.py
from __future__ import annotations

from typing import Dict, Set, List, Tuple


class MatchEngine:
    """Mesin pencocokan entitas (exact, fuzzy, partial)."""

    @staticmethod
    def exact_match(entities_a: Dict[str, Set[str]], entities_b: Dict[str, Set[str]]) -> List[str]:
        """Temukan kecocokan persis antar kategori."""
        matches = []
        for category in entities_a:
            common = entities_a[category].intersection(entities_b[category])
            if common:
                matches.append(f"{category}: {', '.join(list(common)[:3])}")
        return matches

    @staticmethod
    def fuzzy_match_username(username_a: str, username_b: str, threshold: float = 0.8) -> float:
        """Fuzzy matching untuk username (ratio sederhana)."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, username_a.lower(), username_b.lower()).ratio()

    @staticmethod
    def find_similar_usernames(usernames: Set[str], threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """Cari pasangan username yang mirip."""
        similar = []
        user_list = list(usernames)
        for i in range(len(user_list)):
            for j in range(i + 1, len(user_list)):
                score = MatchEngine.fuzzy_match_username(user_list[i], user_list[j])
                if score >= threshold and score < 1.0:
                    similar.append((user_list[i], user_list[j], round(score, 3)))
        return similar