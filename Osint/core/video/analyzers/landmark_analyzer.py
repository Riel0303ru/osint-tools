# core/video/analyzers/landmark_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger

# Coba impor Google Cloud Vision. Jika tidak tersedia, fallback ke mode offline.
try:
    from google.cloud import vision
    _gcv_available = True
except ImportError:
    _gcv_available = False


class LandmarkAnalyzer:
    """
    Mendeteksi landmark dari frame video.
    - Jika Google Cloud Vision tersedia, gunakan Landmark Detection API.
    - Jika tidak, gunakan database landmark offline + heuristik visual.
    """

    # -------------------- DATABASE LANDMARK OFFLINE (contoh) --------------------
    LANDMARK_DATABASE = {
        "monas": ("Monumen Nasional (Monas)", -6.1754, 106.8272),
        "monumen nasional": ("Monumen Nasional (Monas)", -6.1754, 106.8272),
        "borobudur": ("Candi Borobudur", -7.6079, 110.2038),
        "prambanan": ("Candi Prambanan", -7.7520, 110.4915),
        "kuta": ("Pantai Kuta", -8.7185, 115.1686),
        "bali": ("Pulau Bali", -8.3405, 115.0920),
        "jakarta": ("Jakarta", -6.2088, 106.8456),
        "surabaya": ("Surabaya", -7.2575, 112.7521),
        "bandung": ("Bandung", -6.9175, 107.6191),
        "yogyakarta": ("Yogyakarta", -7.7956, 110.3695),
        "eiffel": ("Eiffel Tower", 48.8584, 2.2945),
        "tower eiffel": ("Eiffel Tower", 48.8584, 2.2945),
        "big ben": ("Big Ben", 51.5007, -0.1246),
        "london": ("London", 51.5074, -0.1278),
        "taj mahal": ("Taj Mahal", 27.1751, 78.0421),
        "great wall": ("Tembok Besar Cina", 40.4319, 116.5704),
        "pyramid": ("Piramida Giza", 29.9792, 31.1342),
        "machu picchu": ("Machu Picchu", -13.1631, -72.5450),
        "colosseum": ("Koloseum", 41.8902, 12.4922),
        "opera house": ("Sydney Opera House", -33.8568, 151.2153),
    }

    # Keyword untuk fallback (tetap dipertahankan untuk mode offline)
    LANDMARK_KEYWORDS = {
        "monument": ["monumen", "monument", "monas", "national monument"],
        "mosque": ["masjid", "mosque", "masjid raya", "istiqlal", "grand mosque"],
        "church": ["gereja", "church", "cathedral", "katedral", "basilica"],
        "temple": ["pura", "candi", "temple", "vihara", "klenteng", "pagoda"],
        "government": ["gedung", "government", "presidential palace", "istana", "kantor", "dpr", "parliament", "senate"],
        "bridge": ["jembatan", "bridge", "golden gate", "brooklyn bridge", "tower bridge"],
        "airport": ["bandara", "airport", "terminal", "soekarno", "hatta", "juanda", "changi", "heathrow"],
        "station": ["stasiun", "station", "terminal bus", "kereta api", "grand central"],
        "tower": ["menara", "tower", "eiffel", "tallest", "skyscraper", "burj", "petronas"],
        "mountain": ["gunung", "mountain", "volcano", "peak", "rinjani", "bromo", "merapi", "everest"],
        "river": ["sungai", "river", "canal", "waterfront", "harbour", "pelabuhan", "port"],
        "coastline": ["pantai", "beach", "coast", "sea", "ocean", "laut", "teluk", "bay"],
    }

    NATURAL_COLORS = {
        "mountain": [(100, 140, 80), (120, 100, 50)],
        "river": [(200, 120, 30), (180, 100, 20)],
        "coastline": [(180, 180, 120), (200, 150, 80)],
    }

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self._gcv_client = None
        self._use_gcv = _gcv_available
        if self._use_gcv:
            try:
                self._gcv_client = vision.ImageAnnotatorClient()
                self.logger.info("Google Cloud Vision Landmark Detection siap digunakan")
            except Exception as e:
                self.logger.warning(f"Google Cloud Vision tidak bisa diinisialisasi: {e}. Fallback ke offline.")
                self._use_gcv = False

    def analyze(
        self,
        frame_paths: List[str],
        ocr_text: str = "",
        file_path: str = "",
    ) -> ScanResult:
        """
        Analisis landmark dari frame dan teks OCR.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()
        candidates = []

        # 1. Deteksi dari teks OCR (selalu dilakukan)
        if ocr_text:
            text_lower = ocr_text.lower()
            # Cek di database offline terlebih dahulu (memberikan koordinat)
            for keyword, (name, lat, lon) in self.LANDMARK_DATABASE.items():
                if keyword in text_lower:
                    candidates.append({
                        "category": "landmark",
                        "name": name,
                        "confidence": 0.9,
                        "source": "ocr_keyword",
                        "locations": [{"lat": lat, "lon": lon}],
                    })
            # Jika tidak ada yang cocok di database, gunakan heuristik kategori
            if not any(c.get("source") == "ocr_keyword" for c in candidates):
                for category, keywords in self.LANDMARK_KEYWORDS.items():
                    for kw in keywords:
                        if kw in text_lower:
                            candidates.append({
                                "category": category,
                                "name": kw,
                                "confidence": 0.7,
                                "source": "ocr_text",
                            })
                            break  # satu per kategori

        # 2. Deteksi visual: Cloud Vision atau fallback
        if self._use_gcv:
            gcv_candidates = self._analyze_with_vision(frame_paths[:5])
            candidates.extend(gcv_candidates)
        else:
            # Hanya jalankan heuristik visual jika tidak ada hasil dari OCR
            if not candidates:
                for frame_path in frame_paths[:5]:
                    visual_hints = self._analyze_frame_visual(frame_path)
                    candidates.extend(visual_hints)

        # Deduplikasi
        unique_candidates = {}
        for c in candidates:
            key = c.get("name", c.get("category", ""))
            if key not in unique_candidates or c["confidence"] > unique_candidates[key]["confidence"]:
                unique_candidates[key] = c

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Landmark Analysis",
            username=filename,
            status="FOUND" if unique_candidates else "NOT_FOUND",
            status_code=200 if unique_candidates else 404,
            url=file_path,
            confidence=0.85 if unique_candidates else 0.3,
            extra={
                "candidates": list(unique_candidates.values()),
                "total_candidates": len(unique_candidates),
                "analysis_time_seconds": analysis_time,
                "method": "Google Cloud Vision" if self._use_gcv else "Keyword matching + offline DB + visual heuristics",
            },
        )

    def _analyze_with_vision(self, frame_paths: List[str]) -> List[Dict[str, Any]]:
        """Gunakan Google Cloud Vision untuk mendeteksi landmark."""
        candidates = []
        for frame_path in frame_paths:
            if not os.path.isfile(frame_path):
                continue
            try:
                with open(frame_path, "rb") as img_file:
                    content = img_file.read()
                image = vision.Image(content=content)
                response = self._gcv_client.landmark_detection(image=image)
                landmarks = response.landmark_annotations
                for landmark in landmarks:
                    candidates.append({
                        "category": "landmark",
                        "name": landmark.description,
                        "confidence": round(landmark.score, 2),
                        "source": "google_vision",
                        "locations": [
                            {"lat": loc.lat_lng.latitude, "lon": loc.lat_lng.longitude}
                            for loc in landmark.locations
                        ],
                    })
            except Exception as e:
                self.logger.warning(f"Vision API gagal untuk {frame_path}: {e}")
        return candidates

    def _analyze_frame_visual(self, frame_path: str) -> List[Dict[str, Any]]:
        """Fallback: analisis warna dominan."""
        import cv2
        import numpy as np

        hints = []
        if not os.path.isfile(frame_path):
            return hints
        img = cv2.imread(frame_path)
        if img is None:
            return hints
        avg_color = np.mean(img, axis=(0, 1))
        avg_bgr = (avg_color[0], avg_color[1], avg_color[2])

        for category, color_ranges in self.NATURAL_COLORS.items():
            for target_bgr in color_ranges:
                dist = np.sqrt(
                    (avg_bgr[0] - target_bgr[0])**2 +
                    (avg_bgr[1] - target_bgr[1])**2 +
                    (avg_bgr[2] - target_bgr[2])**2
                )
                if dist < 80:
                    confidence = round(1.0 - (dist / 200), 2)
                    hints.append({
                        "category": category,
                        "name": f"visual_{category}",
                        "source": "visual_color",
                        "confidence": min(confidence, 0.8),
                    })
                    break
        return hints