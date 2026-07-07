# core/video/providers/map_provider.py
from __future__ import annotations

import os
import json
from typing import Dict, Any, Optional, Tuple
from utils.logger import Logger


class MapProvider:
    """
    Provider untuk visualisasi peta dan reverse geocoding.
    Mendukung OpenStreetMap (Nominatim) untuk mendapatkan alamat dari koordinat,
    serta generate link Google Maps dan peta statis.
    """

    def __init__(self, base_dir: str = "Osint", use_offline: bool = True):
        self.logger = Logger(base_dir=base_dir)
        self.geocoder = None
        self.use_offline = use_offline
        self._init_geocoder()

    def _init_geocoder(self):
        """Inisialisasi geocoder (online Nominatim atau offline reverse_geocoder)."""
        if self.use_offline:
            try:
                import reverse_geocoder as rg
                self.geocoder = rg
                self.logger.info("Reverse Geocoder (offline) loaded")
            except ImportError:
                self.logger.warning("reverse_geocoder not installed; fallback to online Nominatim")
                try:
                    from geopy.geocoders import Nominatim
                    self.geocoder = Nominatim(user_agent="osint_fusion_video")
                    self.logger.info("Nominatim geocoder loaded (online)")
                except ImportError:
                    self.logger.error("No geocoder available. Install: pip install reverse_geocoder geopy")

    def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Dapatkan alamat dari koordinat.
        Mengembalikan dict dengan country, city, address, dll.
        """
        if not self.geocoder:
            return {"error": "No geocoder available"}

        try:
            if hasattr(self.geocoder, "search"):  # reverse_geocoder
                result = self.geocoder.search((lat, lon))
                if result:
                    r = result[0]
                    return {
                        "country": r.get("cc", ""),
                        "city": r.get("name", ""),
                        "region": r.get("admin1", ""),
                        "address": f"{r.get('name', '')}, {r.get('admin1', '')}, {r.get('cc', '')}",
                    }
            else:  # Nominatim
                location = self.geocoder.reverse(f"{lat}, {lon}")
                if location:
                    addr = location.raw.get("address", {})
                    return {
                        "country": addr.get("country", ""),
                        "city": addr.get("city", addr.get("town", addr.get("village", ""))),
                        "region": addr.get("state", ""),
                        "address": location.address,
                    }
        except Exception as e:
            self.logger.warning(f"Reverse geocoding failed: {e}")
        return {"error": "Geocoding failed"}

    def generate_static_map_url(self, lat: float, lon: float, zoom: int = 14, width: int = 600, height: int = 400) -> str:
        """Buat URL gambar peta statis dari OpenStreetMap (tile server)."""
        # Menggunakan tile.openstreetmap.org static map (via staticmap library atau manual URL)
        # Di sini kita gunakan staticmap (jika tersedia) atau fallback ke link Google Maps
        try:
            from staticmap import StaticMap, CircleMarker
            m = StaticMap(width, height, url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
            marker = CircleMarker((lon, lat), "red", 10)
            m.add_marker(marker)
            image = m.render()
            # Simpan ke file
            return ""  # placeholder
        except ImportError:
            return f"https://staticmap.openstreetmap.de/staticmap.php?center={lat},{lon}&zoom={zoom}&size={width}x{height}&maptype=mapnik"

    def get_map_links(self, lat: float, lon: float) -> Dict[str, str]:
        """Kembalikan berbagai link peta untuk investigasi."""
        return {
            "google_maps": f"https://maps.google.com/?q={lat},{lon}",
            "openstreetmap": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=14",
            "google_earth": f"https://earth.google.com/web/@{lat},{lon},5000a,1000d",
            "bing_maps": f"https://www.bing.com/maps?cp={lat}~{lon}&lvl=14",
        }