# core/video/analyzers/environment_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
import cv2
import numpy as np
from core.base.scan_result import ScanResult
from utils.logger import Logger


class EnvironmentAnalyzer:
    """
    Menganalisis lingkungan dari frame video:
    - Indoor vs Outdoor
    - Waktu (siang, malam, twilight)
    - Estimasi cuaca (cerah, berawan, hujan)
    """

    # Thresholds yang dikalibrasi secara empiris
    INDOOR_BRIGHTNESS_THRESHOLD = 80      # rata-rata kecerahan di bawah ini → indoor
    NIGHT_BRIGHTNESS_THRESHOLD = 40       # rata-rata kecerahan di bawah ini → malam
    TWILIGHT_BRIGHTNESS_RANGE = (40, 80)  # antara malam dan siang
    CLOUDY_SATURATION_THRESHOLD = 80      # saturasi rendah → berawan/hujan
    RAIN_VARIANCE_THRESHOLD = 400         # varian tinggi → tekstur hujan

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        """
        Analisis lingkungan berdasarkan sampel frame.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        if not frame_paths:
            return ScanResult(
                platform="Environment Analysis",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "No frames available"},
            )

        # Analisis setiap frame, kumpulkan statistik
        indoor_count = 0
        outdoor_count = 0
        day_count = 0
        night_count = 0
        twilight_count = 0
        sunny_count = 0
        cloudy_count = 0
        rainy_count = 0
        total_analyzed = 0

        frame_analyses = []

        for i, frame_path in enumerate(frame_paths[:20]):  # sampel 20 frame
            if not os.path.isfile(frame_path):
                continue

            img = cv2.imread(frame_path)
            if img is None:
                continue

            total_analyzed += 1
            analysis = self._analyze_frame(img, i + 1, frame_path)
            frame_analyses.append(analysis)

            # Akumulasi
            if analysis["indoor_outdoor"] == "indoor":
                indoor_count += 1
            else:
                outdoor_count += 1

            if analysis["time_of_day"] == "day":
                day_count += 1
            elif analysis["time_of_day"] == "night":
                night_count += 1
            else:
                twilight_count += 1

            if analysis["weather"] == "sunny":
                sunny_count += 1
            elif analysis["weather"] == "cloudy":
                cloudy_count += 1
            elif analysis["weather"] == "rainy":
                rainy_count += 1

        # Keputusan mayoritas
        indoor_outdoor = "outdoor" if outdoor_count >= indoor_count else "indoor"
        time_of_day = self._majority({"day": day_count, "night": night_count, "twilight": twilight_count})
        weather = self._majority({"sunny": sunny_count, "cloudy": cloudy_count, "rainy": rainy_count})

        # Hitung confidence
        confidence = self._calculate_confidence({
            "indoor_outdoor": (indoor_count, outdoor_count),
            "time_of_day": (day_count, night_count, twilight_count),
            "weather": (sunny_count, cloudy_count, rainy_count),
        }, total_analyzed)

        analysis_time = round(time.time() - start_time, 2)

        # Bangun evidence untuk geolocation
        evidence = self._build_evidence(indoor_outdoor, time_of_day, weather)

        return ScanResult(
            platform="Environment Analysis",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=confidence,
            extra={
                "indoor_outdoor": indoor_outdoor,
                "time_of_day": time_of_day,
                "weather": weather,
                "indoor_count": indoor_count,
                "outdoor_count": outdoor_count,
                "day_count": day_count,
                "night_count": night_count,
                "twilight_count": twilight_count,
                "sunny_count": sunny_count,
                "cloudy_count": cloudy_count,
                "rainy_count": rainy_count,
                "total_frames_analyzed": total_analyzed,
                "frame_analyses": frame_analyses[:10],  # sampel
                "evidence": evidence,
                "analysis_time_seconds": analysis_time,
                "method": "Brightness & color histogram analysis",
            },
        )

    def _analyze_frame(self, img: np.ndarray, index: int, path: str) -> Dict[str, Any]:
        """Analisis satu frame."""
        # Konversi ke ruang warna berbeda
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Brightness (rata-rata intensitas abu-abu)
        brightness = float(np.mean(gray))

        # 2. Saturasi (rata-rata channel S pada HSV)
        saturation = float(np.mean(hsv[:, :, 1]))

        # 3. Varians spasial (tekstur) — untuk deteksi hujan
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = float(laplacian.var())

        # 4. Klasifikasi indoor/outdoor
        if brightness < self.INDOOR_BRIGHTNESS_THRESHOLD:
            indoor_outdoor = "indoor"
        else:
            indoor_outdoor = "outdoor"

        # 5. Klasifikasi waktu
        if brightness < self.NIGHT_BRIGHTNESS_THRESHOLD:
            time_of_day = "night"
        elif brightness < self.TWILIGHT_BRIGHTNESS_RANGE[1]:
            time_of_day = "twilight"
        else:
            time_of_day = "day"

        # 6. Klasifikasi cuaca (hanya relevan untuk outdoor)
        if indoor_outdoor == "indoor":
            weather = "indoor"  # tidak terdefinisi untuk indoor
        else:
            if variance > self.RAIN_VARIANCE_THRESHOLD:
                weather = "rainy"
            elif saturation < self.CLOUDY_SATURATION_THRESHOLD:
                weather = "cloudy"
            else:
                weather = "sunny"

        return {
            "frame_index": index,
            "frame_path": os.path.basename(path),
            "brightness": round(brightness, 1),
            "saturation": round(saturation, 1),
            "variance": round(variance, 1),
            "indoor_outdoor": indoor_outdoor,
            "time_of_day": time_of_day,
            "weather": weather,
        }

    @staticmethod
    def _majority(counts: Dict[str, int]) -> str:
        """Kembalikan kunci dengan nilai tertinggi."""
        if not counts:
            return "unknown"
        return max(counts, key=counts.get)

    @staticmethod
    def _calculate_confidence(counts: Dict, total: int) -> float:
        """Hitung confidence berdasarkan seberapa dominan mayoritas."""
        if total == 0:
            return 0.0

        # Untuk indoor/outdoor
        io = counts["indoor_outdoor"]
        io_ratio = max(io[0], io[1]) / total if total > 0 else 0

        # Untuk time of day
        tod = counts["time_of_day"]
        tod_max = max(tod[0], tod[1], tod[2]) if total > 0 else 0
        tod_ratio = tod_max / total if total > 0 else 0

        # Untuk weather
        w = counts["weather"]
        w_max = max(w[0], w[1], w[2]) if total > 0 else 0
        w_ratio = w_max / total if total > 0 else 0

        # Rata-rata ketiga rasio, dikalikan 100%
        avg_ratio = (io_ratio + tod_ratio + w_ratio) / 3.0
        return round(avg_ratio, 2)

    @staticmethod
    def _build_evidence(indoor_outdoor: str, time_of_day: str, weather: str) -> List[str]:
        """Bangun daftar evidence untuk geolocation analyzer."""
        evidence = []
        if indoor_outdoor == "outdoor":
            evidence.append("Outdoor scene")
        else:
            evidence.append("Indoor scene")

        if time_of_day == "day":
            evidence.append("Daytime")
        elif time_of_day == "night":
            evidence.append("Nighttime – possible artificial lighting")
        elif time_of_day == "twilight":
            evidence.append("Twilight – dawn or dusk")

        if weather == "sunny":
            evidence.append("Sunny/clear weather")
        elif weather == "cloudy":
            evidence.append("Cloudy/overcast")
        elif weather == "rainy":
            evidence.append("Rainy/wet conditions – possible rain streaks")

        return evidence