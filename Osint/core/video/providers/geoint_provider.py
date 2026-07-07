# core/video/providers/geoint_provider.py
from __future__ import annotations

import math
import os
from typing import Dict, Any, Optional
from utils.logger import Logger


class GeoINTProvider:
    """
    Provider untuk analisis geospasial lanjutan.
    Menghitung sudut matahari, arah bayangan, dan validasi landmark.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def sun_position(self, lat: float, lon: float, timestamp: float) -> Dict[str, Any]:
        """
        Hitung posisi matahari (azimuth, altitude) berdasarkan waktu dan lokasi.
        Rumus disederhanakan untuk estimasi cepat.
        """
        # Konversi timestamp ke jam dalam UTC (asumsi timestamp UNIX)
        import datetime
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        hour = dt.hour + dt.minute / 60.0

        # Perkiraan deklinasi matahari (sederhana)
        day_of_year = dt.timetuple().tm_yday
        declination = 23.45 * math.sin(math.radians(360 / 365 * (284 + day_of_year)))

        # Sudut jam (solar time)
        solar_noon = 12.0  # perkiraan UTC
        hour_angle = (hour - solar_noon) * 15

        # Konversi ke altitude dan azimuth
        lat_rad = math.radians(lat)
        dec_rad = math.radians(declination)
        ha_rad = math.radians(hour_angle)

        # Altitude
        alt_rad = math.asin(
            math.sin(lat_rad) * math.sin(dec_rad) +
            math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
        )
        altitude = math.degrees(alt_rad)

        # Azimuth
        az_rad = math.atan2(
            -math.sin(ha_rad),
            math.cos(lat_rad) * math.tan(dec_rad) - math.sin(lat_rad) * math.cos(ha_rad)
        )
        azimuth = (math.degrees(az_rad) + 360) % 360

        return {"altitude": round(altitude, 1), "azimuth": round(azimuth, 1)}

    def shadow_direction(self, lat: float, lon: float, timestamp: float) -> str:
        """Perkirakan arah bayangan (cardinal direction) dari posisi matahari."""
        sun = self.sun_position(lat, lon, timestamp)
        azimuth = sun["azimuth"]
        # Bayangan berlawanan arah matahari
        shadow_az = (azimuth + 180) % 360
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = round(shadow_az / 45) % 8
        return directions[idx]

    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validasi apakah koordinat berada di permukaan bumi."""
        return -90 <= lat <= 90 and -180 <= lon <= 180

    def nearby_landmarks(self, lat: float, lon: float, radius_km: float = 10) -> list:
        """
        Cari landmark terkenal dalam radius tertentu (database dummy).
        Di production, bisa dihubungkan dengan OSM atau dataset landmark.
        """
        # Landmark dummy di beberapa kota besar
        dummy_landmarks = [
            {"name": "Monas", "lat": -6.1754, "lon": 106.8272, "city": "Jakarta"},
            {"name": "Eiffel Tower", "lat": 48.8584, "lon": 2.2945, "city": "Paris"},
            {"name": "Patung Liberty", "lat": 40.6892, "lon": -74.0445, "city": "New York"},
            {"name": "Burj Khalifa", "lat": 25.1972, "lon": 55.2744, "city": "Dubai"},
        ]
        nearby = []
        for lm in dummy_landmarks:
            dist = self._haversine(lat, lon, lm["lat"], lm["lon"])
            if dist <= radius_km:
                lm["distance_km"] = round(dist, 2)
                nearby.append(lm)
        return nearby

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2) -> float:
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))