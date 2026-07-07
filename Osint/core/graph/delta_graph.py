# core/graph/delta_graph.py
from __future__ import annotations

from typing import Set, List, Dict, Tuple
import networkx as nx
from core.base.storage import Storage
from core.graph.graph_builder import GraphBuilder

class DeltaGraph:
    """Bandingkan dua graf dari timestamp berbeda."""

    def __init__(self, storage: Storage):
        self.storage = storage
        self.builder = GraphBuilder(storage)

    def compare_timestamps(self, username: str, ts1: str, ts2: str) -> Dict:
        """
        Bangun graf dari dua snapshot, bandingkan node dan edge.
        """
        # Ambil data scan pada masing-masing timestamp
        results1 = self.storage.get_scan_snapshot(username, ts1)
        results2 = self.storage.get_scan_snapshot(username, ts2)

        # Bangun graf sementara
        g1 = self._build_graph_from_results(results1)
        g2 = self._build_graph_from_results(results2)

        nodes1 = set(g1.nodes())
        nodes2 = set(g2.nodes())
        edges1 = set(g1.edges())
        edges2 = set(g2.edges())

        new_nodes = nodes2 - nodes1
        removed_nodes = nodes1 - nodes2
        new_edges = edges2 - edges1
        removed_edges = edges1 - edges2

        return {
            "timestamp_older": ts1,
            "timestamp_newer": ts2,
            "new_nodes": list(new_nodes),
            "removed_nodes": list(removed_nodes),
            "new_edges": list(new_edges),
            "removed_edges": list(removed_edges),
        }

    def _build_graph_from_results(self, results: List) -> nx.Graph:
        """Bangun graf dari sekumpulan hasil scan."""
        g = nx.Graph()
        for r in results:
            g.add_node(r.username, type="unknown")
        # Tambahkan edge untuk hasil yang memiliki platform sama
        platform_map = {}
        for r in results:
            platform_map.setdefault(r.platform, []).append(r.username)
        for users in platform_map.values():
            for u1, u2 in __import__('itertools').combinations(users, 2):
                if u1 != u2:
                    g.add_edge(u1, u2)
        return g