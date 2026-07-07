# core/video/analyzers/face_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
import cv2
from core.base.scan_result import ScanResult
from utils.logger import Logger


class FaceAnalyzer:
    """Deteksi wajah dalam frame video menggunakan OpenCV Haar Cascade."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        # Load cascade classifier bawaan OpenCV
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if not os.path.isfile(cascade_path):
            self.logger.error(f"Face cascade not found: {cascade_path}")
            self.face_cascade = None
        else:
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        """
        Deteksi wajah di semua frame yang diberikan.
        Mengembalikan ScanResult dengan total wajah, lokasi, dan timestamp.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        if not self.face_cascade:
            return ScanResult(
                platform="Face Detection",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": "Face cascade not loaded"},
            )

        all_faces = []
        total_faces = 0

        for frame in frame_paths:
            if not os.path.isfile(frame):
                continue

            img = cv2.imread(frame)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Deteksi wajah
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
            )

            frame_name = os.path.basename(frame)
            for (x, y, w, h) in faces:
                all_faces.append({
                    "frame": frame_name,
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 0.9,  # Haar Cascade tidak memberikan confidence score
                })
                total_faces += 1

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Face Detection",
            username=filename,
            status="FOUND" if total_faces > 0 else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=0.9 if total_faces > 0 else 0.5,
            extra={
                "total_faces": total_faces,
                "frames_with_faces": len(set(f["frame"] for f in all_faces)),
                "faces": all_faces[:100],  # batasi 100 wajah pertama
                "analysis_time_seconds": analysis_time,
                "method": "OpenCV Haar Cascade",
            },
        )