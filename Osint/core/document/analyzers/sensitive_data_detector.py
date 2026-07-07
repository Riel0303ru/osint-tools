# core/document/analyzers/sensitive_data_detector.py
from __future__ import annotations

import re
from typing import Dict, List, Set


class SensitiveDataDetector:
    """Deteksi data sensitif dari teks dokumen."""

    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_REGEX = re.compile(r"\+?\d{7,15}")
    IP_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    URL_REGEX = re.compile(r"https?://[^\s,;]+")
    DOMAIN_REGEX = re.compile(r"\b([a-z0-9-]+\.)+[a-z]{2,}\b", re.IGNORECASE)
    USERNAME_REGEX = re.compile(r"@([a-zA-Z0-9._]{3,30})")
    API_KEY_REGEX = re.compile(r"(?:api[_-]?key|apikey|token|secret)[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?", re.IGNORECASE)
    TOKEN_REGEX = re.compile(r"(?:eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)")  # JWT

    @classmethod
    def detect(cls, text: str) -> Dict[str, List[str]]:
        if not text:
            return {
                "emails": [],
                "phones": [],
                "ips": [],
                "urls": [],
                "domains": [],
                "usernames": [],
                "api_keys": [],
                "tokens": [],
            }

        return {
            "emails": list(set(cls.EMAIL_REGEX.findall(text)))[:20],
            "phones": list(set(cls.PHONE_REGEX.findall(text)))[:20],
            "ips": list(set(cls.IP_REGEX.findall(text)))[:20],
            "urls": list(set(cls.URL_REGEX.findall(text)))[:20],
            "domains": list(set(cls.DOMAIN_REGEX.findall(text)))[:20],
            "usernames": list(set(cls.USERNAME_REGEX.findall(text)))[:20],
            "api_keys": list(set(cls.API_KEY_REGEX.findall(text)))[:10],
            "tokens": list(set(cls.TOKEN_REGEX.findall(text)))[:10],
        }