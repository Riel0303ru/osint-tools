# core/video/extractors/thumbnail_generator.py
from __future__ import annotations

import os
import subprocess
import time
from typing import Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class ThumbnailGenerator:
    """
    Menghasilkan thumbnail dari video.
    Mengambil frame pada timestamp tertentu sebagai representasi visual.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def generate(self, file_path: str, output_dir: str, timestamp: str = "00:00:05") -> ScanResult:
        """
        Generate thumbnail dari video pada timestamp yang diberikan.
        Default: 5 detik pertama.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(filename)[0]
        thumb_path = os.path.join(output_dir, f"{base_name}_thumbnail.jpg")

        cmd = [
            "ffmpeg",
            "-ss", timestamp,
            "-i", file_path,
            "-frames:v", "1",
            "-q:v", "2",
            "-y",
            thumb_path,
        ]

        success = False
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and os.path.isfile(thumb_path):
                success = True
        except Exception as e:
            self.logger.warning(f"Thumbnail generation failed: {e}")

        generation_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Thumbnail",
            username=filename,
            status="FOUND" if success else "ERROR",
            status_code=200 if success else 0,
            url=file_path,
            confidence=1.0 if success else 0.0,
            extra={
                "thumbnail_path": thumb_path if success else None,
                "timestamp_used": timestamp,
                "generation_time_seconds": generation_time,
            },
        )