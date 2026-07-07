# core/correlation/relationship_builder.py
from __future__ import annotations

from typing import List, Dict, Set
from core.correlation.entity_extractor import EntityExtractor
from core.correlation.normalizer import Normalizer
from core.correlation.match_engine import MatchEngine
from core.correlation.confidence_engine import ConfidenceEngine
from core.base.scan_result import ScanResult


class RelationshipBuilder:
    """Membangun hubungan antar hasil scan dari berbagai modul."""

    @staticmethod
    def build(results: List[ScanResult]) -> List[Dict]:
        """
        Membangun daftar hubungan (relationships) dari semua hasil scan.
        """
        relationships = []
        found = [r for r in results if r.status == "FOUND"]

        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                a = found[i]
                b = found[j]

                # Ekstrak entitas untuk kedua hasil
                entities_a = EntityExtractor.extract([a])
                entities_b = EntityExtractor.extract([b])

                # Normalisasi
                norm_a = Normalizer.normalize_all(entities_a)
                norm_b = Normalizer.normalize_all(entities_b)

                # Exact match
                matches = MatchEngine.exact_match(norm_a, norm_b)

                if matches:
                    # Hitung confidence
                    confidence = ConfidenceEngine.calculate(matches)

                    relationships.append({
                        "source_platform": a.platform,
                        "source_entity": a.username,
                        "target_platform": b.platform,
                        "target_entity": b.username,
                        "matches": matches,
                        "confidence_score": confidence["confidence_score"],
                        "confidence_level": confidence["confidence_level"],
                        "factors": confidence["factors"],
                    })

        return sorted(relationships, key=lambda x: x["confidence_score"], reverse=True)