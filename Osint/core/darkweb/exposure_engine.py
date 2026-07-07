# core/darkweb/exposure_engine.py
from __future__ import annotations

from typing import Dict


class ExposureEngine:
    """Menghitung exposure berdasarkan data yang bocor."""

    @staticmethod
    def analyze(parsed: Dict) -> Dict:
        exposure = {
            "email_exposure": len(parsed.get("emails", set())),
            "username_exposure": len(parsed.get("usernames", set())),
            "password_exposure": len(parsed.get("passwords", set())),
            "hashed_password_exposure": len(parsed.get("hashed_passwords", set())),
            "phone_exposure": len(parsed.get("phones", set())),
            "ip_exposure": len(parsed.get("ips", set())),
            "domain_exposure": len(parsed.get("domains", set())),
            "name_exposure": len(parsed.get("names", set())),
            "address_exposure": len(parsed.get("addresses", set())),
            "social_exposure": len(parsed.get("social", set())),
            "databases_count": len(parsed.get("databases", set())),
        }

        # Level exposure
        total = sum(exposure.values())
        if total > 50:
            exposure["exposure_level"] = "CRITICAL"
        elif total > 20:
            exposure["exposure_level"] = "HIGH"
        elif total > 5:
            exposure["exposure_level"] = "MEDIUM"
        elif total > 0:
            exposure["exposure_level"] = "LOW"
        else:
            exposure["exposure_level"] = "NONE"

        return exposure