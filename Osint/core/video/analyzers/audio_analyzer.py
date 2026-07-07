# core/video/analyzers/audio_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
from core.base.scan_result import ScanResult
from core.video.providers.whisper_provider import WhisperProvider
from utils.logger import Logger


class AudioAnalyzer:
    """
    Menganalisis file audio dari video: transkripsi, deteksi bahasa,
    dan ekstraksi potensi informasi penting dari ucapan.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.whisper = WhisperProvider(base_dir=base_dir, model_size="tiny")

    def analyze(self, audio_path: str, file_path: str) -> ScanResult:
        """
        Lakukan transkripsi audio dan ekstrak intelijen.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        if not audio_path or not os.path.isfile(audio_path):
            return ScanResult(
                platform="Audio Analysis",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "Audio file not available"},
            )

        # Transkripsi
        transcription = self.whisper.transcribe(audio_path)

        if "error" in transcription:
            return ScanResult(
                platform="Audio Analysis",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": transcription["error"]},
            )

        text = transcription.get("text", "")
        language = transcription.get("language", "")
        segments = transcription.get("segments", [])

        # Deteksi keyword penting (email, telepon, lokasi, dll.) menggunakan regex
        entities = self._extract_entities(text)

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Audio Analysis",
            username=filename,
            status="FOUND" if text else "NOT_FOUND",
            status_code=200 if text else 404,
            url=file_path,
            confidence=0.9 if text else 0.5,
            extra={
                "transcript": text,
                "language": language,
                "segments": segments[:50],  # batasi
                "entities": entities,
                "duration_seconds": segments[-1]["end"] if segments else 0,
                "analysis_time_seconds": analysis_time,
            },
        )

    @staticmethod
    def _extract_entities(text: str) -> Dict[str, List[str]]:
        """Sederhana: ekstrak email, telepon, URL dari transkrip."""
        import re
        email_re = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        phone_re = re.compile(r"\+?\d{7,15}")
        url_re = re.compile(r"https?://[^\s,;\"']+")

        return {
            "emails": list(set(email_re.findall(text)))[:20],
            "phones": list(set(phone_re.findall(text)))[:20],
            "urls": list(set(url_re.findall(text)))[:20],
        }