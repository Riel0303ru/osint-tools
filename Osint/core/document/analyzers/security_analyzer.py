# core/document/analyzers/security_analyzer.py
from __future__ import annotations

from typing import Dict, Any


class SecurityAnalyzer:
    """Analisis keamanan dokumen."""

    @staticmethod
    def analyze(file_path: str, extract_result: Dict[str, Any]) -> Dict[str, Any]:
        findings = []

        # Cek embedded files (PDF)
        if extract_result.get("embedded_files"):
            findings.append({
                "type": "EMBEDDED_FILES",
                "severity": "MEDIUM",
                "details": f"Found {len(extract_result['embedded_files'])} embedded file(s): {extract_result['embedded_files']}",
            })

        # Cek banyak link eksternal
        links = extract_result.get("links", [])
        if len(links) > 20:
            findings.append({
                "type": "MANY_EXTERNAL_LINKS",
                "severity": "LOW",
                "details": f"Document contains {len(links)} external links",
            })

        # Cek error saat ekstraksi
        if "error" in extract_result:
            findings.append({
                "type": "EXTRACTION_ERROR",
                "severity": "HIGH",
                "details": extract_result["error"],
            })

        return {
            "security_findings": findings,
            "total_findings": len(findings),
            "risk_level": (
                "HIGH" if any(f["severity"] == "HIGH" for f in findings)
                else "MEDIUM" if any(f["severity"] == "MEDIUM" for f in findings)
                else "LOW" if findings
                else "NONE"
            ),
        }