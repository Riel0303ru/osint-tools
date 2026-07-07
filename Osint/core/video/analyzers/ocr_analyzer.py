# core/video/analyzers/ocr_analyzer.py
from __future__ import annotations

import os
import re
import time
from typing import List, Dict, Any, Set
from core.base.scan_result import ScanResult
from utils.logger import Logger

# Regex untuk ekstraksi entitas
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\+?\d{7,15}")
URL_REGEX = re.compile(r"https?://[^\s,;\"']+")
USERNAME_REGEX = re.compile(r"@([a-zA-Z0-9._]{3,30})")

# Coba impor Google Cloud Vision
try:
    from google.cloud import vision
    _gcv_available = True
except ImportError:
    _gcv_available = False


class OCRAnalyzer:
    """
    Menganalisis frame video dengan OCR untuk mengekstrak teks,
    termasuk email, telepon, username, URL, dan lainnya.
    Mengutamakan Google Cloud Vision API jika tersedia, fallback ke EasyOCR.

    Catatan: environment variable (termasuk GOOGLE_APPLICATION_CREDENTIALS)
    sudah dimuat oleh main.py melalui load_dotenv, sehingga modul ini
    tidak perlu memuat ulang.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self._gcv_client = None
        self._easyocr_reader = None
        self._use_gcv = _gcv_available

        # Inisialisasi Vision API jika tersedia
        if self._use_gcv:
            try:
                self._gcv_client = vision.ImageAnnotatorClient()
                self.logger.info("Google Cloud Vision OCR siap digunakan")
            except Exception as e:
                self.logger.warning(f"Google Cloud Vision gagal diinisialisasi: {e}. Fallback ke EasyOCR.")
                self._use_gcv = False

        # Inisialisasi EasyOCR sebagai fallback
        if not self._use_gcv:
            self._init_easyocr()

    def _init_easyocr(self):
        """Inisialisasi EasyOCR reader."""
        try:
            import easyocr
            # Memuat model untuk bahasa Inggris dan Indonesia
            self._easyocr_reader = easyocr.Reader(["en", "id"], gpu=False, verbose=False)
            self.logger.info("EasyOCR reader initialized (en, id)")
        except ImportError:
            self.logger.warning("EasyOCR tidak terinstal. Install: pip install easyocr")
        except Exception as e:
            self.logger.error(f"Gagal inisialisasi EasyOCR: {e}")

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        """
        Lakukan OCR pada semua frame dan ekstrak entitas.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        # Periksa ketersediaan engine
        if not self._use_gcv and not self._easyocr_reader:
            return ScanResult(
                platform="OCR Analysis",
                username=filename,
                status="NOT_AVAILABLE",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"message": "Tidak ada OCR engine yang tersedia. Install EasyOCR atau Google Cloud Vision."},
            )

        # Tentukan jumlah frame yang diproses (Vision API lebih efisien)
        frames_to_process = frame_paths[:10] if self._use_gcv else frame_paths[:30]

        all_texts: List[str] = []
        all_emails: Set[str] = set()
        all_phones: Set[str] = set()
        all_urls: Set[str] = set()
        all_usernames: Set[str] = set()
        text_by_frame: Dict[str, str] = {}

        for frame in frames_to_process:
            if not os.path.isfile(frame):
                continue
            frame_name = os.path.basename(frame)
            try:
                if self._use_gcv:
                    frame_text = self._ocr_with_vision(frame)
                else:
                    frame_text = self._ocr_with_easyocr(frame)

                if frame_text.strip():
                    all_texts.append(frame_text)
                    text_by_frame[frame_name] = frame_text[:500]

                    # Ekstrak entitas menggunakan regex
                    emails = EMAIL_REGEX.findall(frame_text)
                    phones = PHONE_REGEX.findall(frame_text)
                    urls = URL_REGEX.findall(frame_text)
                    usernames = USERNAME_REGEX.findall(frame_text)

                    all_emails.update(emails)
                    all_phones.update(phones)
                    all_urls.update(urls)
                    all_usernames.update(usernames)

            except Exception as e:
                self.logger.warning(f"OCR gagal untuk {frame_name}: {e}")

        analysis_time = round(time.time() - start_time, 2)
        has_findings = any([all_emails, all_phones, all_urls, all_usernames, all_texts])

        return ScanResult(
            platform="OCR Analysis",
            username=filename,
            status="FOUND" if has_findings else "NOT_FOUND",
            status_code=200 if has_findings else 404,
            url=file_path,
            confidence=0.9 if has_findings else 0.5,
            extra={
                "total_frames_analyzed": len(text_by_frame),
                "emails": list(all_emails)[:20],
                "phones": list(all_phones)[:20],
                "urls": list(all_urls)[:20],
                "usernames": list(all_usernames)[:20],
                "text_by_frame": text_by_frame,
                "full_text": " ".join(all_texts)[:5000],
                "analysis_time_seconds": analysis_time,
                "method": "Google Cloud Vision" if self._use_gcv else "EasyOCR",
            },
        )

    def _ocr_with_vision(self, image_path: str) -> str:
        """Jalankan OCR menggunakan Google Cloud Vision."""
        with open(image_path, "rb") as img_file:
            content = img_file.read()
        image = vision.Image(content=content)
        response = self._gcv_client.text_detection(image=image)
        texts = response.text_annotations
        if texts:
            # texts[0] adalah seluruh teks gabungan
            return texts[0].description
        return ""

    def _ocr_with_easyocr(self, image_path: str) -> str:
        """Jalankan OCR menggunakan EasyOCR."""
        try:
            # Coba detail=0 (hanya teks)
            results = self._easyocr_reader.readtext(image_path, detail=0)
        except Exception:
            # Fallback: ambil teks dari hasil detail=1
            raw = self._easyocr_reader.readtext(image_path, detail=1)
            results = [item[1] for item in raw if len(item) >= 2]
        return " ".join(results) if results else ""