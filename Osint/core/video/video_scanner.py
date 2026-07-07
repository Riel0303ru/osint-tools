# core/video/video_scanner.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any

from core.base.scan_result import ScanResult
from core.video.extractors.metadata_extractor import MetadataExtractor
from core.video.extractors.frame_extractor import FrameExtractor
from core.video.extractors.audio_extractor import AudioExtractor
from core.video.extractors.subtitle_extractor import SubtitleExtractor
from core.video.extractors.thumbnail_generator import ThumbnailGenerator
from core.video.extractors.gps_extractor import GPSExtractor
from core.video.analyzers.face_analyzer import FaceAnalyzer
from core.video.analyzers.object_analyzer import ObjectAnalyzer
from core.video.analyzers.ocr_analyzer import OCRAnalyzer
from core.video.analyzers.audio_analyzer import AudioAnalyzer
from core.video.analyzers.audio_background_analyzer import AudioBackgroundAnalyzer
from core.video.analyzers.environment_analyzer import EnvironmentAnalyzer
from core.video.analyzers.weather_analyzer import WeatherAnalyzer
from core.video.analyzers.scene_analyzer import SceneAnalyzer
from core.video.analyzers.object_tracker import ObjectTracker
from core.video.analyzers.language_analyzer import LanguageAnalyzer
from core.video.analyzers.timeline_analyzer import TimelineAnalyzer
from core.video.analyzers.landmark_analyzer import LandmarkAnalyzer
from core.video.analyzers.geolocation_analyzer import GeolocationAnalyzer
from core.video.analyzers.risk_engine import RiskEngine
from core.video.analyzers.confidence_engine import ConfidenceEngine
from core.video.correlators.entity_correlator import EntityCorrelator
from core.video.correlators.identity_correlator import IdentityCorrelator
from core.video.correlators.location_correlator import LocationCorrelator
from core.video.correlators.graph_correlator import GraphCorrelator
from core.video.providers.map_provider import MapProvider
from core.video.providers.geoint_provider import GeoINTProvider
from core.video.ai.ai_video_analyzer import AIVideoAnalyzer
from core.video.ai.ai_geoint_reasoner import AIGeoINTReasoner
from core.video.ai.ai_timeline_builder import AITimelineBuilder
from core.video.ai.ai_report_generator import AIReportGenerator
from core.video.video_report import VideoReport
from core.video.models.video_result import VideoResult
from utils.logger import Logger


class VideoScanner:
    """Orchestrator utama Video Intelligence – pipeline analisis video lengkap (28+ tahap)."""

    SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

        # Extractors
        self.metadata_extractor = MetadataExtractor(base_dir)
        self.frame_extractor = FrameExtractor(base_dir)
        self.audio_extractor = AudioExtractor(base_dir)
        self.subtitle_extractor = SubtitleExtractor(base_dir)
        self.thumbnail_generator = ThumbnailGenerator(base_dir)
        self.gps_extractor = GPSExtractor(base_dir)

        # Analyzers – visual & audio
        self.face_analyzer = FaceAnalyzer(base_dir)
        self.object_analyzer = ObjectAnalyzer(base_dir)
        self.ocr_analyzer = OCRAnalyzer(base_dir)
        self.environment_analyzer = EnvironmentAnalyzer(base_dir)
        self.weather_analyzer = WeatherAnalyzer(base_dir)
        self.scene_analyzer = SceneAnalyzer(base_dir)
        self.object_tracker = ObjectTracker(base_dir)
        self.audio_analyzer = AudioAnalyzer(base_dir)
        self.audio_background_analyzer = AudioBackgroundAnalyzer(base_dir)

        # Higher-level analysis
        self.language_analyzer = LanguageAnalyzer(base_dir)
        self.timeline_analyzer = TimelineAnalyzer(base_dir)
        self.landmark_analyzer = LandmarkAnalyzer(base_dir)
        self.geolocation_analyzer = GeolocationAnalyzer(base_dir)

        # Map & location providers
        self.map_provider = MapProvider(base_dir)
        self.geoint_provider = GeoINTProvider(base_dir)

        # Risk, Confidence, Correlation
        self.risk_engine = RiskEngine(base_dir)
        self.confidence_engine = ConfidenceEngine(base_dir)
        self.entity_correlator = EntityCorrelator(base_dir)
        self.identity_correlator = IdentityCorrelator(base_dir)
        self.location_correlator = LocationCorrelator(base_dir)
        self.graph_correlator = GraphCorrelator(base_dir)

        # AI
        self.ai_analyzer = AIVideoAnalyzer(base_dir)
        self.ai_geoint_reasoner = AIGeoINTReasoner(base_dir)
        self.ai_timeline_builder = AITimelineBuilder(base_dir)
        self.ai_report_generator = AIReportGenerator(base_dir)

        # Report (storage sudah di-handle oleh core/base/storage.py)
        self.video_report = VideoReport(base_dir)

        self.base_dir = base_dir

    async def scan(self, file_path: str) -> List[ScanResult]:
        """
        Jalankan seluruh pipeline Video Intelligence (28+ tahap).
        Mengembalikan daftar ScanResult yang mencakup setiap tahap.
        """
        self.logger.info(f"Scanning video → {file_path}")
        results: List[ScanResult] = []

        # ---------- 1. Validasi file ----------
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        if not os.path.isfile(file_path):
            return [ScanResult(
                platform="Video Validation",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": "File not found"}
            )]

        if ext not in self.SUPPORTED_EXTENSIONS:
            return [ScanResult(
                platform="Video Validation",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": f"Unsupported video format: {ext}"}
            )]

        # ---------- 2. Persiapan direktori output ----------
        safe_name = os.path.splitext(filename)[0]
        output_dir = os.path.join(self.base_dir, "results", "video", safe_name)
        frames_dir = os.path.join(output_dir, "frames")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(frames_dir, exist_ok=True)

        start_time = time.time()

        # ---------- 3. Metadata ----------
        metadata_result = self.metadata_extractor.extract(file_path)
        results.append(metadata_result)

        # ---------- 4. GPS Extraction ----------
        gps_result = self.gps_extractor.extract(metadata_result.extra, file_path)
        results.append(gps_result)

        # ---------- 5. Frame Extraction ----------
        frame_result = self.frame_extractor.extract(file_path, frames_dir, interval=2.0)
        results.append(frame_result)

        frames = frame_result.extra.get("frames", []) if frame_result.extra else []
        frame_paths = [f["path"] for f in frames if os.path.isfile(f["path"])]

        # ---------- 6. Thumbnail ----------
        thumbnail_result = self.thumbnail_generator.generate(file_path, output_dir)
        results.append(thumbnail_result)

        # ---------- 7. Audio Extraction ----------
        audio_result = self.audio_extractor.extract(file_path, output_dir)
        results.append(audio_result)
        audio_path = audio_result.extra.get("audio_path", "") if audio_result else ""

        # ---------- 8. Subtitle Extraction ----------
        subtitle_result = self.subtitle_extractor.extract(file_path, output_dir)
        results.append(subtitle_result)

        # ---------- 9. Visual Analyzers (frame-based) ----------
        face_result = object_result = ocr_result = env_result = weather_result = scene_result = tracking_result = landmark_result = None

        if frame_paths:
            face_result = self.face_analyzer.analyze(frame_paths, file_path)
            results.append(face_result)

            object_result = self.object_analyzer.analyze(frame_paths, file_path)
            results.append(object_result)

            ocr_result = self.ocr_analyzer.analyze(frame_paths, file_path)
            results.append(ocr_result)

            env_result = self.environment_analyzer.analyze(frame_paths, file_path)
            results.append(env_result)

            # 9.5 Weather Analysis
            weather_result = self.weather_analyzer.analyze(frame_paths, file_path)
            results.append(weather_result)

            # 9.6 Scene Analysis (indoor/outdoor, urban/rural, natural/built)
            scene_result = self.scene_analyzer.analyze(frame_paths, file_path)
            results.append(scene_result)

            # 9.7 Object Tracking
            tracking_result = self.object_tracker.analyze(frame_paths, file_path)
            results.append(tracking_result)

            # Landmark (menggunakan teks OCR + Vision API jika tersedia)
            ocr_text_for_landmark = ""
            if ocr_result and ocr_result.status == "FOUND":
                ocr_text_for_landmark = ocr_result.extra.get("full_text", "")
            landmark_result = self.landmark_analyzer.analyze(
                frame_paths=frame_paths,
                ocr_text=ocr_text_for_landmark,
                file_path=file_path,
            )
            results.append(landmark_result)
        else:
            self.logger.warning("No frames extracted; visual analyzers skipped.")

        # ---------- 10. Audio Analysis (Transkripsi) ----------
        audio_analysis = self.audio_analyzer.analyze(audio_path, file_path)
        results.append(audio_analysis)

        # ---------- 11. Audio Background Sound Detection ----------
        audio_bg_result = self.audio_background_analyzer.analyze(audio_path, file_path)
        results.append(audio_bg_result)

        # ---------- 12. Language Analysis ----------
        ocr_text = ""
        if ocr_result and ocr_result.status == "FOUND":
            ocr_text = ocr_result.extra.get("full_text", "")

        audio_transcript = ""
        if audio_analysis and audio_analysis.status in ("FOUND", "SUCCESS"):
            audio_transcript = audio_analysis.extra.get("transcript", "")

        lang_result = self.language_analyzer.analyze(
            ocr_text=ocr_text,
            audio_transcript=audio_transcript,
            file_path=file_path,
        )
        results.append(lang_result)

        # ---------- 13. Timeline ----------
        timeline_result = self.timeline_analyzer.analyze(
            frame_results=frame_result,
            face_results=face_result,
            object_results=object_result,
            ocr_results=ocr_result,
            audio_results=audio_analysis,
            env_results=env_result,
            file_path=file_path,
        )
        results.append(timeline_result)

        # ---------- 14. Geolocation ----------
        geolocation_result = self.geolocation_analyzer.analyze(
            metadata_result=metadata_result,
            language_result=lang_result,
            environment_result=env_result,
            landmark_result=landmark_result,
            file_path=file_path,
        )
        results.append(geolocation_result)

        # ---------- 15. AI GeoINT Reasoner (reasoning chain lokasi) ----------
        ai_geoint_result = self.ai_geoint_reasoner.reason(
            geolocation_result=geolocation_result,
            language_result=lang_result,
            environment_result=env_result,
            landmark_result=landmark_result,
            weather_result=weather_result,
            file_path=file_path,
        )
        results.append(ai_geoint_result)

        # ---------- 16. Map Provider (jika ada GPS) ----------
        map_result = None
        if gps_result and gps_result.status == "FOUND":
            lat = gps_result.extra.get("latitude")
            lon = gps_result.extra.get("longitude")
            if lat is not None and lon is not None:
                address = self.map_provider.reverse_geocode(lat, lon)
                links = self.map_provider.get_map_links(lat, lon)
                map_result = ScanResult(
                    platform="Map Provider",
                    username=filename,
                    status="FOUND",
                    status_code=200,
                    url=file_path,
                    confidence=0.95,
                    extra={
                        "latitude": lat,
                        "longitude": lon,
                        "address": address,
                        "map_links": links,
                    },
                )
            else:
                map_result = ScanResult(
                    platform="Map Provider",
                    username=filename,
                    status="NOT_FOUND",
                    status_code=404,
                    url=file_path,
                    confidence=0.0,
                    extra={"error": "GPS coordinates incomplete"},
                )
        else:
            map_result = ScanResult(
                platform="Map Provider",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "No GPS coordinates available"},
            )
        results.append(map_result)

        # ---------- 17. Risk Assessment (termasuk SafeSearch) ----------
        risk_result = self.risk_engine.analyze(
            metadata_result=metadata_result,
            ocr_result=ocr_result,
            face_result=face_result,
            object_result=object_result,
            environment_result=env_result,
            geolocation_result=geolocation_result,
            language_result=lang_result,
            frame_paths=frame_paths,      # <-- dikirim untuk SafeSearch (Vision API)
            file_path=file_path,
        )
        results.append(risk_result)

        # ---------- 18. Entity Correlation ----------
        entities = self.entity_correlator.collect_entities(
            metadata_result=metadata_result,
            ocr_result=ocr_result,
            audio_analysis=audio_analysis,
            language_result=lang_result,
            geolocation_result=geolocation_result,
            risk_result=risk_result,
            file_path=file_path,
        )
        entity_corr_result = self.entity_correlator.correlate_and_report(
            entities=entities,
            file_path=file_path,
        )
        results.append(entity_corr_result)

        # ---------- 19. Identity Correlation ----------
        identity_corr_result = self.identity_correlator.correlate(
            entities=entities,
            face_result=face_result,
            ocr_result=ocr_result,
            audio_analysis=audio_analysis,
            file_path=file_path,
        )
        results.append(identity_corr_result)

        # ---------- 20. Location Correlation ----------
        location_corr_result = self.location_correlator.correlate(
            gps_result=gps_result,
            geolocation_result=geolocation_result,
            environment_result=env_result,
            language_result=lang_result,
            landmark_result=landmark_result,
            file_path=file_path,
        )
        results.append(location_corr_result)

        # ---------- 21. Graph Correlation (hubungkan ke global) ----------
        graph_result = self.graph_correlator.push_to_global_graph(
            entities=entities,
            identity_corr=identity_corr_result,
            location_corr=location_corr_result,
            file_path=file_path,
        )
        results.append(graph_result)

        # ---------- 22. Confidence Engine ----------
        confidence_result = self.confidence_engine.analyze(
            results=results,
            file_path=file_path,
        )
        results.append(confidence_result)

        # ---------- 23. AI Timeline Builder (narasi timeline) ----------
        ai_timeline_result = self.ai_timeline_builder.build_narrative(
            timeline_result=timeline_result,
            file_path=file_path,
        )
        results.append(ai_timeline_result)

        # ---------- 24. AI Analysis ----------
        ai_result = self.ai_analyzer.analyze(
            all_results=results,
            file_path=file_path,
        )
        results.append(ai_result)

        # ---------- 25. AI Report Generator ----------
        ai_report_result = self.ai_report_generator.generate_report(
            all_results=results,
            file_path=file_path,
        )
        results.append(ai_report_result)

        # ---------- Selesai ----------
        total_time = round(time.time() - start_time, 2)
        self.logger.success(
            f"Video scan completed → {filename} ({len(results)} stages) in {total_time}s"
        )
        return results