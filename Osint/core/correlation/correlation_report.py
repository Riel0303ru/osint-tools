# core/correlation/correlation_report.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List


class CorrelationReport:
    """Generate laporan korelasi dalam berbagai format."""

    @staticmethod
    def export_all(output_dir: Path, relationships: List[Dict], clusters: List[Dict], graph: Dict) -> None:
        """Ekspor semua laporan ke folder output."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. correlation_report.json
        with open(output_dir / "correlation_report.json", "w", encoding="utf-8") as f:
            json.dump({"relationships": relationships, "clusters": clusters, "graph": graph}, f, indent=4)

        # 2. identity_graph.json
        with open(output_dir / "identity_graph.json", "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=4)

        # 3. clusters.json
        with open(output_dir / "clusters.json", "w", encoding="utf-8") as f:
            json.dump(clusters, f, indent=4)

        # 4. relationships.csv
        import csv
        with open(output_dir / "relationships.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Source Platform", "Source Entity", "Target Platform", "Target Entity",
                             "Confidence Score", "Confidence Level", "Matches", "Factors"])
            for r in relationships:
                writer.writerow([
                    r["source_platform"], r["source_entity"],
                    r["target_platform"], r["target_entity"],
                    r["confidence_score"], r["confidence_level"],
                    "; ".join(r["matches"]), "; ".join(r["factors"])
                ])

        # 5. intelligence_summary.md
        with open(output_dir / "intelligence_summary.md", "w", encoding="utf-8") as f:
            f.write(CorrelationReport._generate_markdown(relationships, clusters, graph))

    @staticmethod
    def _generate_markdown(relationships: List[Dict], clusters: List[Dict], graph: Dict) -> str:
        md = "# Cross‑Module Intelligence Summary\n\n"
        md += f"**Total Relationships Found:** {len(relationships)}\n"
        md += f"**Total Identity Clusters:** {len(clusters)}\n"
        md += f"**Graph Nodes:** {graph['total_nodes']} | **Edges:** {graph['total_edges']}\n\n"

        if clusters:
            md += "## Identity Clusters\n\n"
            for i, cluster in enumerate(clusters[:10], 1):
                md += f"### Cluster {i} (Confidence: {cluster['confidence_level']}, Score: {cluster['average_confidence']:.2f})\n"
                md += f"**Members:** {', '.join(cluster['members'][:10])}\n\n"

        if relationships:
            md += "## Top Relationships (by Confidence)\n\n"
            md += "| Source | Target | Confidence | Level |\n"
            md += "|--------|--------|------------|-------|\n"
            for r in relationships[:20]:
                md += f"| {r['source_platform']}:{r['source_entity']} | {r['target_platform']}:{r['target_entity']} | {r['confidence_score']:.2f} | {r['confidence_level']} |\n"

        return md