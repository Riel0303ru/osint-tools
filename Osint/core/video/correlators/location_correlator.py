# core/video/correlators/location_correlator.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.models.video_entity import VideoEntity
from utils.logger import Logger


class LocationCorrelator:
    """
    Menghubungkan petunjuk lokasi dari video (GPS, geolocation inference,
    environment) untuk mempersempit area dan menghasilkan koordinat kandidat.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def correlate(
        self,
        gps_result: Optional[ScanResult] = None,
        geolocation_result: Optional[ScanResult] = None,
        environment_result: Optional[ScanResult] = None,
        language_result: Optional[ScanResult] = None,
        landmark_result: Optional[ScanResult] = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Gabungkan GPS, inference geolokasi, environment, bahasa, dan
        landmark untuk menghasilkan lokasi yang paling mungkin.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        locations = []
        gps_loc = None  # ← inisialisasi untuk menghindari UnboundLocalError

        # 1. GPS langsung (paling akurat)
        if gps_result and gps_result.status == "FOUND":
            lat = gps_result.extra.get("latitude")
            lon = gps_result.extra.get("longitude")
            if lat is not None and lon is not None:
                gps_loc = {
                    "latitude": lat,
                    "longitude": lon,
                    "source": "gps_metadata",
                    "confidence": 0.95,
                }
                locations.append(gps_loc)

        # 2. Geolocation inference
        if geolocation_result and geolocation_result.status == "FOUND":
            for c in geolocation_result.extra.get("candidates", []):
                if c.get("country", "Unknown") != "Unknown":
                    locations.append({
                        "country": c.get("country"),
                        "confidence": c.get("country_confidence", 0.5),
                        "evidence": c.get("evidence", []),
                        "reasoning": c.get("reasoning", ""),
                        "source": "geolocation_inference",
                    })

        # 3. Environment hints
        env_evidence = []
        if environment_result and environment_result.status == "FOUND":
            env_evidence = environment_result.extra.get("evidence", [])

        # 4. Language hints
        lang_hint = ""
        if language_result and language_result.status == "FOUND":
            lang_hint = language_result.extra.get("combined_language", "")

        # 5. Landmark hints
        landmark_hints = []
        if landmark_result and landmark_result.status == "FOUND":
            for c in landmark_result.extra.get("candidates", []):
                if c.get("keyword"):
                    landmark_hints.append(c["keyword"])

        # Gabungkan menjadi satu lokasi terbaik
        best_location = None
        if locations:
            if gps_loc:  # prioritaskan GPS
                best_location = gps_loc
            else:
                # Pilih geolocation inference dengan confidence tertinggi
                best_location = max(locations, key=lambda x: x.get("confidence", 0))

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Location Correlation",
            username=filename,
            status="FOUND" if best_location else "NOT_FOUND",
            status_code=200 if best_location else 404,
            url=file_path,
            confidence=best_location.get("confidence", 0.3) if best_location else 0.0,
            extra={
                "best_location": best_location,
                "all_locations": locations,
                "environment_evidence": env_evidence,
                "language_hint": lang_hint,
                "landmark_hints": landmark_hints,
                "analysis_time_seconds": analysis_time,
                "ready_for_map_display": bool(gps_loc),  # aman karena sudah diinisialisasi
            },
        )