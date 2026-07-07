# core/graph/graph_visualizer.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any
import networkx as nx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class GraphVisualizer:
    """Tampilkan graf di terminal dan ekspor ke GEXF/JSON."""

    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def show_centrality_table(self, top_n: int = 10):
        """Tampilkan tabel sentralitas."""
        from core.graph.graph_builder import GraphBuilder
        builder = GraphBuilder(None)  # dummy, kita pakai graph langsung
        builder.graph = self.graph
        centrality = builder.get_centrality(top_n)
        if not centrality:
            console.print("[yellow]Graf masih kosong[/yellow]")
            return

        table = Table(title="Top Centrality Nodes", border_style="bright_magenta")
        table.add_column("Rank", style="cyan")
        table.add_column("Identifier", style="white")
        table.add_column("Centrality", style="green")
        for i, (node, score) in enumerate(centrality, 1):
            table.add_row(str(i), node, f"{score:.4f}")
        console.print(table)

    def show_components_summary(self):
        """Tampilkan ringkasan komponen terhubung."""
        from core.graph.graph_builder import GraphBuilder
        builder = GraphBuilder(None)
        builder.graph = self.graph
        components = builder.get_connected_components()
        if not components:
            console.print("[yellow]Tidak ada komponen[/yellow]")
            return

        console.print(Panel(f"Graf memiliki {len(components)} komponen terhubung", border_style="cyan"))
        # Tampilkan komponen terbesar
        largest = max(components, key=len)
        table = Table(title=f"Komponen Terbesar ({len(largest)} node)", border_style="cyan")
        table.add_column("Node", style="white")
        for node in sorted(largest)[:20]:  # batasi tampilan
            table.add_row(node)
        if len(largest) > 20:
            table.add_row(f"... dan {len(largest)-20} lainnya")
        console.print(table)

    def export_gexf(self, output_path: str) -> str:
        """Ekspor graf ke format GEXF (Gephi)."""
        nx.write_gexf(self.graph, output_path)
        return output_path

    def export_json(self, output_path: str) -> str:
        """Ekspor struktur graf ke JSON."""
        data = {
            "nodes": list(self.graph.nodes(data=True)),
            "edges": list(self.graph.edges())
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_path

    def show_graph_ascii(self):
        """Tampilkan graf ASCII sederhana (untuk graf kecil)."""
        if len(self.graph) > 50:
            console.print("[yellow]Graf terlalu besar untuk tampilan ASCII (>50 node)[/yellow]")
            return
        try:
            import asciinet
            console.print(asciinet.graph_to_ascii(self.graph))
        except ImportError:
            console.print("[yellow]Package 'asciinet' tidak terinstal. Install untuk ASCII graph.[/yellow]")