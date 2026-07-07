# core/image/image_scanner.py
from __future__ import annotations

import asyncio
import os
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

from core.base.scan_result import ScanResult
from core.image.image_workflow import ImageWorkflow
from utils.logger import Logger

# Thread pool untuk operasi blocking (pemrosesan gambar)
_pool = ThreadPoolExecutor(max_workers=4)


class ImageScanner:
    """
    Async-safe image scanner.
    Membungkus ImageWorkflow yang bersifat blocking ke dalam thread pool
    agar tidak memblokir event loop utama.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.workflow = ImageWorkflow(base_dir)

    async def scan_image(self, image_path: str) -> Tuple[List[ScanResult], dict]:
        """
        Memindai file gambar dan mengembalikan (List[ScanResult], raw_results_dict).
        Tidak melakukan display atau export di sini – diserahkan ke caller.
        """
        self.logger.info(f"Scanning image -> {image_path}")

        # Validasi keberadaan file
        if not os.path.isfile(image_path):
            return (
                [
                    ScanResult(
                        platform="Image Validation",
                        username=os.path.basename(image_path),
                        status="ERROR",
                        status_code=0,
                        url=image_path,
                        confidence=0.0,
                        extra={"error": "File not found"},
                    )
                ],
                {},  # raw results kosong jika file tidak ditemukan
            )

        filename = os.path.basename(image_path)

        # Jalankan workflow di thread pool
        loop = asyncio.get_running_loop()
        try:
            raw = await loop.run_in_executor(_pool, self.workflow.run, image_path)
        except Exception as e:
            self.logger.error(f"Image workflow failed: {e}")
            return (
                [
                    ScanResult(
                        platform="Image Validation",
                        username=filename,
                        status="ERROR",
                        status_code=0,
                        url=image_path,
                        confidence=0.0,
                        extra={"error": str(e)},
                    )
                ],
                {},
            )

        # Konversi ke List[ScanResult] untuk kompatibilitas pipeline
        scan_results = self._results_to_scanresults(raw, filename, image_path)
        return scan_results, raw

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Bersihkan nama file dari karakter ilegal untuk folder."""
        import re
        return re.sub(r'[<>:"/\\|?*]', "_", name)

    def _results_to_scanresults(
        self, results: dict, filename: str, image_path: str
    ) -> List[ScanResult]:
        """Mengonversi hasil gabungan ke dalam list ScanResult."""
        scan_results = []

        # EXIF
        exif = results["exif"]
        scan_results.append(
            ScanResult(
                platform="EXIF Metadata",
                username=filename,
                status="FOUND" if exif.get("camera") or exif.get("gps") == "FOUND" else "NOT_FOUND",
                status_code=200 if exif.get("camera") else 404,
                url=image_path,
                confidence=0.9 if exif.get("gps") == "FOUND" else 0.5,
                extra=exif,
            )
        )

        # OCR
        ocr = results["ocr"]
        has_ocr = bool(ocr.get("emails") or ocr.get("phones") or ocr.get("usernames") or ocr.get("urls"))
        scan_results.append(
            ScanResult(
                platform="OCR",
                username=filename,
                status="FOUND" if has_ocr else "NOT_FOUND",
                status_code=200 if has_ocr else 404,
                url=image_path,
                confidence=0.9 if has_ocr else 0.3,
                extra=ocr,
            )
        )

        # Face Detection
        faces = results["faces"]
        face_count = faces.get("faces_detected", 0)
        scan_results.append(
            ScanResult(
                platform="Face Detection",
                username=filename,
                status="FOUND" if face_count > 0 else "NOT_FOUND",
                status_code=200 if face_count > 0 else 404,
                url=image_path,
                confidence=0.95 if face_count > 0 else 0.5,
                extra=faces,
            )
        )

        # Perceptual Hash
        hash_data = results["hash"]
        scan_results.append(
            ScanResult(
                platform="Perceptual Hash",
                username=filename,
                status="FOUND" if hash_data.get("hash") else "ERROR",
                status_code=200 if hash_data.get("hash") else 500,
                url=image_path,
                confidence=1.0 if hash_data.get("hash") else 0.0,
                extra=hash_data,
            )
        )

        # Steganography
        stego = results["steganography"]
        scan_results.append(
            ScanResult(
                platform="Steganography",
                username=filename,
                status="FOUND" if stego.get("suspicious") else "NOT_FOUND",
                status_code=200,
                url=image_path,
                confidence=0.7 if stego.get("suspicious") else 0.3,
                extra=stego,
            )
        )

        # Reverse Search
        for sr in results.get("reverse_search", []):
            scan_results.append(
                ScanResult(
                    platform=sr["platform"],
                    username=filename,
                    status=sr.get("status", "READY"),
                    status_code=200,
                    url=sr.get("url", ""),
                    confidence=0.0,
                    extra=sr,
                )
            )

        # Object Detection (placeholder)
        obj = results["object_detection"]
        scan_results.append(
            ScanResult(
                platform="Object Detection",
                username=filename,
                status=obj.get("status", "NOT_IMPLEMENTED"),
                status_code=0,
                url=image_path,
                confidence=0.0,
                extra=obj,
            )
        )

        return scan_results