# core/video/extractors/gps_extractor.py
from __future__ import annotations

import os
import re
import time
from typing import Dict, Any, Optional, Tuple
from core.base.scan_result import ScanResult
from utils.logger import Logger


class GPSExtractor:
    """
    Mengekstrak koordinat GPS dari metadata video.
    Mendukung berbagai format: ISO 6709, DMS, decimal dalam tag metadata.
    """

    # Pola regex untuk berbagai format GPS
    ISO6709_PATTERN = re.compile(
        r"([+-]\d{2,3}(?:\.\d+)?)[,\s]*([+-]\d{2,3}(?:\.\d+)?)(?:[,\s]*([+-]\d+(?:\.\d+)?))?"
    )
    DMS_PATTERN = re.compile(
        r"(\d{1,3})°\s*(\d{1,2})'\s*(\d{1,2}(?:\.\d+)?)\"?\s*([NS])\s*,?\s*"
        r"(\d{1,3})°\s*(\d{1,2})'\s*(\d{1,2}(?:\.\d+)?)\"?\s*([EW])"
    )
    DECIMAL_PATTERN = re.compile(
        r"([+-]?\d{1,3}\.\d{4,})\s*[,/]\s*([+-]?\d{1,3}\.\d{4,})"
    )

    # Tag metadata yang mungkin berisi GPS
    GPS_TAGS = [
        "location",
        "com.apple.quicktime.location.ISO6709",
        "GPS coordinates",
        "gps",
        "geo",
        "geolocation",
    ]

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def extract(self, metadata: Dict[str, Any], file_path: str) -> ScanResult:
        """
        Parse GPS dari metadata video.
        Mengembalikan ScanResult dengan latitude, longitude, altitude.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        tags = metadata.get("tags", {})
        gps_raw = None
        for tag in self.GPS_TAGS:
            if tag in tags:
                gps_raw = tags[tag]
                break

        if not gps_raw:
            # Coba juga dari 'gps' key jika ada
            gps_dict = metadata.get("gps", {})
            if gps_dict.get("raw"):
                gps_raw = gps_dict["raw"]

        if not gps_raw:
            return ScanResult(
                platform="GPS Extraction",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "No GPS data found in metadata tags"},
            )

        lat, lon, alt = self._parse_coordinates(str(gps_raw))
        extraction_time = round(time.time() - start_time, 2)

        if lat is None or lon is None:
            return ScanResult(
                platform="GPS Extraction",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={
                    "error": "Failed to parse GPS coordinates",
                    "raw_gps": gps_raw,
                },
            )

        return ScanResult(
            platform="GPS Extraction",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=0.95,
            extra={
                "latitude": lat,
                "longitude": lon,
                "altitude": alt,
                "raw_gps": gps_raw,
                "extraction_time_seconds": extraction_time,
                "google_maps_link": f"https://maps.google.com/?q={lat},{lon}",
            },
        )

    def _parse_coordinates(self, raw: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Parse string GPS ke (latitude, longitude, altitude).
        Mengembalikan tuple (lat, lon, alt) atau None jika gagal.
        """
        # 1. Coba format ISO 6709: +12.3456+098.7654+100.0/
        match = self.ISO6709_PATTERN.search(raw)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            alt = float(match.group(3)) if match.group(3) else None
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon, alt

        # 2. Coba format DMS: 12°34'56"N 98°45'12"E
        match = self.DMS_PATTERN.search(raw)
        if match:
            lat_d, lat_m, lat_s, lat_dir = match.group(1, 2, 3, 4)
            lon_d, lon_m, lon_s, lon_dir = match.group(5, 6, 7, 8)
            lat = self._dms_to_decimal(float(lat_d), float(lat_m), float(lat_s), lat_dir)
            lon = self._dms_to_decimal(float(lon_d), float(lon_m), float(lon_s), lon_dir)
            if lat is not None and lon is not None:
                return lat, lon, None

        # 3. Coba format decimal sederhana: 12.3456, 98.7654
        match = self.DECIMAL_PATTERN.search(raw)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon, None

        # 4. Coba ekstrak dua bilangan float berturut-turut
        numbers = re.findall(r"[-+]?\d+\.\d+", raw)
        if len(numbers) >= 2:
            lat, lon = float(numbers[0]), float(numbers[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                alt = float(numbers[2]) if len(numbers) >= 3 else None
                return lat, lon, alt

        return None, None, None

    @staticmethod
    def _dms_to_decimal(degrees: float, minutes: float, seconds: float, direction: str) -> Optional[float]:
        """Konversi DMS ke decimal degrees."""
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        if direction.upper() in ("S", "W"):
            decimal = -decimal
        if not (-90 <= decimal <= 90 if direction.upper() in "NS" else -180 <= decimal <= 180):
            return None
        return decimal