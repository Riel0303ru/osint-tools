# core/video/video_workflow.py
from __future__ import annotations

import os
import json
import csv
from typing import List
from rich.console import Console
from core.base.scan_result import ScanResult
from core.video.video_report import VideoReport

console = Console()


class VideoWorkflow:
    """Ekspor hasil Video Intelligence – lengkap dengan laporan final."""

    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = base_dir
        self.output_root = os.path.join(base_dir, "results", "video")
        self.video_report = VideoReport(base_dir)

    def run(self, target: str, results: List[ScanResult]) -> str:
        """
        Jalankan workflow ekspor:
        1. Ekspor standar (JSON, CSV, Markdown)
        2. Hasilkan laporan final (JSON & Markdown) via VideoReport
        (Penyimpanan history sudah dilakukan oleh scan_manager melalui core/base/storage.py)
        """
        filename = os.path.basename(target)
        safe_target = self._sanitize_name(os.path.splitext(filename)[0])
        user_dir = os.path.join(self.output_root, safe_target)
        os.makedirs(user_dir, exist_ok=True)

        # 1. Ekspor standar
        self._export_json(results, user_dir)
        self._export_csv(results, user_dir)
        self._export_markdown(target, results, user_dir)

        # 2. Laporan final (JSON & Markdown) menggunakan VideoReport
        report_paths = self.video_report.generate(results, target, user_dir)
        console.print(f"[green]Final JSON report:[/green] {report_paths.get('json_report', 'N/A')}")
        console.print(f"[green]Final Markdown report:[/green] {report_paths.get('markdown_report', 'N/A')}")

        console.print(f"[bold green]Video workflow completed → {user_dir}[/bold green]")
        return user_dir

    @staticmethod
    def _sanitize_name(name: str) -> str:
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def _export_json(self, results: List[ScanResult], user_dir: str) -> None:
        data = [r.to_dict() for r in results]
        path = os.path.join(user_dir, "video_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _export_csv(self, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "video_details.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Platform", "Status", "Field", "Value"])
            for r in results:
                extra = r.extra or {}
                for field, value in extra.items():
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value)
                    writer.writerow([r.platform, r.status, field, value])
                writer.writerow([r.platform, r.status, "username", r.username])
                writer.writerow([r.platform, r.status, "url", r.url])
                writer.writerow([r.platform, r.status, "confidence", r.confidence])
                writer.writerow([r.platform, r.status, "intelligence_score", r.intelligence_score])

    def _export_markdown(self, target: str, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "video_report.md")
        md = f"# Video Intelligence Report\n\n**Target:** {target}\n\n"
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