# core/video/analyzers/language_analyzer.py
from __future__ import annotations

import os
import time
from typing import Dict, Any, List, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class LanguageAnalyzer:
    """
    Mendeteksi bahasa dari teks OCR dan transkrip audio.
    Menggunakan langdetect untuk analisis cepat, dengan aturan
    konsolidasi yang lebih hati‑hati untuk menghindari overconfidence.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.detector = None
        self._init_detector()

    def _init_detector(self):
        """Inisialisasi detektor bahasa."""
        try:
            from langdetect import DetectorFactory
            DetectorFactory.seed = 42  # konsisten
            self.detector = True
            self.logger.info("langdetect initialized")
        except ImportError:
            self.logger.warning("langdetect not installed. Run: pip install langdetect")
            self.detector = False

    def analyze(
        self,
        ocr_text: Optional[str] = None,
        audio_transcript: Optional[str] = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Deteksi bahasa dari teks OCR dan/atau transkrip audio.
        Aturan:
        - Jika hanya satu sumber → confidence maksimum 0.7
        - Jika kedua sumber tersedia & cocok → confidence hingga 0.95
        - Jika kedua sumber tersedia & berbeda → pilih yang lebih yakin,
          tetapi confidence dikurangi (×0.8)
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        if not self.detector:
            return ScanResult(
                platform="Language Analysis",
                username=filename,
                status="NOT_AVAILABLE",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": "langdetect not installed"},
            )

        # Hasil mentah
        ocr_lang, ocr_conf = self._detect_language(ocr_text) if ocr_text and len(ocr_text.strip()) > 10 else (None, 0.0)
        audio_lang, audio_conf = self._detect_language(audio_transcript) if audio_transcript and len(audio_transcript.strip()) > 10 else (None, 0.0)

        # Gabungkan dengan logika cross‑validation
        combined_lang = None
        combined_conf = 0.0

        if ocr_lang and audio_lang:
            if ocr_lang == audio_lang:
                combined_lang = ocr_lang
                # Kedua sumber setuju → confidence tinggi (rata‑rata lalu dipotong 0.95)
                combined_conf = min((ocr_conf + audio_conf) / 2.0, 0.95)
            else:
                # Pilih yang confidence-nya lebih tinggi
                if ocr_conf >= audio_conf:
                    combined_lang = ocr_lang
                    # Karena tidak ada konsensus, confidence dikurangi
                    combined_conf = ocr_conf * 0.8
                else:
                    combined_lang = audio_lang
                    combined_conf = audio_conf * 0.8
        elif ocr_lang:
            combined_lang = ocr_lang
            combined_conf = min(ocr_conf, 0.7)   # hanya satu sumber
        elif audio_lang:
            combined_lang = audio_lang
            combined_conf = min(audio_conf, 0.7) # hanya satu sumber
        else:
            combined_lang = None
            combined_conf = 0.0

        # Regional hints
        regional_hints = self._get_regional_hints(combined_lang) if combined_lang else []

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Language Analysis",
            username=filename,
            status="FOUND" if combined_lang else "NOT_FOUND",
            status_code=200 if combined_lang else 404,
            url=file_path,
            confidence=combined_conf,
            extra={
                "ocr_language": ocr_lang,
                "ocr_confidence": ocr_conf,
                "audio_language": audio_lang,
                "audio_confidence": audio_conf,
                "combined_language": combined_lang,
                "combined_confidence": combined_conf,
                "regional_hints": regional_hints,
                "analysis_time_seconds": analysis_time,
            },
        )

    def _detect_language(self, text: Optional[str]) -> tuple:
        """Deteksi bahasa dari teks, kembalikan (kode_bahasa, confidence)."""
        if not text or len(text.strip()) < 10:
            return None, 0.0
        try:
            from langdetect import detect_langs
            langs = detect_langs(text[:500])   # batasi panjang
            if langs:
                best = langs[0]
                return best.lang, round(best.prob, 2)
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
        return None, 0.0

    @staticmethod
    def _get_regional_hints(lang_code: str) -> List[str]:
        """Berikan petunjuk regional berdasarkan kode bahasa."""
        mapping = {
            "id": ["Indonesia", "Malaysia (Bahasa Melayu)"],
            "en": ["English-speaking country (US, UK, AU, etc.)"],
            "es": ["Spain", "Latin America"],
            "ar": ["Middle East", "North Africa"],
            "zh": ["China", "Taiwan", "Singapore"],
            "hi": ["India"],
            "pt": ["Brazil", "Portugal"],
            "ru": ["Russia", "Former Soviet Union"],
            "ja": ["Japan"],
            "ko": ["South Korea"],
            "fr": ["France", "Canada (Quebec)", "West Africa"],
            "de": ["Germany", "Austria", "Switzerland"],
        }
        return mapping.get(lang_code, [f"Unknown region for language '{lang_code}'"])