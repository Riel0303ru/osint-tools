# core/darkweb/identity_correlator.py
from __future__ import annotations

from typing import Dict, List, Set


class IdentityCorrelator:
    """Mengkorelasikan identitas yang ditemukan di breach."""

    @staticmethod
    def correlate(parsed: Dict[str, Set[str]]) -> Dict:
        correlations = []

        # Email ↔ Username
        emails = parsed.get("emails", set())
        usernames = parsed.get("usernames", set())
        if emails and usernames:
            correlations.append({
                "type": "email_username",
                "emails": list(emails)[:10],
                "usernames": list(usernames)[:10],
                "confidence": 0.8,
            })

        # Email ↔ Phone
        phones = parsed.get("phones", set())
        if emails and phones:
            correlations.append({
                "type": "email_phone",
                "emails": list(emails)[:10],
                "phones": list(phones)[:10],
                "confidence": 0.7,
            })

        # Username ↔ Domain
        domains = parsed.get("domains", set())
        if usernames and domains:
            correlations.append({
                "type": "username_domain",
                "usernames": list(usernames)[:10],
                "domains": list(domains)[:10],
                "confidence": 0.6,
            })

        return {
            "correlations": correlations,
            "total_correlations": len(correlations),
            "aliases": list(usernames | emails | phones)[:20],
        }