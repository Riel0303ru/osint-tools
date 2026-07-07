# core/correlation/identity_cluster.py
from __future__ import annotations

from typing import List, Dict
from core.base.scan_result import ScanResult


class IdentityCluster:
    """Mengelompokkan entitas terkait menjadi klaster identitas."""

    @staticmethod
    def build_clusters(results: List[ScanResult], relationships: List[Dict]) -> List[Dict]:
        graph = {}
        for rel in relationships:
            a = f"{rel.get('source_platform', '')}:{rel.get('source_entity', '')}"
            b = f"{rel.get('target_platform', '')}:{rel.get('target_entity', '')}"
            conf = rel.get("confidence_score", 0)
            graph.setdefault(a, []).append((b, conf))
            graph.setdefault(b, []).append((a, conf))

        visited = set()
        clusters = []
        for node in graph:
            if node not in visited:
                cluster_nodes = []
                stack = [node]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster_nodes.append(current)
                        for neighbor, _ in graph.get(current, []):
                            if neighbor not in visited:
                                stack.append(neighbor)
                if len(cluster_nodes) >= 2:
                    total_conf = 0
                    count = 0
                    for n in cluster_nodes:
                        for neighbor, conf in graph[n]:
                            if neighbor in cluster_nodes:
                                total_conf += conf
                                count += 1
                    avg_conf = total_conf / max(count, 1)
                    clusters.append({
                        "members": cluster_nodes,
                        "size": len(cluster_nodes),
                        "average_confidence": round(avg_conf, 3),
                        "confidence_level": (
                            "VERY_HIGH" if avg_conf >= 0.8
                            else "HIGH" if avg_conf >= 0.6
                            else "MEDIUM" if avg_conf >= 0.4
                            else "LOW"
                        )
                    })
        return sorted(clusters, key=lambda x: x["average_confidence"], reverse=True)