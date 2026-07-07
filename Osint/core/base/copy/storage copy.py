# core/base/storage.py
import sqlite3
import json
import os
import csv
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult


class Storage:
    """SQLite-based scan history, delta detection, and metadata persistence."""

    def __init__(self, db_path: str = "data/osint_history.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    status TEXT NOT NULL,
                    status_code INTEGER,
                    url TEXT,
                    confidence REAL DEFAULT 1.0,
                    intelligence_score REAL DEFAULT 0.0,
                    extra_json TEXT DEFAULT '{}',
                    scan_timestamp TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_username_platform
                ON scan_results(username, platform)
            """)
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_username_timestamp
                ON scan_results(username, scan_timestamp)
            """)

    # =========================================================
    # HELPERS
    # =========================================================
    @staticmethod
    def _make_json_safe(obj: Any) -> Any:
        """
        Secara rekursif mengonversi objek menjadi JSON-safe.
        Boolean diubah menjadi integer (0/1), objek lain yang tidak
        bisa di-serialisasi diubah menjadi string.
        """
        if isinstance(obj, dict):
            return {k: Storage._make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Storage._make_json_safe(i) for i in obj]
        elif isinstance(obj, bool):
            return int(obj)          # True -> 1, False -> 0
        elif isinstance(obj, (int, float, str, type(None))):
            return obj
        else:
            return str(obj)

    # =========================================================
    # SAVE
    # =========================================================

    def save_scan(self, username: str, results: List[ScanResult]) -> str:
        """
        Simpan seluruh hasil scan dalam satu transaksi dengan timestamp UTC.
        Mengembalikan timestamp yang digunakan.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        with self.conn:
            for r in results:
                # Sanitasi extra agar selalu JSON‑serializable
                extra_safe = self._make_json_safe(r.extra) if r.extra else {}
                extra_json = json.dumps(extra_safe)
                self.conn.execute(
                    """INSERT INTO scan_results
                       (username, platform, status, status_code, url, confidence,
                        intelligence_score, extra_json, scan_timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (username,
                     r.platform,
                     r.status,
                     r.status_code,
                     r.url,
                     r.confidence,
                     r.intelligence_score,
                     extra_json,
                     timestamp)
                )
        return timestamp

    # =========================================================
    # QUERY HISTORY
    # =========================================================

    def get_distinct_timestamps(self, username: str) -> List[str]:
        """Daftar timestamp scan yang ada untuk seorang pengguna (terbaru dulu)."""
        cur = self.conn.execute(
            "SELECT DISTINCT scan_timestamp FROM scan_results "
            "WHERE username = ? ORDER BY scan_timestamp DESC",
            (username,)
        )
        return [row["scan_timestamp"] for row in cur.fetchall()]

    def get_scan_snapshot(self, username: str, timestamp: str) -> List[ScanResult]:
        """Ambil semua hasil scan pada timestamp tertentu."""
        cur = self.conn.execute(
            "SELECT * FROM scan_results WHERE username = ? AND scan_timestamp = ?",
            (username, timestamp)
        )
        results = []
        for row in cur.fetchall():
            extra = json.loads(row["extra_json"]) if row["extra_json"] else {}
            results.append(ScanResult(
                platform=row["platform"],
                username=row["username"],
                status=row["status"],
                status_code=row["status_code"],
                url=row["url"],
                confidence=row["confidence"],
                intelligence_score=row["intelligence_score"],
                extra=extra
            ))
        return results

    def get_latest_scan(self, username: str) -> List[ScanResult]:
        timestamps = self.get_distinct_timestamps(username)
        if not timestamps:
            return []
        return self.get_scan_snapshot(username, timestamps[0])

    # =========================================================
    # DELTA DETECTION
    # =========================================================

    def compare_scans(self, username: str, ts1: str, ts2: str) -> Dict[str, Any]:
        """
        Bandingkan dua snapshot (ts1 = older, ts2 = newer).
        Mengembalikan dict dengan daftar perubahan (NEW, LOST, UPDATED).
        """
        old = self.get_scan_snapshot(username, ts1)
        new = self.get_scan_snapshot(username, ts2)

        old_map = {r.platform: r for r in old}
        new_map = {r.platform: r for r in new}

        changes = []
        all_platforms = set(list(old_map.keys()) + list(new_map.keys()))

        for platform in sorted(all_platforms):
            old_r = old_map.get(platform)
            new_r = new_map.get(platform)

            if old_r is None and new_r is not None:
                changes.append({
                    "type": "NEW",
                    "platform": platform,
                    "details": f"Akun baru: {new_r.url} (status={new_r.status})"
                })
            elif old_r is not None and new_r is None:
                changes.append({
                    "type": "LOST",
                    "platform": platform,
                    "details": f"Akun hilang: {old_r.url} sebelumnya status={old_r.status}"
                })
            else:
                detail_parts = []
                if old_r.status != new_r.status:
                    detail_parts.append(f"Status: {old_r.status} → {new_r.status}")
                if old_r.status_code != new_r.status_code:
                    detail_parts.append(f"Kode: {old_r.status_code} → {new_r.status_code}")
                if abs(old_r.confidence - new_r.confidence) > 0.001:
                    detail_parts.append(f"Confidence: {old_r.confidence:.2f} → {new_r.confidence:.2f}")
                if abs(old_r.intelligence_score - new_r.intelligence_score) > 0.001:
                    detail_parts.append(f"Intel: {old_r.intelligence_score:.2f} → {new_r.intelligence_score:.2f}")

                # Deep diff pada extra
                old_extra = old_r.extra or {}
                new_extra = new_r.extra or {}
                if old_extra != new_extra:
                    changed_keys = []
                    for k in set(list(old_extra.keys()) + list(new_extra.keys())):
                        if old_extra.get(k) != new_extra.get(k):
                            changed_keys.append(k)
                    if changed_keys:
                        detail_parts.append(f"Metadata berubah: {', '.join(changed_keys)}")

                if detail_parts:
                    changes.append({
                        "type": "UPDATED",
                        "platform": platform,
                        "details": "; ".join(detail_parts)
                    })

        return {
            "username": username,
            "older_timestamp": ts1,
            "newer_timestamp": ts2,
            "changes": changes
        }

    # =========================================================
    # EXPORT DELTA CSV
    # =========================================================

    def export_delta_csv(self, username: str, ts1: str, ts2: str, output_path: str) -> Dict:
        delta = self.compare_scans(username, ts1, ts2)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tipe", "Platform", "Detail"])
            for ch in delta["changes"]:
                writer.writerow([ch["type"], ch["platform"], ch["details"]])
        return delta