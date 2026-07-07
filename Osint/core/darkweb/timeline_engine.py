# core/darkweb/timeline_engine.py
from __future__ import annotations

from typing import List, Dict


class TimelineEngine:
    """Membangun timeline breach."""

    @staticmethod
    def build(entries: List[Dict]) -> Dict:
        timeline = []
        databases_seen = {}

        for entry in entries:
            db_name = entry.get("database_name", "Unknown")
            if db_name not in databases_seen:
                databases_seen[db_name] = {
                    "database": db_name,
                    "count": 0,
                }
            databases_seen[db_name]["count"] += 1

        timeline = list(databases_seen.values())
        timeline.sort(key=lambda x: x["count"], reverse=True)

        return {
            "databases_found": len(timeline),
            "timeline": timeline,
            "most_exposed_in": timeline[0]["database"] if timeline else None,
        }