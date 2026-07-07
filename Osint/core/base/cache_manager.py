from __future__ import annotations

import json
import gzip
import hashlib
import threading

from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


@dataclass
class CacheEntry:

    key: str

    namespace: str

    created_at: str

    expires_at: str

    hit_count: int

    size_bytes: int

    compressed: bool

    data: Any

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        return cls(**data)


@dataclass
class CacheStats:

    hits: int = 0

    misses: int = 0

    writes: int = 0

    deletes: int = 0

    expired: int = 0

    memory_entries: int = 0

    disk_entries: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


class CacheManager:

    DEFAULT_NAMESPACES = [
        "username",
        "email",
        "phone",
        "domain",
        "ip",
        "image",
        "video",
        "company",
        "darkweb",
        "ai",
        "correlation"
    ]

    def __init__(
        self,
        base_dir: str = "Osint",
        cache_dir: str = "data/cache",
        compression_threshold: int = 10000
    ):

        self.base_dir = Path(base_dir)

        self.cache_root = self.base_dir / cache_dir

        self.compression_threshold = compression_threshold

        self.memory_cache: Dict[str, CacheEntry] = {}

        self.stats = CacheStats()

        self.lock = threading.RLock()

        self._create_structure()

    def _create_structure(self) -> None:

        self.cache_root.mkdir(
            parents=True,
            exist_ok=True
        )

        for namespace in self.DEFAULT_NAMESPACES:

            (
                self.cache_root /
                namespace
            ).mkdir(
                parents=True,
                exist_ok=True
            )

    def build_cache_key(
        self,
        namespace: str,
        key: str
    ) -> str:

        raw = f"{namespace}:{key}"

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    def _cache_file(
        self,
        namespace: str,
        key: str
    ) -> Path:

        hashed = self.build_cache_key(
            namespace,
            key
        )

        return (
            self.cache_root /
            namespace /
            f"{hashed}.json"
        )

    def _is_expired(
        self,
        entry: CacheEntry
    ) -> bool:

        return (
            datetime.utcnow()
            >
            datetime.fromisoformat(
                entry.expires_at
            )
        )

    def exists(
        self,
        namespace: str,
        key: str
    ) -> bool:

        return self.get(
            namespace,
            key
        ) is not None

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl_hours: int = 24
    ) -> bool:

        with self.lock:

            created = datetime.utcnow()

            expires = (
                created +
                timedelta(
                    hours=ttl_hours
                )
            )

            raw_json = json.dumps(
                value,
                default=str
            )

            raw_bytes = raw_json.encode()

            compressed = (
                len(raw_bytes)
                >
                self.compression_threshold
            )

            if compressed:

                payload = gzip.compress(
                    raw_bytes
                ).hex()

            else:

                payload = value

            entry = CacheEntry(
                key=key,
                namespace=namespace,
                created_at=created.isoformat(),
                expires_at=expires.isoformat(),
                hit_count=0,
                size_bytes=len(raw_bytes),
                compressed=compressed,
                data=payload
            )

            self.memory_cache[
                f"{namespace}:{key}"
            ] = entry

            path = self._cache_file(
                namespace,
                key
            )

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    entry.to_dict(),
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            self.stats.writes += 1
            self.stats.memory_entries = len(
                self.memory_cache
            )

            return True

    def get(
        self,
        namespace: str,
        key: str
    ) -> Optional[Any]:

        cache_key = f"{namespace}:{key}"

        with self.lock:

            if cache_key in self.memory_cache:

                entry = self.memory_cache[
                    cache_key
                ]

                if self._is_expired(entry):

                    self.stats.expired += 1

                    self.delete(
                        namespace,
                        key
                    )

                    return None

                entry.hit_count += 1

                self.stats.hits += 1

                return self._decode_entry(
                    entry
                )

            path = self._cache_file(
                namespace,
                key
            )

            if not path.exists():

                self.stats.misses += 1

                return None

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                entry = CacheEntry.from_dict(
                    data
                )

                if self._is_expired(entry):

                    self.stats.expired += 1

                    self.delete(
                        namespace,
                        key
                    )

                    return None

                entry.hit_count += 1

                self.memory_cache[
                    cache_key
                ] = entry

                self.stats.hits += 1

                return self._decode_entry(
                    entry
                )

            except Exception:

                self.stats.misses += 1

                return None

    def _decode_entry(
        self,
        entry: CacheEntry
    ) -> Any:

        if not entry.compressed:

            return entry.data

        try:

            compressed = bytes.fromhex(
                entry.data
            )

            decompressed = gzip.decompress(
                compressed
            )

            return json.loads(
                decompressed.decode()
            )

        except Exception:

            return None

    def delete(
        self,
        namespace: str,
        key: str
    ) -> bool:

        with self.lock:

            cache_key = f"{namespace}:{key}"

            self.memory_cache.pop(
                cache_key,
                None
            )

            path = self._cache_file(
                namespace,
                key
            )

            if path.exists():

                path.unlink()

            self.stats.deletes += 1

            return True

    def clear_namespace(
        self,
        namespace: str
    ) -> None:

        with self.lock:

            folder = (
                self.cache_root /
                namespace
            )

            if not folder.exists():
                return

            for file in folder.glob(
                "*.json"
            ):
                file.unlink()

            keys = [
                k
                for k in self.memory_cache
                if k.startswith(
                    f"{namespace}:"
                )
            ]

            for k in keys:
                self.memory_cache.pop(
                    k,
                    None
                )

    def cleanup_expired(
        self
    ) -> int:

        removed = 0

        with self.lock:

            for namespace in self.DEFAULT_NAMESPACES:

                folder = (
                    self.cache_root /
                    namespace
                )

                if not folder.exists():
                    continue

                for file in folder.glob(
                    "*.json"
                ):

                    try:

                        data = json.loads(
                            file.read_text(
                                encoding="utf-8"
                            )
                        )

                        entry = (
                            CacheEntry
                            .from_dict(data)
                        )

                        if self._is_expired(
                            entry
                        ):

                            file.unlink()

                            removed += 1

                    except Exception:

                        continue

        self.stats.expired += removed

        return removed

    def get_stats(
        self
    ) -> dict:

        disk_entries = 0

        for namespace in self.DEFAULT_NAMESPACES:

            folder = (
                self.cache_root /
                namespace
            )

            if folder.exists():

                disk_entries += len(
                    list(
                        folder.glob(
                            "*.json"
                        )
                    )
                )

        self.stats.disk_entries = (
            disk_entries
        )

        self.stats.memory_entries = (
            len(
                self.memory_cache
            )
        )

        return self.stats.to_dict()

    def export_manifest(
        self
    ) -> Dict[str, Any]:

        manifest = {}

        for namespace in self.DEFAULT_NAMESPACES:

            folder = (
                self.cache_root /
                namespace
            )

            if not folder.exists():
                continue

            manifest[namespace] = []

            for file in folder.glob(
                "*.json"
            ):

                manifest[
                    namespace
                ].append(
                    file.name
                )

        return manifest

    def warmup(
        self,
        limit_per_namespace: int = 50
    ) -> None:

        with self.lock:

            for namespace in self.DEFAULT_NAMESPACES:

                folder = (
                    self.cache_root /
                    namespace
                )

                if not folder.exists():
                    continue

                loaded = 0

                for file in folder.glob(
                    "*.json"
                ):

                    if loaded >= limit_per_namespace:
                        break

                    try:

                        data = json.loads(
                            file.read_text(
                                encoding="utf-8"
                            )
                        )

                        entry = (
                            CacheEntry
                            .from_dict(data)
                        )

                        if self._is_expired(
                            entry
                        ):
                            continue

                        self.memory_cache[
                            f"{namespace}:{entry.key}"
                        ] = entry

                        loaded += 1

                    except Exception:
                        continue