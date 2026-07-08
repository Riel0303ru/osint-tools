# core/correlation/correlation_workflow.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from core.base.storage import Storage
from core.correlation.entity_extractor import EntityExtractor
from core.correlation.relationship_builder import RelationshipBuilder
from core.correlation.identity_cluster import IdentityCluster
from core.correlation.graph_engine import GraphEngine
from core.correlation.correlation_report import CorrelationReport


class CorrelationWorkflow:
    """Orchestrator utama korelasi lintas modul."""

    def __init__(self, storage: Storage, base_dir: str = "Osint"):
        self.storage = storage
        self.base_dir = Path(base_dir)

    def execute_all(self) -> Dict:
        """
        Jalankan korelasi penuh terhadap semua data yang tersimpan.
        Mengembalikan dictionary hasil korelasi.
        """
        # Ambil semua hasil scan dari semua target
        all_results = self._get_all_results()

        if not all_results:
            return {"error": "No scan data found in storage"}

        # Bangun relationships
        relationships = RelationshipBuilder.build(all_results)

        # Bangun klaster identitas
        clusters = IdentityCluster.build_clusters(all_results, relationships)

        # Bangun graph
        graph = GraphEngine.build_graph(relationships)

        # Ekspor laporan
        output_dir = self.base_dir / "results" / "correlation"
        CorrelationReport.export_all(output_dir, relationships, clusters, graph)

        return {
            "total_relationships": len(relationships),
            "total_clusters": len(clusters),
            "graph_nodes": graph["total_nodes"],
            "graph_edges": graph["total_edges"],
            "output_directory": str(output_dir),
            "relationships": relationships,
            "clusters": clusters,
            "graph": graph,
        }

    def _get_all_results(self) -> List:
        """Ambil semua hasil scan dari storage (semua target, timestamp terbaru per target)."""
        cur = self.storage.execute(
            "SELECT DISTINCT username FROM scan_results"
        )
        targets = [row["username"] for row in cur.fetchall()]

        all_results = []
        for target in targets:
            latest = self.storage.get_latest_scan(target)
            all_results.extend(latest)

        return all_results