# core/video/correlators/graph_correlator.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.models.video_entity import VideoEntity
from utils.logger import Logger


class GraphCorrelator:
    """
    Jembatan antara Video Intelligence dan Global Correlation Engine.
    Mengirimkan entitas video (email, telepon, domain, lokasi, dll.)
    ke core/correlation untuk membangun graph hubungan global.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.graph_engine = None
        self.entity_extractor = None
        self._init_correlation_modules()

    def _init_correlation_modules(self):
        """Inisialisasi koneksi ke core/correlation (jika tersedia)."""
        try:
            from core.correlation.graph_engine import GraphEngine
            from core.correlation.entity_extractor import EntityExtractor
            self.graph_engine = GraphEngine()
            self.entity_extractor = EntityExtractor()
            self.logger.info("Graph correlator terhubung ke core/correlation")
        except ImportError as e:
            self.logger.warning(f"core/correlation tidak tersedia: {e}")
            self.logger.warning("Graph correlator berjalan dalam mode standalone")
        except Exception as e:
            self.logger.error(f"Gagal inisialisasi correlation modules: {e}")

    def push_to_global_graph(
        self,
        entities: List[VideoEntity],
        identity_corr: Optional[ScanResult] = None,
        location_corr: Optional[ScanResult] = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Kirim semua entitas video ke graph engine global.
        Jika core/correlation tidak tersedia, kembalikan entitas dalam format
        yang kompatibel untuk korelasi manual.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        nodes_added = 0
        edges_added = 0
        graph_data = {"nodes": [], "edges": []}

        # 1. Tambahkan node untuk setiap entitas
        for entity in entities:
            node = {
                "id": f"video_{entity.entity_type}_{entity.value}",
                "type": entity.entity_type,
                "value": entity.value,
                "confidence": entity.confidence,
                "source": entity.source,
            }
            graph_data["nodes"].append(node)

            if self.graph_engine:
                try:
                    # Cek apakah metode add_node tersedia
                    if hasattr(self.graph_engine, "add_node"):
                        self.graph_engine.add_node(
                            node_id=node["id"],
                            node_type=entity.entity_type,
                            value=entity.value,
                            metadata={"confidence": entity.confidence, "source": "video_intelligence"},
                        )
                        nodes_added += 1
                    else:
                        self.logger.warning("graph_engine tidak memiliki metode add_node – node disimpan lokal")
                except Exception as e:
                    self.logger.warning(f"Gagal menambahkan node {node['id']}: {e}")

        # 2. Buat edge antara entitas terkait (dalam video yang sama)
        video_source_id = f"video_file_{filename}"
        graph_data["nodes"].append({
            "id": video_source_id,
            "type": "video_source",
            "value": filename,
            "confidence": 1.0,
            "source": "video_intelligence",
        })

        for node in graph_data["nodes"]:
            if node["id"] != video_source_id:
                edge = {
                    "source": video_source_id,
                    "target": node["id"],
                    "relationship": "CONTAINS",
                    "confidence": node.get("confidence", 0.5),
                }
                graph_data["edges"].append(edge)

                if self.graph_engine:
                    try:
                        if hasattr(self.graph_engine, "add_edge"):
                            self.graph_engine.add_edge(
                                source=video_source_id,
                                target=node["id"],
                                relationship="CONTAINS",
                                metadata={"confidence": node["confidence"]},
                            )
                            edges_added += 1
                        else:
                            self.logger.warning("graph_engine tidak memiliki metode add_edge – edge disimpan lokal")
                    except Exception as e:
                        self.logger.warning(f"Gagal menambahkan edge: {e}")

        # 3. Korelasikan dengan modul lain (via EntityExtractor)
        cross_module_links = []
        if self.entity_extractor:
            for entity in entities:
                try:
                    # Cek apakah metode find_related tersedia
                    if hasattr(self.entity_extractor, "find_related"):
                        matches = self.entity_extractor.find_related(
                            entity_type=entity.entity_type,
                            value=entity.value,
                        )
                        for match in matches:
                            cross_module_links.append({
                                "entity": entity.value,
                                "matched_module": match.get("module", "unknown"),
                                "matched_value": match.get("value", ""),
                                "confidence": match.get("confidence", 0.5),
                            })
                    else:
                        self.logger.info("entity_extractor tidak memiliki find_related – cross‑module links dilewati")
                except Exception as e:
                    self.logger.info(f"Entity extraction skipped for {entity.value}: {e}")  # ganti debug -> info

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Graph Correlation",
            username=filename,
            status="FOUND" if nodes_added > 0 or graph_data["nodes"] else "NOT_FOUND",
            status_code=200 if graph_data["nodes"] else 404,
            url=file_path,
            confidence=0.9 if nodes_added > 0 else 0.5,
            extra={
                "nodes_added": nodes_added,
                "edges_added": edges_added,
                "graph_data": graph_data if not self.graph_engine else None,
                "cross_module_links": cross_module_links,
                "total_cross_links": len(cross_module_links),
                "analysis_time_seconds": analysis_time,
                "correlation_engine_connected": self.graph_engine is not None,
            },
        )