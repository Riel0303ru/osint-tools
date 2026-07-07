# core/phone/phone_workflow.py
from __future__ import annotations

import asyncio
import os
import json
import csv
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.phone.phone_scanner import PhoneScanner
from core.base.scan_result import ScanResult
from core.base.storage import Storage
from utils.export_manager import ExportManager

console = Console()


class PhoneWorkflow:
    """
    Orchestrates phone scanning, output formatting, history storage,
    and file export (JSON, CSV, Markdown).
    Menghasilkan laporan terminal + file di results/phone/<nomor>/
    dan menyimpan ke database history untuk delta detection.
    """

    def __init__(
        self,
        base_dir: str = "Osint",
        storage: Optional[Storage] = None,
        export_manager: Optional[ExportManager] = None,
    ):
        self.scanner = PhoneScanner(base_dir)
        self.base_dir = base_dir
        self.storage = storage
        self.export_manager = export_manager or ExportManager()
        self.output_root = os.path.join(base_dir, "results", "phone")

    async def run(self, phone: str) -> List[ScanResult]:
        """Jalankan scan, tampilkan laporan, simpan history, export file."""
        results = await self.scanner.scan_phone(phone)

        # Tampilkan laporan terminal
        self._display_report(results)

        # Simpan ke history
        if self.storage:
            timestamp = self.storage.save_scan(phone, results)
            console.print(f"[dim]Scan saved to history with timestamp {timestamp}[/dim]")

        # Export via ExportManager (CSV per platform + summary Excel)
        self.export_manager.export_and_display(
            results=results,
            title=f"Phone Intelligence: {phone}",
            username=phone,
            category="phone",
        )

        # Export tambahan: JSON, CSV detail, Markdown
        user_dir = self._get_user_dir(phone)
        self._export_json(phone, results, user_dir)
        self._export_csv(phone, results, user_dir)
        self._export_markdown(phone, results, user_dir)

        console.print(f"[green]Additional exports saved to {user_dir}[/green]")
        return results

    def _get_user_dir(self, phone: str) -> str:
        safe_phone = phone.replace("+", "").replace(" ", "_")
        path = os.path.join(self.output_root, safe_phone)
        os.makedirs(path, exist_ok=True)
        return path

    def _display_report(self, results: List[ScanResult]) -> None:
        console.print(Panel("[bold cyan]PHONE INTELLIGENCE REPORT[/bold cyan]", border_style="cyan"))
        table = Table(border_style="cyan")
        table.add_column("Platform", style="bold white")
        table.add_column("Status", style="cyan")
        table.add_column("Detail", style="white")

        for r in results:
            status_color = (
                "green" if r.status == "FOUND"
                else "red" if r.status == "ERROR"
                else "yellow"
            )
            status_text = f"[{status_color}]{r.status}[/{status_color}]"
            detail = self._extract_detail(r)
            table.add_row(r.platform, status_text, detail)

        console.print(table)

    def _extract_detail(self, result: ScanResult) -> str:
        extra = result.extra or {}
        if result.platform == "Phone Validation":
            if result.status == "FOUND":
                return f"{extra.get('international_format', '')} | {extra.get('carrier', '')} | {extra.get('location', '')}"
            return "Invalid"
        elif result.platform == "Numverify":
            if result.status == "FOUND":
                return f"Carrier: {extra.get('carrier', '-')} | Line: {extra.get('line_type', '-')}"
            return extra.get("message", "Not found")
        elif result.platform == "WhatsApp":
            return "Registered" if extra.get("registered") else "Not registered"
        elif result.platform == "Telegram":
            return "Registered" if extra.get("registered") else "Not registered"
        elif result.platform == "BreachDirectory":
            return f"Breaches: {extra.get('breaches_count', 0)}"
        elif result.platform == "AbstractAPI":
            if result.status == "FOUND":
                return f"Risk: {extra.get('risk', '-')}"
            return extra.get("message", "Not available")
        elif result.platform == "HaveIBeenPwned":
            if result.status == "FOUND":
                return f"Breaches: {extra.get('breaches_count', 0)}"
            return extra.get("message", "Not found")
        return "-"

    def _export_json(self, phone: str, results: List[ScanResult], user_dir: str) -> None:
        data = [r.to_dict() for r in results]
        path = os.path.join(user_dir, "phone_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _export_csv(self, phone: str, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "phone_details.csv")
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

    def _export_markdown(self, phone: str, results: List[ScanResult], user_dir: str) -> None:
        path = os.path.join(user_dir, "phone_report.md")
        md = f"# Phone Intelligence Report\n\n## Number\n{phone}\n\n"
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