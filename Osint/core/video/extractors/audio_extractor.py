# core/video/extractors/audio_extractor.py
from __future__ import annotations

import os
import time
from typing import Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.providers.ffmpeg_provider import FFmpegProvider
from utils.logger import Logger


class AudioExtractor:
    """Ekstrak audio dari video dan siapkan untuk transkripsi."""

    def __init__(self, base_dir: str = "Osint"):
        self.ffmpeg = FFmpegProvider(base_dir)
        self.logger = Logger(base_dir=base_dir)

    def extract(self, file_path: str, output_dir: str) -> ScanResult:
        """
        Ekstrak audio dari video ke file WAV.
        Mengembalikan ScanResult dengan path audio.
        """
        filename = os.path.basename(file_path)
        os.makedirs(output_dir, exist_ok=True)

        # Nama output
        base_name = os.path.splitext(filename)[0]
        audio_path = os.path.join(output_dir, f"{base_name}_audio.wav")

        start_time = time.time()

        # Ekstrak audio
        success = self.ffmpeg.extract_audio(file_path, audio_path)
        extraction_time = round(time.time() - start_time, 2)

        if not success:
            return ScanResult(
                platform="Audio Extraction",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={
                    "error": "Failed to extract audio",
                    "audio_path": audio_path,
                },
            )

        # Cek ukuran file audio
        audio_size = os.path.getsize(audio_path) if os.path.isfile(audio_path) else 0

        return ScanResult(
            platform="Audio Extraction",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=1.0,
            extra={
                "audio_path": audio_path,
                "audio_size_bytes": audio_size,
                "audio_format": "WAV (16kHz, mono)",
                "extraction_time_seconds": extraction_time,
            },
        )