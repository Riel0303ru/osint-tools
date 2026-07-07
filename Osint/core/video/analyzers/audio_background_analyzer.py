# core/video/analyzers/audio_background_analyzer.py
from __future__ import annotations

import os
import time
import numpy as np
from typing import List, Dict, Any
from core.base.scan_result import ScanResult
from utils.logger import Logger


class AudioBackgroundAnalyzer:
    """
    Menganalisis suara latar dari audio: deteksi traffic, sirene, keramaian,
    burung, konstruksi, dan musik. Menggunakan analisis spektral sederhana.
    """

    # Frekuensi khas suara latar (Hz)
    SOUND_SIGNATURES = {
        "traffic": (50, 500),       # frekuensi rendah, kontinu
        "siren": (800, 2000),       # frekuensi tinggi, berulang
        "crowd": (300, 1500),       # banyak frekuensi campur
        "birds": (2000, 8000),      # frekuensi sangat tinggi
        "construction": (200, 1500),# impulsif, lebar
        "music": (50, 4000),        # spektrum luas, harmonik
    }

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(self, audio_path: str, file_path: str) -> ScanResult:
        """
        Deteksi suara latar dari file audio WAV.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        if not audio_path or not os.path.isfile(audio_path):
            return ScanResult(
                platform="Audio Background Analysis",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "Audio file not available"},
            )

        try:
            import scipy.io.wavfile as wav
            from scipy.signal import spectrogram
            rate, data = wav.read(audio_path)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)  # mono

            # Spectrogram
            f, t, Sxx = spectrogram(data, fs=rate, nperseg=1024)

            detections = []
            for sound, (fmin, fmax) in self.SOUND_SIGNATURES.items():
                # Cari energi dalam rentang frekuensi
                freq_mask = (f >= fmin) & (f <= fmax)
                energy = np.mean(Sxx[freq_mask, :])
                if energy > 0.1 * np.max(Sxx):  # threshold relatif
                    confidence = min(energy / (np.max(Sxx) + 1e-9), 1.0)
                    detections.append({
                        "sound": sound,
                        "confidence": round(confidence, 2),
                    })

            analysis_time = round(time.time() - start_time, 2)
            return ScanResult(
                platform="Audio Background Analysis",
                username=filename,
                status="FOUND" if detections else "NOT_FOUND",
                status_code=200 if detections else 404,
                url=file_path,
                confidence=0.8 if detections else 0.3,
                extra={
                    "detections": detections,
                    "analysis_time_seconds": analysis_time,
                    "method": "Spectrogram energy analysis",
                },
            )

        except ImportError as e:
            return ScanResult(
                platform="Audio Background Analysis",
                username=filename,
                status="NOT_AVAILABLE",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": f"scipy not installed: {e}. Run: pip install scipy"},
            )
        except Exception as e:
            self.logger.error(f"Audio background analysis failed: {e}")
            return ScanResult(
                platform="Audio Background Analysis",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": str(e)},
            )