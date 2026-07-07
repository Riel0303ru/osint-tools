# core/ai/ai_report_generator.py
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from utils.logger import Logger


class AIReportGenerator:
    """
    Generator laporan hasil analisis AI.
    Menyediakan ekspor ke berbagai format (JSON, Markdown, HTML, PDF placeholder)
    serta validasi input sebelum menyimpan.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    # ------------------------------------------------------------------
    # Ekspor JSON
    # ------------------------------------------------------------------
    def export_json(self, output_dir: Path, data: dict) -> bool:
        """
        Simpan data ke file JSON di output_dir.
        Mengembalikan True jika berhasil, False jika gagal.
        """
        if not data:
            self.logger.warning("Data untuk laporan JSON kosong, tidak mengekspor.")
            return False

        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "ai_analysis.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info(f"Laporan JSON disimpan di {path}")
            return True
        except Exception as e:
            self.logger.error(f"Gagal mengekspor JSON ke {path}: {e}")
            return False

    # ------------------------------------------------------------------
    # Ekspor Markdown
    # ------------------------------------------------------------------
    def export_markdown(self, output_dir: Path, analysis: dict) -> bool:
        """
        Buat laporan Markdown dari dictionary analysis.
        """
        if not analysis:
            self.logger.warning("Data analysis kosong, tidak mengekspor Markdown.")
            return False

        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "ai_report.md"

        try:
            md = self._build_markdown(analysis)
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)
            self.logger.info(f"Laporan Markdown disimpan di {path}")
            return True
        except Exception as e:
            self.logger.error(f"Gagal mengekspor Markdown ke {path}: {e}")
            return False

    def _build_markdown(self, analysis: Dict[str, Any]) -> str:
        """Bangun konten Markdown dari dictionary analysis."""
        lines = [
            "# OSINT AI Analysis Report",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Executive Summary",
            analysis.get("summary", "N/A"),
            "",
            "## Risk Assessment",
            f"- **Risk Level:** {analysis.get('risk_level', 'unknown').upper()}",
            f"- **Risk Score:** {analysis.get('risk_score', 0)}/100",
            f"- **Confidence Estimate:** {analysis.get('confidence_estimate', 0)}%",
            "",
            "## Correlations",
        ]
        correlations = analysis.get("correlations", [])
        if correlations:
            lines.extend(f"- {c}" for c in correlations)
        else:
            lines.append("None")
        lines.append("")

        lines.append("## Suspicious Findings")
        suspicious = analysis.get("suspicious_findings", [])
        if suspicious:
            lines.extend(f"- {f}" for f in suspicious)
        else:
            lines.append("None")
        lines.append("")

        lines.append("## Insights")
        insights = analysis.get("insights", [])
        if insights:
            lines.extend(f"- {i}" for i in insights)
        else:
            lines.append("None")
        lines.append("")

        lines.append("## Narrative")
        lines.append(analysis.get("narrative", "N/A"))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Ekspor HTML (sederhana)
    # ------------------------------------------------------------------
    def export_html(self, output_dir: Path, analysis: dict) -> bool:
        """Buat laporan HTML minimal dari analysis."""
        if not analysis:
            self.logger.warning("Data analysis kosong, tidak mengekspor HTML.")
            return False

        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "ai_report.html"

        try:
            html = self._build_html(analysis)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            self.logger.info(f"Laporan HTML disimpan di {path}")
            return True
        except Exception as e:
            self.logger.error(f"Gagal mengekspor HTML ke {path}: {e}")
            return False

    def _build_html(self, analysis: Dict[str, Any]) -> str:
        """Bangun konten HTML sederhana."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OSINT AI Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        .section {{ margin-bottom: 30px; }}
        ul {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>OSINT AI Analysis Report</h1>
    <p><strong>Generated:</strong> {datetime.now().isoformat()}</p>

    <div class="section">
        <h2>Executive Summary</h2>
        <p>{analysis.get('summary', 'N/A')}</p>
    </div>

    <div class="section">
        <h2>Risk Assessment</h2>
        <ul>
            <li><strong>Risk Level:</strong> {analysis.get('risk_level', 'unknown').upper()}</li>
            <li><strong>Risk Score:</strong> {analysis.get('risk_score', 0)}/100</li>
            <li><strong>Confidence Estimate:</strong> {analysis.get('confidence_estimate', 0)}%</li>
        </ul>
    </div>

    <div class="section">
        <h2>Correlations</h2>
        {'<ul>' + ''.join(f'<li>{c}</li>' for c in analysis.get('correlations', [])) + '</ul>' if analysis.get('correlations') else '<p>None</p>'}
    </div>

    <div class="section">
        <h2>Suspicious Findings</h2>
        {'<ul>' + ''.join(f'<li>{f}</li>' for f in analysis.get('suspicious_findings', [])) + '</ul>' if analysis.get('suspicious_findings') else '<p>None</p>'}
    </div>

    <div class="section">
        <h2>Insights</h2>
        {'<ul>' + ''.join(f'<li>{i}</li>' for i in analysis.get('insights', [])) + '</ul>' if analysis.get('insights') else '<p>None</p>'}
    </div>

    <div class="section">
        <h2>Narrative</h2>
        <p>{analysis.get('narrative', 'N/A')}</p>
    </div>
</body>
</html>"""

    # ------------------------------------------------------------------
    # Ekspor PDF (placeholder – butuh WeasyPrint atau ReportLab)
    # ------------------------------------------------------------------
    def export_pdf(self, output_dir: Path, analysis: dict) -> bool:
        """
        Placeholder untuk ekspor PDF.
        Jika WeasyPrint tersedia, akan menghasilkan PDF dari HTML.
        """
        try:
            from weasyprint import HTML
            html = self._build_html(analysis)
            output_dir.mkdir(parents=True, exist_ok=True)
            path = output_dir / "ai_report.pdf"
            HTML(string=html).write_pdf(path)
            self.logger.info(f"Laporan PDF disimpan di {path}")
            return True
        except ImportError:
            self.logger.warning("WeasyPrint tidak terinstal. PDF tidak dibuat.")
            return False
        except Exception as e:
            self.logger.error(f"Gagal menghasilkan PDF: {e}")
            return False