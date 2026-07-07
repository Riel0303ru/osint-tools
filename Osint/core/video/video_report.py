# core/video/video_report.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any
from core.base.scan_result import ScanResult
from utils.logger import Logger


class VideoReport:
    """Membangun laporan akhir investigasi video."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def generate(self, results: List[ScanResult], file_path: str, output_dir: str) -> Dict[str, str]:
        """
        Hasilkan laporan JSON dan Markdown.
        Mengembalikan dict dengan path file.
        """
        filename = os.path.basename(file_path)
        safe_name = os.path.splitext(filename)[0]
        os.makedirs(output_dir, exist_ok=True)

        # Kumpulkan semua data
        report = {
            "video_file": filename,
            "analysis_summary": {},
            "stages": [],
        }
        for r in results:
            stage = {"platform": r.platform, "status": r.status, "confidence": r.confidence}
            # Ambil extra penting
            extra_clean = {}
            for k, v in (r.extra or {}).items():
                if isinstance(v, (str, int, float, bool, list, dict)):
                    extra_clean[k] = v
            stage["extra"] = extra_clean
            report["stages"].append(stage)

        # Simpan JSON
        json_path = os.path.join(output_dir, f"{safe_name}_final_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Simpan Markdown sederhana
        md = f"# Video Intelligence Report: {filename}\n\n"
        for s in report["stages"]:
            md += f"## {s['platform']}\n- Status: {s['status']}\n- Confidence: {s['confidence']}\n\n"
        md_path = os.path.join(output_dir, f"{safe_name}_final_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)

        return {"json_report": json_path, "markdown_report": md_path}