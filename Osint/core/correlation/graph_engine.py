# core/correlation/graph_engine.py
from __future__ import annotations

from typing import List, Dict
import json


class GraphEngine:
    """Membangun graph nodes/edges dari relationships."""

    @staticmethod
    def build_graph(relationships: List[Dict]) -> Dict:
        """
        Membangun struktur graph dengan nodes dan edges.
        """
        nodes = {}
        edges = []

        for rel in relationships:
            source = rel["source_platform"] + ":" + rel["source_entity"]
            target = rel["target_platform"] + ":" + rel["target_entity"]

            if source not in nodes:
                nodes[source] = {"id": source, "platform": rel["source_platform"], "entity": rel["source_entity"]}
            if target not in nodes:
                nodes[target] = {"id": target, "platform": rel["target_platform"], "entity": rel["target_entity"]}

            edges.append({
                "source": source,
                "target": target,
                "confidence": rel["confidence_score"],
                "level": rel["confidence_level"],
                "factors": rel["factors"],
            })

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }