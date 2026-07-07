# core/username/correlators/identity_correlator.py
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple
from core.base.scan_result import ScanResult


class IdentityCorrelator:
    """
    Mengkorelasikan identitas di berbagai platform berdasarkan metadata yang ditemukan.
    """

    EXTERNAL_LINK_REGEX = re.compile(
        r'(?:https?://)?(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}(?:/[^\s,;"]*)?'
    )
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def __init__(self):
        pass

    def correlate(self, results: List[ScanResult]) -> List[Dict]:
        """
        Terima list ScanResult dan kembalikan daftar akun yang saling terkait.
        Setiap entri berisi pasangan platform, confidence, dan bukti.
        """
        linked = []
        found_results = [r for r in results if r.status == "FOUND"]

        for i in range(len(found_results)):
            for j in range(i + 1, len(found_results)):
                a = found_results[i]
                b = found_results[j]
                evidence, confidence = self._match_pair(a, b)
                if evidence:
                    linked.append({
                        "platform_a": a.platform,
                        "platform_b": b.platform,
                        "username_a": a.username,
                        "username_b": b.username,
                        "confidence": round(confidence, 3),
                        "evidence": evidence,
                    })

        return sorted(linked, key=lambda x: x["confidence"], reverse=True)

    def _match_pair(self, a: ScanResult, b: ScanResult) -> Tuple[List[str], float]:
        evidence = []
        extra_a = a.extra or {}
        extra_b = b.extra or {}

        # 1. Username match (persis atau setelah normalisasi)
        if self._normalize_username(a.username) == self._normalize_username(b.username):
            evidence.append("identical_normalized_username")
            return evidence, 1.0  # sangat yakin

        # 2. Bio similarity (sederhana: keyword overlapping)
        bio_a = extra_a.get("bio", "")
        bio_b = extra_b.get("bio", "")
        if bio_a and bio_b:
            common = self._keyword_overlap(bio_a, bio_b)
            if common > 0.6:
                evidence.append(f"bio_similarity_{common:.2f}")

        # 3. Avatar / profile picture reference
        avatar_a = extra_a.get("avatar_url", "")
        avatar_b = extra_b.get("avatar_url", "")
        if avatar_a and avatar_b and self._compare_avatar_refs(avatar_a, avatar_b):
            evidence.append("avatar_reference_match")

        # 4. External links yang tumpang tindih
        links_a = self._extract_links(extra_a)
        links_b = self._extract_links(extra_b)
        shared_links = links_a.intersection(links_b)
        if shared_links:
            evidence.append("shared_external_links")
            evidence.append(str(shared_links))

        # 5. Nama display (case-insensitive)
        name_a = extra_a.get("name", "").lower().strip()
        name_b = extra_b.get("name", "").lower().strip()
        if name_a and name_b and name_a == name_b:
            evidence.append("display_name_match")

        # 6. Lokasi
        loc_a = extra_a.get("location", "").lower().strip()
        loc_b = extra_b.get("location", "").lower().strip()
        if loc_a and loc_b and loc_a == loc_b:
            evidence.append("location_match")

        if not evidence:
            return [], 0.0

        # Hitung confidence berdasarkan bobot bukti
        confidence = min(0.5 + len(evidence) * 0.15, 0.98)
        return evidence, confidence

    @staticmethod
    def _normalize_username(username: str) -> str:
        return re.sub(r'[\W_]+', '', username).lower()

    @staticmethod
    def _keyword_overlap(text_a: str, text_b: str) -> float:
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a.intersection(words_b)
        return len(intersection) / min(len(words_a), len(words_b))

    @staticmethod
    def _compare_avatar_refs(url_a: str, url_b: str) -> bool:
        # Bandingkan nama file atau hash jika tersedia
        file_a = url_a.rsplit("/", 1)[-1]
        file_b = url_b.rsplit("/", 1)[-1]
        return file_a == file_b

    @staticmethod
    def _extract_links(extra: Dict) -> Set[str]:
        links = set()
        for key in ("website", "blog", "profile_url", "url"):
            if key in extra and isinstance(extra[key], str):
                links.add(extra[key].lower().rstrip("/"))
        return links