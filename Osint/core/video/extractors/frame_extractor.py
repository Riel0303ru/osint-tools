# core/video/extractors/frame_extractor.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.providers.ffmpeg_provider import FFmpegProvider
from utils.logger import Logger


class FrameExtractor:
    """Ekstrak frame dari video pada interval tertentu."""

    def __init__(self, base_dir: str = "Osint"):
        self.ffmpeg = FFmpegProvider(base_dir)
        self.logger = Logger(base_dir=base_dir)

    def extract(self, file_path: str, output_dir: str, interval: float = 2.0) -> ScanResult:
        """
        Ekstrak frame dari video setiap `interval` detik.
        Mengembalikan ScanResult dengan metadata frame.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        # Buat folder output
        os.makedirs(output_dir, exist_ok=True)

        # Ekstrak frame menggunakan FFmpeg
        frame_paths = self.ffmpeg.extract_frames(file_path, output_dir, interval)

        extraction_time = round(time.time() - start_time, 2)

        if not frame_paths:
            return ScanResult(
                platform="Frame Extraction",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={
                    "error": "Failed to extract frames",
                    "frames_found": 0,
                },
            )

        # Informasi frame
        frame_info = []
        for i, fpath in enumerate(frame_paths):
            frame_info.append({
                "index": i + 1,
                "path": fpath,
                "timestamp_seconds": round(i * interval, 1),
                "filename": os.path.basename(fpath),
            })

        return ScanResult(
            platform="Frame Extraction",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=1.0,
            extra={
                "frames_found": len(frame_paths),
                "extraction_interval": interval,
                "extraction_time_seconds": extraction_time,
                "frames": frame_info,
                "output_directory": output_dir,
            },
        )