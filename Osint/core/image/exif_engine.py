# core/image/exif_engine.py
from __future__ import annotations

from typing import Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class EXIFEngine:
    """Extract EXIF metadata including GPS coordinates, camera model, and timestamps."""

    @staticmethod
    def _convert_to_degrees(value: Any) -> float:
        """Convert GPS coordinates from EXIF format to decimal degrees."""
        try:
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)
        except (TypeError, IndexError, ValueError):
            return 0.0

    @staticmethod
    def _get_gps_info(exif_data: Dict) -> Dict[str, Any]:
        """Extract GPS coordinates if available."""
        gps_info = {}
        if "GPSInfo" in exif_data:
            gps = exif_data["GPSInfo"]
            try:
                lat = gps.get(2)
                lat_ref = gps.get(1, "N")
                lon = gps.get(4)
                lon_ref = gps.get(3, "E")

                if lat and lon:
                    lat_decimal = EXIFEngine._convert_to_degrees(lat)
                    lon_decimal = EXIFEngine._convert_to_degrees(lon)
                    if lat_ref == "S":
                        lat_decimal = -lat_decimal
                    if lon_ref == "W":
                        lon_decimal = -lon_decimal
                    gps_info["latitude"] = round(lat_decimal, 6)
                    gps_info["longitude"] = round(lon_decimal, 6)
                    gps_info["maps_link"] = (
                        f"https://maps.google.com/?q={lat_decimal},{lon_decimal}"
                    )
            except Exception:
                pass
        return gps_info

    @staticmethod
    def extract_exif(image_path: str) -> Dict[str, Any]:
        """Extract EXIF metadata from an image file."""
        try:
            img = Image.open(image_path)
            raw_exif = img._getexif()
            if not raw_exif:
                return {
                    "camera": "",
                    "gps": "NOT_FOUND",
                    "datetime": "",
                    "software": "",
                    "resolution": f"{img.width}x{img.height}",
                    "gps_details": {},
                    "full_exif": {},
                }

            exif_data = {}
            for tag_id, value in raw_exif.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                # Convert bytes to string for JSON compatibility
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="replace")
                    except Exception:
                        value = str(value)
                exif_data[tag_name] = str(value) if not isinstance(value, (int, float, list, dict)) else value

            gps_info = EXIFEngine._get_gps_info(exif_data)

            return {
                "camera": exif_data.get("Model", ""),
                "gps": "FOUND" if gps_info else "NOT_FOUND",
                "datetime": exif_data.get("DateTimeOriginal", exif_data.get("DateTime", "")),
                "software": exif_data.get("Software", ""),
                "resolution": f"{img.width}x{img.height}",
                "gps_details": gps_info,
                "full_exif": exif_data,
            }
        except Exception:
            return {
                "camera": "",
                "gps": "NOT_FOUND",
                "datetime": "",
                "software": "",
                "resolution": "",
                "gps_details": {},
                "full_exif": {},
                "error": "Failed to read EXIF",
            }