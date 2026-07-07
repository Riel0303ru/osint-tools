# core/correlation/normalizer.py
from __future__ import annotations

import re
from typing import Dict, Set


class Normalizer:
    """Normalisasi entitas untuk perbandingan yang akurat."""

    @staticmethod
    def normalize_username(username: str) -> str:
        """Hapus karakter khusus, lowercase."""
        return re.sub(r'[\W_]+', '', username).lower()

    @staticmethod
    def normalize_email(email: str) -> str:
        """Lowercase email."""
        return email.strip().lower()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Hapus semua karakter non-digit, simpan + jika internasional."""
        cleaned = re.sub(r'[^\d+]', '', phone)
        return cleaned

    @staticmethod
    def normalize_domain(domain: str) -> str:
        """Lowercase domain."""
        return domain.strip().lower()

    @classmethod
    def normalize_all(cls, entities: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """Normalisasi seluruh kategori entitas."""
        normalized = {}
        for category, values in entities.items():
            if category in ("usernames",):
                normalized[category] = {cls.normalize_username(v) for v in values}
            elif category == "emails":
                normalized[category] = {cls.normalize_email(v) for v in values}
            elif category == "phones":
                normalized[category] = {cls.normalize_phone(v) for v in values}
            elif category == "domains":
                normalized[category] = {cls.normalize_domain(v) for v in values}
            else:
                normalized[category] = {v.lower().strip() for v in values if isinstance(v, str)}
        return normalized