# core/darkweb/leak_parser.py
from __future__ import annotations

from typing import Dict, List, Set


class LeakParser:
    """Parse hasil DeHashed menjadi entitas terstruktur."""

    @staticmethod
    def parse(entries: List[Dict]) -> Dict[str, Set[str]]:
        entities = {
            "emails": set(),
            "usernames": set(),
            "passwords": set(),
            "hashed_passwords": set(),
            "phones": set(),
            "ips": set(),
            "domains": set(),
            "names": set(),
            "addresses": set(),
            "companies": set(),
            "urls": set(),
            "social": set(),
            "databases": set(),
        }

        for entry in entries:
            for field in ["email", "username", "password", "hashed_password",
                         "phone", "ip_address", "name", "address", "company",
                         "url", "social"]:
                values = entry.get(field, [])
                if isinstance(values, list):
                    for v in values:
                        if v and isinstance(v, str):
                            entities[field + "s" if field != "ip_address" else "ips"].add(v.strip())

            db_name = entry.get("database_name")
            if db_name:
                entities["databases"].add(db_name)

        return {k: v for k, v in entities.items() if v}