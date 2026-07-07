# core/video/extractors/subtitle_extractor.py
from __future__ import annotations

import os
import subprocess
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class SubtitleExtractor:
    """
    Mengekstrak subtitle internal dari file video (jika ada).
    Mendukung format SRT, ASS, VTT yang tertanam dalam video.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def extract(self, file_path: str, output_dir: str) -> ScanResult:
        """
        Ekstrak subtitle dari video dan simpan ke file SRT.
        Mengembalikan ScanResult dengan teks subtitle dan path file.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(filename)[0]
        output_srt = os.path.join(output_dir, f"{base_name}_subtitle.srt")

        # Gunakan ffmpeg untuk mengekstrak subtitle
        cmd = [
            "ffmpeg",
            "-i", file_path,
            "-map", "0:s:0?",  # ambil stream subtitle pertama jika ada
            "-c:s", "srt",
            "-y",
            output_srt,
        ]

        subtitle_text = ""
        subtitle_segments = []

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.isfile(output_srt):
                # Baca dan parse SRT
                subtitle_text, subtitle_segments = self._parse_srt(output_srt)
        except FileNotFoundError:
            self.logger.warning("FFmpeg not found – subtitle extraction skipped")
        except Exception as e:
            self.logger.warning(f"Subtitle extraction failed: {e}")

        extraction_time = round(time.time() - start_time, 2)
        has_subtitle = bool(subtitle_text)

        return ScanResult(
            platform="Subtitle Extraction",
            username=filename,
            status="FOUND" if has_subtitle else "NOT_FOUND",
            status_code=200 if has_subtitle else 404,
            url=file_path,
            confidence=1.0 if has_subtitle else 0.0,
            extra={
                "subtitle_text": subtitle_text[:5000],  # batasi 5k karakter
                "subtitle_segments": subtitle_segments[:50],  # 50 segmen pertama
                "subtitle_file": output_srt if has_subtitle else None,
                "extraction_time_seconds": extraction_time,
            },
        )

    @staticmethod
    def _parse_srt(srt_path: str) -> tuple:
        """
        Parse file SRT menjadi teks lengkap dan list segmen.
        Mengembalikan (full_text, segments).
        """
        import re
        with open(srt_path, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()

        # Pola: nomor urut, timestamp, teks, baris kosong
        pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})\n(.+?)(?=\n\n|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)

        segments = []
        full_text = []
        for idx, start, end, text in matches:
            text_clean = text.replace("\n", " ").strip()
            segments.append({
                "index": int(idx),
                "start": start,
                "end": end,
                "text": text_clean,
            })
            full_text.append(text_clean)

        return " ".join(full_text), segments