# core/document/analyzers/metadata_analyzer.py
from __future__ import annotations

from typing import Dict, Any


class MetadataAnalyzer:
    """Analisis metadata yang diekstrak."""

    @staticmethod
    def analyze(metadata: Dict[str, Any]) -> Dict[str, Any]:
        findings = {
            "has_author": False,
            "has_creator": False,
            "has_company": False,
            "has_software": False,
            "suspicious_metadata": [],
        }

        # Cek author/creator
        for key in ["author", "creator", "last_modified_by"]:
            val = metadata.get(key)
            if val and str(val).strip():
                findings["has_author"] = True
                findings["has_creator"] = True
                break

        # Cek company/software
        for key in ["company", "producer", "application"]:
            val = metadata.get(key)
            if val and str(val).strip():
                findings["has_company"] = True
                findings["has_software"] = True
                break

        # Deteksi mencurigakan
        author = str(metadata.get("author", "")).lower()
        if any(w in author for w in ["user", "admin", "test", "default", "unknown"]):
            findings["suspicious_metadata"].append("Generic author name detected")

        return findings