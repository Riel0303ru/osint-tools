# core/video/video_intelligence.py
from __future__ import annotations

from typing import List, Dict, Any
from core.base.scan_result import ScanResult


class VideoIntelligence:
    """
    Scoring engine untuk Video Intelligence.
    Menghitung skor 0–100 berdasarkan temuan dari seluruh pipeline video
    (mencakup 18+ tahap yang telah diimplementasikan di VideoScanner).
    """

    # Bobot total = 100, mencakup semua tahap analisis (sesuai pipeline scanner)
    WEIGHTS = {
        "metadata": 8,
        "gps_extraction": 6,
        "frame_extraction": 4,
        "thumbnail": 2,
        "audio_extraction": 4,
        "subtitle_extraction": 2,
        "face_detection": 8,
        "object_detection": 6,
        "ocr_analysis": 14,
        "environment_analysis": 6,
        "landmark_analysis": 4,
        "audio_analysis": 12,
        "language_analysis": 4,
        "timeline_analysis": 3,
        "geolocation_analysis": 6,
        "risk_assessment": 5,
        "entity_correlation": 3,
        "confidence_engine": 1,
        "ai_analysis": 2,
    }

    @classmethod
    def score(cls, file_path: str, results: List[ScanResult]) -> float:
        """
        Hitung skor intelijen total dari semua ScanResult.
        Setiap komponen memiliki bobot dan sub-skor internal (0–100).
        """
        result_map: Dict[str, ScanResult] = {r.platform: r for r in results}

        # Skor per komponen (0–100)
        scores = {
            "metadata": cls._score_metadata(result_map.get("Video Metadata")),
            "gps_extraction": cls._score_gps(result_map.get("GPS Extraction")),
            "frame_extraction": cls._score_frame_extraction(result_map.get("Frame Extraction")),
            "thumbnail": cls._score_thumbnail(result_map.get("Thumbnail")),
            "audio_extraction": cls._score_audio_extraction(result_map.get("Audio Extraction")),
            "subtitle_extraction": cls._score_subtitle(result_map.get("Subtitle Extraction")),
            "face_detection": cls._score_face_detection(result_map.get("Face Detection")),
            "object_detection": cls._score_object_detection(result_map.get("Object Detection")),
            "ocr_analysis": cls._score_ocr_analysis(result_map.get("OCR Analysis")),
            "environment_analysis": cls._score_environment(result_map.get("Environment Analysis")),
            "landmark_analysis": cls._score_landmark(result_map.get("Landmark Analysis")),
            "audio_analysis": cls._score_audio_analysis(result_map.get("Audio Analysis")),
            "language_analysis": cls._score_language(result_map.get("Language Analysis")),
            "timeline_analysis": cls._score_timeline(result_map.get("Timeline Analysis")),
            "geolocation_analysis": cls._score_geolocation(result_map.get("Geolocation Analysis")),
            "risk_assessment": cls._score_risk_assessment(result_map.get("Risk Assessment")),
            "entity_correlation": cls._score_entity_correlation(result_map.get("Entity Correlation")),
            "confidence_engine": cls._score_confidence_engine(result_map.get("Confidence Engine")),
            "ai_analysis": cls._score_ai(result_map.get("AI Analysis")),
        }

        total = 0.0
        for component, weight in cls.WEIGHTS.items():
            comp_score = scores.get(component, 0.0)
            total += (comp_score / 100.0) * weight

        return round(min(total, 100.0), 1)

    # ------------------------------ Sub-Scorers ------------------------------

    @classmethod
    def _score_metadata(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        score = 40.0
        extra = result.extra or {}

        gps = extra.get("gps", {})
        if gps and gps.get("raw"):
            score += 40.0

        if extra.get("duration_seconds", 0) > 0:
            score += 10.0

        video = extra.get("video", {})
        if video.get("resolution") and video["resolution"] != "?x?":
            score += 10.0

        integrity = extra.get("integrity_check", {})
        if integrity.get("suspicious") is False:
            score += 10.0
        elif integrity.get("findings"):
            score -= min(len(integrity["findings"]) * 5, 20)

        return max(0.0, min(score, 100.0))

    @classmethod
    def _score_gps(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        extra = result.extra or {}
        if extra.get("latitude") is not None and extra.get("longitude") is not None:
            return 100.0
        return 0.0

    @classmethod
    def _score_frame_extraction(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        count = result.extra.get("frames_found", 0) if result.extra else 0
        return min(count * 2.0, 100.0)

    @classmethod
    def _score_thumbnail(cls, result: ScanResult | None) -> float:
        if not result or result.status == "FOUND":
            return 100.0
        return 0.0

    @classmethod
    def _score_audio_extraction(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        audio_size = result.extra.get("audio_size_bytes", 0) if result.extra else 0
        return 100.0 if audio_size > 0 else 50.0

    @classmethod
    def _score_subtitle(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        text = result.extra.get("subtitle_text", "") if result.extra else ""
        return min(len(text) / 10.0, 100.0)

    @classmethod
    def _score_audio_analysis(cls, result: ScanResult | None) -> float:
        if not result or result.status not in ("FOUND", "SUCCESS"):
            return 0.0
        extra = result.extra or {}
        score = 0.0
        if extra.get("transcript"):
            score += 50.0
        if extra.get("language"):
            score += 20.0
        entities = extra.get("entities", {})
        if entities:
            score += min(len(entities.get("emails", [])) * 10, 20)
            score += min(len(entities.get("phones", [])) * 5, 10)
            score += min(len(entities.get("urls", [])) * 5, 10)
        return min(score, 100.0)

    @classmethod
    def _score_face_detection(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        total_faces = result.extra.get("total_faces", 0) if result.extra else 0
        return min(total_faces * 5.0, 100.0)

    @classmethod
    def _score_object_detection(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        total_objects = result.extra.get("total_objects", 0) if result.extra else 0
        unique_objects = result.extra.get("unique_objects", 0) if result.extra else 0
        score = min(total_objects * 0.5, 50) + min(unique_objects * 5, 50)
        return min(score, 100.0)

    @classmethod
    def _score_ocr_analysis(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        extra = result.extra or {}
        score = 0.0
        if extra.get("full_text"):
            score += 30.0

        emails = extra.get("emails", [])
        phones = extra.get("phones", [])
        urls = extra.get("urls", [])
        usernames = extra.get("usernames", [])

        if emails:
            score += min(len(emails) * 10, 30)
        if phones:
            score += min(len(phones) * 7, 20)
        if urls:
            score += min(len(urls) * 5, 15)
        if usernames:
            score += min(len(usernames) * 5, 15)

        return min(score, 100.0)

    @classmethod
    def _score_environment(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        evidence = result.extra.get("evidence", []) if result.extra else []
        return min(len(evidence) * 33.33, 100.0)

    @classmethod
    def _score_language(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        return (result.confidence or 0.0) * 100.0

    @classmethod
    def _score_landmark(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        total = result.extra.get("total_candidates", 0) if result.extra else 0
        return min(total * 25.0, 100.0)

    @classmethod
    def _score_timeline(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        total_events = result.extra.get("total_events", 0) if result.extra else 0
        return min(total_events * 2.0, 100.0)

    @classmethod
    def _score_geolocation(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        return (result.confidence or 0.0) * 100.0

    @classmethod
    def _score_risk_assessment(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        risk_level = result.extra.get("risk_level", "LOW") if result.extra else "LOW"
        mapping = {"MINIMAL": 0, "LOW": 25, "MEDIUM": 50, "HIGH": 100}
        return mapping.get(risk_level, 0.0)

    @classmethod
    def _score_entity_correlation(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        total_entities = result.extra.get("total_entities", 0) if result.extra else 0
        return min(total_entities * 10.0, 100.0)

    @classmethod
    def _score_confidence_engine(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        return (result.confidence or 0.0) * 100.0

    @classmethod
    def _score_ai(cls, result: ScanResult | None) -> float:
        if not result or result.status != "FOUND":
            return 0.0
        extra = result.extra or {}
        if extra.get("executive_summary"):
            return 100.0
        return 50.0