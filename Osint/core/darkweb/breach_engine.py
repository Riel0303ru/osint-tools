# core/darkweb/breach_engine.py
from __future__ import annotations

from typing import List, Dict


class BreachEngine:
    """Analisis breach dari hasil DeHashed."""

    @staticmethod
    def analyze(entries: List[Dict]) -> Dict:
        breaches = []
        databases_seen = set()

        for entry in entries:
            db_name = entry.get("database_name", "Unknown")
            if db_name not in databases_seen:
                databases_seen.add(db_name)
                breaches.append({
                    "database": db_name,
                    "fields": list(entry.keys()),
                    "has_password": "password" in entry and bool(entry.get("password")),
                    "has_hashed_password": "hashed_password" in entry and bool(entry.get("hashed_password")),
                    "has_email": "email" in entry and bool(entry.get("email")),
                    "has_username": "username" in entry and bool(entry.get("username")),
                    "has_phone": "phone" in entry and bool(entry.get("phone")),
                    "has_ip": "ip_address" in entry and bool(entry.get("ip_address")),
                })

        return {
            "total_breaches": len(breaches),
            "total_entries": len(entries),
            "plaintext_password_exposure": any(b["has_password"] for b in breaches),
            "breaches": breaches,
        }