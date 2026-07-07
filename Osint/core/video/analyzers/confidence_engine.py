# core/video/analyzers/confidence_engine.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class ConfidenceEngine:
    """
    Menghitung confidence score gabungan dari seluruh tahap analisis.
    Menggunakan weighted average dengan bobot berdasarkan jenis analyzer.
    """

    # Bobot confidence per analyzer (seberapa akurat jenis analisis ini)
    CONFIDENCE_WEIGHTS = {
        "Video Metadata": 0.90,
        "Frame Extraction": 0.95,
        "Audio Extraction": 0.90,
        "Subtitle Extraction": 0.80,
        "Thumbnail": 1.00,
        "GPS Extraction": 0.95,
        "Face Detection": 0.75,
        "Object Detection": 0.85,
        "OCR Analysis": 0.80,
        "Audio Analysis": 0.85,
        "Environment Analysis": 0.75,
        "Language Analysis": 0.80,
        "Landmark Analysis": 0.60,
        "Timeline Analysis": 0.90,
        "Geolocation Analysis": 0.70,
        "Risk Assessment": 0.85,
        "AI Analysis": 0.50,
    }

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(self, results: List[ScanResult], file_path: str = "") -> ScanResult:
        """
        Hitung confidence gabungan dari semua hasil.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        total_weight = 0.0
        weighted_sum = 0.0
        details = []

        for r in results:
            platform = r.platform
            weight = self.CONFIDENCE_WEIGHTS.get(platform, 0.5)
            conf = r.confidence if r.status in ("FOUND", "SUCCESS") else 0.0

            weighted_sum += conf * weight
            total_weight += weight

            details.append({
                "platform": platform,
                "status": r.status,
                "confidence": conf,
                "weight": weight,
                "contribution": round(conf * weight, 3),
            })

        overall_confidence = round(weighted_sum / total_weight, 3) if total_weight > 0 else 0.0

        # Kategorisasi confidence level
        if overall_confidence >= 0.90:
            level = "VERY HIGH"
        elif overall_confidence >= 0.75:
            level = "HIGH"
        elif overall_confidence >= 0.50:
            level = "MEDIUM"
        elif overall_confidence >= 0.30:
            level = "LOW"
        else:
            level = "VERY LOW"

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Confidence Engine",
            username=filename,
            status="FOUND" if overall_confidence > 0 else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=overall_confidence,
            extra={
                "overall_confidence": overall_confidence,
                "confidence_level": level,
                "components_analyzed": len(details),
                "details": details,
                "analysis_time_seconds": analysis_time,
                "method": "Weighted average across all analysis stages",
            },
        )