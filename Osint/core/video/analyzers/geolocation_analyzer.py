# core/video/analyzers/geolocation_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.models.location_candidate import LocationCandidate
from utils.logger import Logger


class GeolocationAnalyzer:
    """
    Mengestimasi lokasi pengambilan video dari berbagai petunjuk:
    - GPS metadata (jika ada)
    - Bahasa yang terdeteksi (teks + audio)
    - Environment (outdoor/indoor, weather)
    - Landmark yang terdeteksi (termasuk dari Google Cloud Vision)
    - Heuristik regional (berdasarkan kombinasi petunjuk)
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(
        self,
        metadata_result: ScanResult | None = None,
        language_result: ScanResult | None = None,
        environment_result: ScanResult | None = None,
        landmark_result: ScanResult | None = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Gabungkan semua petunjuk untuk menghasilkan kandidat lokasi.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        candidates: List[LocationCandidate] = []

        # 1. GPS dari metadata
        gps = self._extract_gps(metadata_result)
        if gps:
            candidates.append(LocationCandidate(
                country="GPS-Tagged",
                country_confidence=1.0,
                latitude=gps.get("lat"),
                longitude=gps.get("lon"),
                gps_source="metadata",
                evidence=["GPS coordinates found in video metadata"],
                reasoning="Direct GPS coordinates from camera/device metadata.",
            ))

        # 2. Koordinat dari Landmark (Google Cloud Vision)
        if landmark_result and landmark_result.status == "FOUND":
            for c in landmark_result.extra.get("candidates", []):
                if c.get("source") == "google_vision" and "locations" in c and c["locations"]:
                    # Ambil koordinat pertama
                    loc = c["locations"][0]
                    candidates.append(LocationCandidate(
                        country=c.get("name", ""),         # nama landmark sebagai "negara" (atau bisa region)
                        country_confidence=c.get("confidence", 0.9),
                        latitude=loc.get("lat"),
                        longitude=loc.get("lon"),
                        gps_source="landmark_vision",
                        evidence=[f"Landmark detected: {c['name']}"],
                        reasoning=f"Google Cloud Vision identified '{c['name']}' at these coordinates.",
                    ))

        # 3. Petunjuk dari bahasa
        lang_hints = self._get_language_hints(language_result)

        # 4. Petunjuk dari environment
        env_hints = self._get_environment_hints(environment_result)

        # 5. Petunjuk dari landmark (non-Vision)
        landmark_hints = self._get_landmark_hints(landmark_result)

        # 6. Gabungkan petunjuk untuk inferensi lokasi
        #    Hanya infer jika tidak ada GPS pasti atau landmark Vision
        if not gps and not candidates:
            inferred = self._infer_location(lang_hints, env_hints, landmark_hints)
            candidates.extend(inferred)

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Geolocation Analysis",
            username=filename,
            status="FOUND" if candidates else "NOT_FOUND",
            status_code=200 if candidates else 404,
            url=file_path,
            confidence=self._calculate_overall_confidence(candidates),
            extra={
                "candidates": [c.to_dict() for c in candidates],
                "total_candidates": len(candidates),
                "gps_direct": gps is not None or any(c.gps_source == "landmark_vision" for c in candidates),
                "language_hints": lang_hints,
                "environment_hints": env_hints,
                "landmark_hints": landmark_hints,
                "analysis_time_seconds": analysis_time,
                "method": "Multi-source fusion: GPS + language + environment + landmark Vision API",
            },
        )

    # ---------- Helper Methods ----------

    def _extract_gps(self, result: ScanResult | None) -> Optional[Dict[str, float]]:
        """Ekstrak koordinat GPS dari metadata."""
        if not result or result.status != "FOUND":
            return None
        extra = result.extra or {}
        gps = extra.get("gps", {})
        raw = gps.get("raw", "")
        if raw:
            import re
            match = re.search(r"([+-]\d+\.\d+)\s*[+,]\s*([+-]\d+\.\d+)", raw)
            if match:
                return {"lat": float(match.group(1)), "lon": float(match.group(2))}
        return None

    def _get_language_hints(self, result: ScanResult | None) -> List[str]:
        """Ambil petunjuk dari language analyzer."""
        if not result or result.status != "FOUND":
            return []
        return result.extra.get("regional_hints", []) if result.extra else []

    def _get_environment_hints(self, result: ScanResult | None) -> List[str]:
        """Ambil petunjuk dari environment analyzer."""
        if not result or result.status != "FOUND":
            return []
        return result.extra.get("evidence", []) if result.extra else []

    def _get_landmark_hints(self, result: ScanResult | None) -> List[str]:
        """Ambil petunjuk dari landmark analyzer (baik Vision maupun heuristik)."""
        if not result or result.status != "FOUND":
            return []
        cands = result.extra.get("candidates", []) if result.extra else []
        hints = []
        for c in cands:
            # Untuk Vision, gunakan nama landmark
            if c.get("source") == "google_vision" and c.get("name"):
                hints.append(f"landmark: {c['name']}")
            # Untuk fallback, gunakan keyword
            elif c.get("keyword"):
                hints.append(f"{c['category']}: {c['keyword']}")
            # Jika hanya ada kategori (fallback lama)
            elif c.get("category"):
                hints.append(c['category'])
        return hints

    def _infer_location(
        self,
        lang_hints: List[str],
        env_hints: List[str],
        landmark_hints: List[str],
    ) -> List[LocationCandidate]:
        """Inferensi lokasi dari petunjuk."""
        candidates = []

        # Mapping sederhana: bahasa → negara
        for hint in lang_hints:
            if "Indonesia" in hint:
                candidates.append(LocationCandidate(
                    country="Indonesia",
                    country_confidence=0.9,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="Language detected as Indonesian/Malay; combined with environment and landmark hints.",
                ))
            elif "English" in hint:
                candidates.append(LocationCandidate(
                    country="English-speaking Country",
                    country_confidence=0.6,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="English language detected; location could be US, UK, AU, etc.",
                ))
            elif "Arab" in hint or "Middle East" in hint:
                candidates.append(LocationCandidate(
                    country="Middle East / North Africa",
                    country_confidence=0.7,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="Arabic language detected; likely Middle East or North Africa.",
                ))
            elif "China" in hint or "Chinese" in hint:
                candidates.append(LocationCandidate(
                    country="China / Taiwan / Singapore",
                    country_confidence=0.7,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="Chinese language detected; likely China, Taiwan, or Singapore.",
                ))
            elif "India" in hint:
                candidates.append(LocationCandidate(
                    country="India",
                    country_confidence=0.8,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="Hindi detected; likely India.",
                ))
            elif "Japan" in hint:
                candidates.append(LocationCandidate(
                    country="Japan",
                    country_confidence=0.9,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="Japanese language detected; location Japan.",
                ))
            elif "Korea" in hint:
                candidates.append(LocationCandidate(
                    country="South Korea",
                    country_confidence=0.9,
                    evidence=[hint] + env_hints[:3] + landmark_hints[:2],
                    reasoning="Korean language detected; location South Korea.",
                ))

        # Jika tidak ada bahasa terdeteksi, gunakan environment + landmark
        if not candidates:
            for lh in landmark_hints:
                if "monumen" in lh.lower() or "monas" in lh.lower():
                    candidates.append(LocationCandidate(
                        country="Indonesia",
                        country_confidence=0.7,
                        evidence=env_hints[:3] + [lh],
                        reasoning="Monument keyword detected; likely Indonesia (Monas).",
                    ))
                    break
                elif "eiffel" in lh.lower():
                    candidates.append(LocationCandidate(
                        country="France",
                        country_confidence=0.9,
                        evidence=[lh],
                        reasoning="Eiffel Tower keyword detected; location France.",
                    ))
                    break

        # Fallback: environment saja
        if not candidates and env_hints:
            candidates.append(LocationCandidate(
                country="Unknown",
                country_confidence=0.3,
                evidence=env_hints[:3],
                reasoning="Insufficient data for location; only environment hints available.",
            ))

        return candidates

    def _calculate_overall_confidence(self, candidates: List[LocationCandidate]) -> float:
        """Hitung confidence rata-rata dari semua kandidat."""
        if not candidates:
            return 0.0
        return round(sum(c.country_confidence for c in candidates) / len(candidates), 2)