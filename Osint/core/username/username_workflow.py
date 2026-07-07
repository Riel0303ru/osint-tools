# core/username/username_workflow.py
from __future__ import annotations

import os
import json
import csv
from typing import List
from rich.console import Console
from core.base.scan_result import ScanResult

console = Console()


class UsernameWorkflow:
    """Ekspor hasil scan username ke JSON, CSV detail, Markdown, serta laporan korelasi identitas & persona."""

    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = base_dir
        self.output_root = os.path.join(base_dir, "results", "username")

    def run(self, target: str, results: List[ScanResult]) -> str:
        safe_target = self._sanitize_name(target)
        user_dir = os.path.join(self.output_root, safe_target)
        os.makedirs(user_dir, exist_ok=True)

        self._export_json(results, user_dir)
        self._export_csv(results, user_dir)
        self._export_markdown(target, results, user_dir)
        self._export_correlation(results, user_dir)   # ← tambahan
        self._export_persona(results, user_dir)       # ← tambahan

        console.print(f"[green]Username summary exported to {user_dir}[/green]")
        return user_dir

    @staticmethod
    def _sanitize_name(name: str) -> str:
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    def _export_json(self, results: List[ScanResult], user_dir: str) -> None:
        data = [r.to_dict() for r in results]
        path = os.path.join(user_dir, "username_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _export_csv(self, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "username_details.csv")
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
        path = os.path.join(user_dir, "username_report.md")
        md = f"# Username Intelligence Report\n\n**Target:** {target}\n\n"
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

    # ------------------------------------------------------------------
    # Ekspor khusus untuk hasil korelasi identitas & persona
    # ------------------------------------------------------------------
    def _export_correlation(self, results: List[ScanResult], user_dir: str) -> None:
        """Menyimpan linked_accounts.json jika ada hasil Identity Correlation."""
        for r in results:
            if r.platform == "Identity Correlation":
                linked = r.extra.get("linked_accounts", [])
                if linked:
                    path = os.path.join(user_dir, "linked_accounts.json")
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(linked, f, indent=4, ensure_ascii=False)
                break

    def _export_persona(self, results: List[ScanResult], user_dir: str) -> None:
        """Menyimpan persona_analysis.json jika ada hasil Persona Classification."""
        for r in results:
            if r.platform == "Persona Classification":
                persona_data = r.extra.get("persona", {})
                if persona_data:
                    path = os.path.join(user_dir, "persona_analysis.json")
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(persona_data, f, indent=4, ensure_ascii=False)
                break