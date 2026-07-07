# core/ip/ip_workflow.py
from __future__ import annotations

import os
import json
import csv
from typing import List
from rich.console import Console
from core.base.scan_result import ScanResult

console = Console()


class IPWorkflow:
    """Ekspor hasil pemindaian IP ke JSON, CSV detail, dan Markdown."""

    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = base_dir
        self.output_root = os.path.join(base_dir, "results", "ip")

    def run(self, target: str, results: List[ScanResult]) -> str:
        """
        Jalankan ekspor lengkap untuk hasil pemindaian IP.
        Mengembalikan path direktori output.
        """
        safe_target = self._sanitize_name(target)
        user_dir = os.path.join(self.output_root, safe_target)
        os.makedirs(user_dir, exist_ok=True)

        self._export_json(results, user_dir)
        self._export_csv(results, user_dir)
        self._export_markdown(target, results, user_dir)

        console.print(f"[green]IP intelligence summary exported to {user_dir}[/green]")
        return user_dir

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Bersihkan nama target dari karakter yang tidak valid untuk nama folder."""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def _export_json(self, results: List[ScanResult], user_dir: str) -> None:
        """Ekspor seluruh data mentah ke dalam file JSON."""
        data = [r.to_dict() for r in results]
        path = os.path.join(user_dir, "ip_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _export_csv(self, results: List[ScanResult], user_dir: str) -> None:
        """
        Ekspor detail per field dari setiap platform ke dalam file CSV.
        Setiap baris berisi: Platform, Status, Field, Value.
        """
        path = os.path.join(user_dir, "ip_details.csv")
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
        """Ekspor laporan naratif dalam format Markdown."""
        path = os.path.join(user_dir, "ip_report.md")
        md = f"# IP Intelligence Report\n\n**Target:** {target}\n\n"
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