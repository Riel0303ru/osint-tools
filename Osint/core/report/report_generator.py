# core/report/report_generator.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import re
from typing import Optional

from core.report.data_collector import DataCollector
from core.report.html_template import HTMLTemplate
from core.report.pdf_converter import PDFConverter
from utils.logger import Logger


class ReportGenerator:
    """Orchestrator pembuatan laporan profesional – mendukung semua modul termasuk Video."""

    VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

    def __init__(self, storage, base_dir: str = "Osint"):
        self.storage = storage
        self.base_dir = Path(base_dir)
        self.results_base = self.base_dir / "results"
        self.collector = DataCollector(storage, str(self.results_base))
        self.template = HTMLTemplate()
        self.logger = Logger(base_dir=str(base_dir))

    def generate(self, target: str, output_dir: str = None) -> Path:
        """
        Hasilkan laporan lengkap (HTML + PDF) untuk target.
        - Jika target adalah file video, akan menyertakan analisis Video Intelligence
          dan AI Analysis (jika tersedia).
        """
        # 1. Tentukan modul dari target
        module = self._guess_module(target)

        # 2. Kumpulkan data
        data = self._collect_data(target, module)
        data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        data["module"] = module

        # 3. Build HTML
        html = self.template.build(data)

        # 4. Tentukan folder output
        safe_target = re.sub(r'[<>:"/\\|?*]', '_', target)[:100]
        if not output_dir:
            output_dir = self.base_dir / "results" / "reports" / safe_target
        else:
            output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 5. Simpan HTML
        html_path = output_dir / "osint_report.html"
        html_path.write_text(html, encoding="utf-8")

        # 6. Konversi ke PDF
        pdf_path = output_dir / "osint_report.pdf"
        success = PDFConverter.convert(html_path, pdf_path)
        if not success:
            self.logger.warning("Gagal mengonversi ke PDF – pastikan WeasyPrint terinstal.")

        self.logger.info(f"Laporan untuk '{target}' disimpan di {output_dir}")
        return output_dir

    def generate_video_report(self, video_path: str, results: list, output_dir: str = None) -> Path:
        """
        Pembuatan laporan khusus video, menerima list ScanResult langsung.
        Berguna jika Anda sudah memiliki hasil scan tanpa melalui storage.
        """
        safe_target = re.sub(r'[<>:"/\\|?*]', '_', Path(video_path).name)[:100]
        if not output_dir:
            output_dir = self.base_dir / "results" / "reports" / safe_target
        else:
            output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Format data dari hasil scan
        data = self._format_video_scan_data(video_path, results)
        data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        data["module"] = "video"

        html = self.template.build(data)
        html_path = output_dir / "osint_report.html"
        html_path.write_text(html, encoding="utf-8")

        pdf_path = output_dir / "osint_report.pdf"
        PDFConverter.convert(html_path, pdf_path)
        return output_dir

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _guess_module(self, target: str) -> str:
        """Identifikasi jenis target berdasarkan format atau ekstensi."""
        if "@" in target:
            return "email"
        if target.startswith("+"):
            return "phone"
        if "\\" in target or (target.startswith("http") and "://" in target):
            return "image"
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
            return "ip"
        # Deteksi video dari ekstensi
        if Path(target).suffix.lower() in self.VIDEO_EXTENSIONS:
            return "video"
        if "." in target and not target.startswith("C:"):
            return "domain"
        return "username"

    def _collect_data(self, target: str, module: str) -> dict:
        """Kumpulkan data untuk laporan dari storage + AI analysis."""
        data = {}

        # Data utama dari storage
        if module == "video":
            # Ambil snapshot scan terakhir untuk video
            snapshot = self.storage.get_latest_scan(target)
            if snapshot:
                data["video_scan"] = self._format_video_scan_data(target, snapshot)
                # Coba sertakan AI analysis dari hasil scan (jika ada)
                ai_result = next((r for r in snapshot if r.platform == "AI Analysis"), None)
                if ai_result and ai_result.status == "FOUND":
                    data["ai_analysis"] = ai_result.extra
                else:
                    # Cek juga di direktori ai/
                    ai_json = self.results_base / "ai" / re.sub(r'[<>:"/\\|?*]', '_', target) / "ai_analysis.json"
                    if ai_json.exists():
                        import json
                        data["ai_analysis"] = json.loads(ai_json.read_text(encoding="utf-8"))
            else:
                data["video_scan"] = {"error": "No scan history found for this video."}
        else:
            # Untuk modul lain, gunakan collector yang sudah ada
            data = self.collector.collect_all(target)

        # Tambahkan AI Analysis jika ada (untuk semua modul)
        if "ai_analysis" not in data:
            ai_json = self.results_base / "ai" / re.sub(r'[<>:"/\\|?*]', '_', target) / "ai_analysis.json"
            if ai_json.exists():
                import json
                data["ai_analysis"] = json.loads(ai_json.read_text(encoding="utf-8"))

        return data

    def _format_video_scan_data(self, video_path: str, results: list) -> dict:
        """
        Ubah list ScanResult menjadi struktur ringkasan untuk template HTML.
        """
        metadata = next((r for r in results if r.platform == "Video Metadata"), None)
        face = next((r for r in results if r.platform == "Face Detection"), None)
        obj = next((r for r in results if r.platform == "Object Detection"), None)
        geo = next((r for r in results if r.platform == "Geolocation Analysis"), None)
        risk = next((r for r in results if r.platform == "Risk Assessment"), None)
        ai = next((r for r in results if r.platform == "AI Analysis"), None)

        summary = {
            "file": Path(video_path).name,
            "duration_seconds": metadata.extra.get("duration_seconds", 0) if metadata else 0,
            "resolution": metadata.extra.get("video", {}).get("resolution", "?") if metadata else "?",
            "faces_found": face.extra.get("total_faces", 0) if face else 0,
            "objects_found": obj.extra.get("total_objects", 0) if obj else 0,
            "threat_level": risk.extra.get("threat_level", "N/A") if risk else "N/A",
            "threat_score": risk.extra.get("threat_score", 0) if risk else 0,
            "location_candidates": geo.extra.get("candidates", []) if geo else [],
            "ai_summary": ai.extra.get("executive_summary", "") if ai else "",
        }

        return {
            "summary": summary,
            "full_results": [r.to_dict() for r in results],
        }