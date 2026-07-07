# core/username/correlators/persona_classifier.py
from __future__ import annotations

from typing import Dict, List
from core.base.scan_result import ScanResult


class PersonaClassifier:
    """
    Mengklasifikasikan persona digital berdasarkan platform yang ditemukan.
    """

    PLATFORM_PERSONA_MAP = {
        "GitHub": "developer",
        "GitLab": "developer",
        "Bitbucket": "developer",
        "Codecademy": "developer",
        "LeetCode": "developer",
        "HackerRank": "developer",
        "Codewars": "developer",
        "PyPI": "developer",
        "npm": "developer",
        "Docker Hub": "developer",
        "Stack Overflow": "developer",
        "Replit": "developer",
        "CodePen": "developer",
        "TryHackMe": "cybersecurity",
        "HackerOne": "cybersecurity",
        "Bugcrowd": "cybersecurity",
        "Twitch": "gamer",
        "Steam": "gamer",
        "Roblox": "gamer",
        "Chess.com": "gamer",
        "Osu!": "gamer",
        "YouTube": "creator",
        "Twitch": "creator",  # bisa keduanya
        "TikTok": "creator",
        "Instagram": "creator",
        "Behance": "artist",
        "Dribbble": "artist",
        "DeviantArt": "artist",
        "ArtStation": "artist",
        "SoundCloud": "musician",
        "Spotify": "musician",
        "Mixcloud": "musician",
        "Bandcamp": "musician",
        "Fiverr": "freelancer",
        "Upwork": "freelancer",
        "Etsy": "business",
        "eBay": "business",
        "LinkedIn": "business",
    }

    @classmethod
    def classify(cls, results: List[ScanResult]) -> Dict:
        """
        Kembalikan persona dominan berdasarkan platform yang ditemukan.
        """
        if not results:
            return {"persona": "unknown", "confidence": 0.0, "evidence": []}

        found_platforms = [r.platform for r in results if r.status == "FOUND"]
        persona_scores: Dict[str, int] = {}
        evidence = []

        for platform in found_platforms:
            persona = cls.PLATFORM_PERSONA_MAP.get(platform)
            if persona:
                persona_scores[persona] = persona_scores.get(persona, 0) + 1
                evidence.append(platform)

        if not persona_scores:
            return {"persona": "unknown", "confidence": 0.0, "evidence": evidence}

        # Pilih persona dengan skor tertinggi
        dominant = max(persona_scores, key=persona_scores.get)
        total_found = len(found_platforms)
        confidence = min(persona_scores[dominant] / max(total_found, 1), 1.0)

        return {
            "persona": dominant,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "persona_scores": persona_scores,
        }