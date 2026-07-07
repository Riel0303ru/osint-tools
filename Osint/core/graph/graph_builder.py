# core/graph/graph_builder.py
from __future__ import annotations

import itertools
from typing import Dict, List, Set, Tuple, Optional
import networkx as nx
from core.base.storage import Storage

class GraphBuilder:
    """Membangun graf identitas dari data scan di storage."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.graph = nx.Graph()

    def build_graph(self, username_filter: Optional[str] = None) -> nx.Graph:
        """
        Membaca semua hasil scan (atau filter username) lalu membuat graf.
        Node: setiap identifier unik (username/email/domain/phone).
        Edge: dua node terhubung jika mereka muncul dalam hasil scan yang sama,
              atau memiliki atribut yang sama (misalnya platform yang sama, atau domain yang sama).
        """
        self.graph = nx.Graph()
        # Ambil semua identifier unik dari storage
        identifiers = self._get_all_identifiers(username_filter)

        # Tambahkan node
        for ident in identifiers:
            self.graph.add_node(ident, type=self._guess_type(ident))

        # Bangun edge berdasarkan koneksi antar hasil scan
        edges = self._find_connections(identifiers)
        self.graph.add_edges_from(edges)

        return self.graph

    def _get_all_identifiers(self, username_filter: Optional[str] = None) -> Set[str]:
        """Ambil semua username (identifier) unik dari storage."""
        query = "SELECT DISTINCT username FROM scan_results"
        if username_filter:
            query += " WHERE username LIKE ?"
            rows = self.storage.conn.execute(query, (f"%{username_filter}%",)).fetchall()
        else:
            rows = self.storage.conn.execute(query).fetchall()
        return {row["username"] for row in rows}

    def _guess_type(self, identifier: str) -> str:
        """Tebak tipe node berdasarkan format."""
        if "@" in identifier:
            return "email"
        elif identifier.startswith("+"):
            return "phone"
        elif "." in identifier and not identifier.startswith("@"):
            # Bisa domain atau username dengan titik, kita periksa lebih lanjut
            # Jika mengandung protokol atau TLD dikenal, anggap domain
            if any(identifier.endswith(tld) for tld in [".com", ".org", ".net", ".id", ".io", ".dev", ".co"]):
                return "domain"
            else:
                return "username"
        else:
            return "username"

    def _find_connections(self, identifiers: Set[str]) -> List[Tuple[str, str]]:
        """
        Cari koneksi antar identifier berdasarkan:
        - Mereka muncul bersama dalam satu scan (timestamp yang sama)
        - Mereka memiliki platform hasil scan yang sama (misal sama-sama punya akun GitHub)
        - Mereka memiliki domain yang sama (untuk email/domain)
        """
        edges = set()
        # 1) Koneksi dari timestamp yang sama (satu kali scan)
        rows = self.storage.conn.execute(
            "SELECT DISTINCT username, scan_timestamp FROM scan_results"
        ).fetchall()
        # Kelompokkan berdasarkan timestamp
        timestamp_map: Dict[str, List[str]] = {}
        for row in rows:
            ts = row["scan_timestamp"]
            timestamp_map.setdefault(ts, []).append(row["username"])

        for ts, users in timestamp_map.items():
            for u1, u2 in itertools.combinations(users, 2):
                if u1 != u2:
                    edges.add((u1, u2))

        # 2) Koneksi dari platform yang sama (antar identifier)
        platform_rows = self.storage.conn.execute(
            "SELECT DISTINCT platform, username FROM scan_results WHERE status='FOUND'"
        ).fetchall()
        platform_map: Dict[str, List[str]] = {}
        for row in platform_rows:
            platform_map.setdefault(row["platform"], []).append(row["username"])
        for users in platform_map.values():
            for u1, u2 in itertools.combinations(users, 2):
                if u1 != u2:
                    edges.add((u1, u2))

        # 3) Koneksi dari domain yang sama (email/domain)
        # Ambil extra yang mengandung domain
        # Ekstrak domain dari email atau field 'domain' di extra
        domain_map: Dict[str, List[str]] = {}
        all_rows = self.storage.conn.execute(
            "SELECT username, extra_json FROM scan_results WHERE extra_json != '{}'"
        ).fetchall()
        for row in all_rows:
            extra = __import__('json').loads(row["extra_json"])
            # Ambil domain dari berbagai field
            domain = None
            if "domain" in extra:
                domain = extra["domain"]
            elif "email" in extra:
                domain = extra["email"].split("@")[1] if "@" in extra["email"] else None
            elif "blog" in extra and "." in extra["blog"]:
                domain = extra["blog"]
            if domain:
                domain_map.setdefault(domain, []).append(row["username"])
        for users in domain_map.values():
            for u1, u2 in itertools.combinations(users, 2):
                if u1 != u2:
                    edges.add((u1, u2))

        return list(edges)

    def get_centrality(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Hitung degree centrality dan kembalikan top N."""
        if not self.graph:
            return []
        centrality = nx.degree_centrality(self.graph)
        sorted_items = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_n]

    def get_connected_components(self) -> List[Set[str]]:
        """Daftar komponen terhubung."""
        if not self.graph:
            return []
        return list(nx.connected_components(self.graph))