# core/base/storage.py
import os
import json
import csv
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy import create_engine, Column, Integer, Text, Float, text, func, select
from sqlalchemy.orm import declarative_base, sessionmaker

from core.base.scan_result import ScanResult

Base = declarative_base()

class ScanResultModel(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False, index=True)
    platform = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    status_code = Column(Integer)
    url = Column(Text)
    confidence = Column(Float, default=1.0)
    intelligence_score = Column(Float, default=0.0)
    extra_json = Column(Text, default="{}")
    scan_timestamp = Column(Text, nullable=False, index=True)


class DictLikeRow:
    """Compatibility wrapper for SQLAlchemy Row objects to support dictionary-like access (row['col'])."""
    def __init__(self, mapping):
        self._mapping = mapping

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self._mapping.values())[key]
        return self._mapping[key]

    def get(self, key, default=None):
        return self._mapping.get(key, default)

    def keys(self):
        return self._mapping.keys()


class ResultWrapper:
    """Wrapper to make SQLAlchemy query results compatible with standard sqlite3 cursor outputs."""
    def __init__(self, result):
        self.result = result

    def fetchall(self) -> List[DictLikeRow]:
        return [DictLikeRow(row) for row in self.result.mappings().fetchall()]

    def fetchone(self) -> Optional[DictLikeRow]:
        row = self.result.mappings().fetchone()
        return DictLikeRow(row) if row else None


class Storage:
    """SQLAlchemy-based scan history, delta detection, and metadata persistence."""

    def __init__(self, db_path: Optional[str] = None):
        # 1. Load DATABASE_URL from env or parameter
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            # Fallback to local SQLite using db_path or default
            path = db_path or "Osint/data/osint_history.db"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            db_url = f"sqlite:///{path}"

        # Ensure correct prefix for SQLite
        if db_url.startswith("sqlite:///"):
            sqlite_path = db_url.replace("sqlite:///", "")
            if sqlite_path:
                os.makedirs(os.path.dirname(os.path.abspath(sqlite_path)), exist_ok=True)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Auto-create tables for SQLite ease of use, Alembic handles PostgreSQL production migrations
        if "sqlite" in db_url:
            Base.metadata.create_all(bind=self.engine)

    def execute(self, query: str, params: tuple = ()) -> ResultWrapper:
        """
        Legacy raw query execution compatibility layer.
        Converts SQLite (?) or PostgreSQL (%s) placeholders to SQLAlchemy named parameters.
        """
        param_dict = {}
        # Convert SQLite ? parameters to named SQLAlchemy parameters
        if "?" in query:
            parts = query.split("?")
            new_query = ""
            for i, part in enumerate(parts[:-1]):
                new_query += f"{part}:p{i}"
                param_dict[f"p{i}"] = params[i]
            new_query += parts[-1]
            query = new_query
        # Convert Postgres %s parameters to named SQLAlchemy parameters
        elif "%s" in query:
            parts = query.split("%s")
            new_query = ""
            for i, part in enumerate(parts[:-1]):
                new_query += f"{part}:p{i}"
                param_dict[f"p{i}"] = params[i]
            new_query += parts[-1]
            query = new_query

        session = self.SessionLocal()
        try:
            res = session.execute(text(query), param_dict or params)
            session.commit()
            return ResultWrapper(res)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _make_json_safe(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: Storage._make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Storage._make_json_safe(i) for i in obj]
        elif isinstance(obj, bool):
            return int(obj)
        elif isinstance(obj, (int, float, str, type(None))):
            return obj
        else:
            return str(obj)

    # =========================================================
    # SAVE
    # =========================================================

    def save_scan(self, username: str, results: List[ScanResult]) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        session = self.SessionLocal()
        try:
            for r in results:
                extra_safe = self._make_json_safe(r.extra) if r.extra else {}
                extra_json = json.dumps(extra_safe)
                
                model = ScanResultModel(
                    username=username,
                    platform=r.platform,
                    status=r.status,
                    status_code=r.status_code,
                    url=r.url,
                    confidence=r.confidence,
                    intelligence_score=r.intelligence_score,
                    extra_json=extra_json,
                    scan_timestamp=timestamp
                )
                session.add(model)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return timestamp

    # =========================================================
    # QUERY HISTORY
    # =========================================================

    def get_distinct_timestamps(self, username: str) -> List[str]:
        session = self.SessionLocal()
        try:
            stmt = (
                select(ScanResultModel.scan_timestamp)
                .where(ScanResultModel.username == username)
                .distinct()
                .order_by(ScanResultModel.scan_timestamp.desc())
            )
            rows = session.execute(stmt).scalars().all()
            return list(rows)
        finally:
            session.close()

    def get_scan_snapshot(self, username: str, timestamp: str) -> List[ScanResult]:
        session = self.SessionLocal()
        try:
            stmt = (
                select(ScanResultModel)
                .where(ScanResultModel.username == username)
                .where(ScanResultModel.scan_timestamp == timestamp)
            )
            models = session.execute(stmt).scalars().all()
            results = []
            for m in models:
                extra = json.loads(m.extra_json) if m.extra_json else {}
                results.append(ScanResult(
                    platform=m.platform,
                    username=m.username,
                    status=m.status,
                    status_code=m.status_code,
                    url=m.url,
                    confidence=m.confidence,
                    intelligence_score=m.intelligence_score,
                    extra=extra
                ))
            return results
        finally:
            session.close()

    def get_latest_scan(self, username: str) -> List[ScanResult]:
        timestamps = self.get_distinct_timestamps(username)
        if not timestamps:
            return []
        return self.get_scan_snapshot(username, timestamps[0])

    def get_paginated_history(self, page: int, limit: int) -> List[str]:
        """Gets paginated distinct list of target usernames scanned."""
        session = self.SessionLocal()
        try:
            stmt = (
                select(ScanResultModel.username)
                .distinct()
                .order_by(ScanResultModel.username)
                .limit(limit)
                .offset((page - 1) * limit)
            )
            rows = session.execute(stmt).scalars().all()
            return list(rows)
        finally:
            session.close()

    def get_total_history_count(self) -> int:
        """Gets total count of unique targets scanned."""
        session = self.SessionLocal()
        try:
            stmt = select(func.count(ScanResultModel.username.distinct()))
            return session.execute(stmt).scalar() or 0
        finally:
            session.close()

    # =========================================================
    # DELTA DETECTION
    # =========================================================

    def get_delta(self, username: str, new_results: List[ScanResult]) -> List[Dict[str, Any]]:
        old_results = self.get_latest_scan(username)
        old_map = {r.platform: r for r in old_results}
        new_map = {r.platform: r for r in new_results}

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
                    detail_parts.append(f"Status: {old_r.status} \u2192 {new_r.status}")
                if old_r.status_code != new_r.status_code:
                    detail_parts.append(f"Kode: {old_r.status_code} \u2192 {new_r.status_code}")
                if abs(old_r.confidence - new_r.confidence) > 0.001:
                    detail_parts.append(f"Confidence: {old_r.confidence:.2f} \u2192 {new_r.confidence:.2f}")
                if abs(old_r.intelligence_score - new_r.intelligence_score) > 0.001:
                    detail_parts.append(f"Intel: {old_r.intelligence_score:.2f} \u2192 {new_r.intelligence_score:.2f}")

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

        return changes

    def compare_scans(self, username: str, ts1: str, ts2: str) -> Dict[str, Any]:
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
                    detail_parts.append(f"Status: {old_r.status} \u2192 {new_r.status}")
                if old_r.status_code != new_r.status_code:
                    detail_parts.append(f"Kode: {old_r.status_code} \u2192 {new_r.status_code}")
                if abs(old_r.confidence - new_r.confidence) > 0.001:
                    detail_parts.append(f"Confidence: {old_r.confidence:.2f} \u2192 {new_r.confidence:.2f}")
                if abs(old_r.intelligence_score - new_r.intelligence_score) > 0.001:
                    detail_parts.append(f"Intel: {old_r.intelligence_score:.2f} \u2192 {new_r.intelligence_score:.2f}")

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