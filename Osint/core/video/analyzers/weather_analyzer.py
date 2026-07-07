# core/video/analyzers/weather_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
import cv2
import numpy as np
from core.base.scan_result import ScanResult
from utils.logger import Logger


class WeatherAnalyzer:
    """
    Menganalisis kondisi cuaca secara visual dari frame video.
    Mendeteksi: cerah (sunny), berawan (cloudy), hujan (rainy), berkabut (foggy).
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        if not frame_paths:
            return ScanResult(
                platform="Weather Analysis",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "No frames available"},
            )

        results = []
        sunny = cloudy = rainy = foggy = 0
        total = 0

        for frame_path in frame_paths[:20]:
            img = cv2.imread(frame_path)
            if img is None:
                continue
            total += 1
            label, conf = self._classify_weather(img)
            results.append({"frame": os.path.basename(frame_path), "weather": label, "confidence": conf})
            if label == "sunny":
                sunny += 1
            elif label == "cloudy":
                cloudy += 1
            elif label == "rainy":
                rainy += 1
            elif label == "foggy":
                foggy += 1

        # Mayoritas
        counts = {"sunny": sunny, "cloudy": cloudy, "rainy": rainy, "foggy": foggy}
        majority = max(counts, key=counts.get) if total > 0 else "unknown"
        confidence = counts[majority] / total if total > 0 else 0.0

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Weather Analysis",
            username=filename,
            status="FOUND" if majority != "unknown" else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=confidence,
            extra={
                "weather": majority,
                "confidence": round(confidence, 2),
                "sunny_frames": sunny,
                "cloudy_frames": cloudy,
                "rainy_frames": rainy,
                "foggy_frames": foggy,
                "total_frames": total,
                "details": results[:10],
                "analysis_time_seconds": analysis_time,
                "method": "Histogram + edge density analysis",
            },
        )

    def _classify_weather(self, img: np.ndarray) -> tuple:
        """Klasifikasi cuaca satu frame. Mengembalikan (label, confidence)."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        brightness = np.mean(gray)
        saturation = np.mean(hsv[:, :, 1])

        # Edge density (tekstur) – hujan atau kabut mengurangi edge
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.mean(edges) / 255.0

        # Heuristik
        if brightness > 150 and saturation > 80:
            return "sunny", 0.85
        elif brightness > 100 and saturation < 60:
            return "cloudy", 0.75
        elif edge_density > 0.15 and saturation > 60:
            return "rainy", 0.7
        elif brightness < 80 and edge_density < 0.1:
            return "foggy", 0.8
        else:
            return "cloudy", 0.5