# core/email/email_workflow.py
from __future__ import annotations

import os
import json
import csv
from typing import List, Dict, Any
from datetime import datetime

from rich.console import Console
from core.base.scan_result import ScanResult

console = Console()


class EmailWorkflow:
    """
    Orchestrates email scanning output: JSON, CSV detail, Markdown.
    Menghasilkan laporan terminal + file di results/email/<target>/
    """

    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = base_dir
        self.output_root = os.path.join(base_dir, "results", "email")

    def run(self, target: str, results: List[ScanResult]) -> str:
        """
        Jalankan ekspor tambahan (JSON, CSV detail, Markdown).
        Mengembalikan direktori output.
        """
        # Direktori output
        safe_target = self._sanitize_name(target)
        user_dir = os.path.join(self.output_root, safe_target)
        os.makedirs(user_dir, exist_ok=True)

        # Ekspor
        self._export_json(results, user_dir)
        self._export_csv(results, user_dir)
        self._export_markdown(target, results, user_dir)

        console.print(f"[green]Additional exports saved to {user_dir}[/green]")
        return user_dir

    @staticmethod
    def _sanitize_name(name: str) -> str:
        import re
        # Untuk email, karakter @ dan . diperbolehkan, tapi karakter ilegal lainnya diganti
        name = name.replace("@", "_at_")
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def _export_json(self, results: List[ScanResult], user_dir: str) -> None:
        data = [r.to_dict() for r in results]
        path = os.path.join(user_dir, "email_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _export_csv(self, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "email_details.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Platform", "Status", "Field", "Value"])
            for r in results:
                extra = r.extra or {}
                for field, value in extra.items():
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value)
                    writer.writerow([r.platform, r.status, field, value])
                # Data dasar
                writer.writerow([r.platform, r.status, "username", r.username])
                writer.writerow([r.platform, r.status, "url", r.url])
                writer.writerow([r.platform, r.status, "confidence", r.confidence])
                writer.writerow([r.platform, r.status, "intelligence_score", r.intelligence_score])

    def _export_markdown(self, target: str, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "email_report.md")
        md = f"# Email Intelligence Report\n\n**Target:** {target}\n\n"
        for r in results:
            md += f"## {r.platform}\n"
            md += f"- Status: {r.status}\n"
            md += f"- Confidence: {r.confidence:.2f}\n"
            md += f"- Intelligence Score: {r.intelligence_score:.1f}\n"
            extra = r.extra or {}
            for key, val in extra.items():
                if isinstance(val, (list, dict)):
                    val = json.dumps(val, indent=2)
                md += f"- {key}: {val}\n"
            md += "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)