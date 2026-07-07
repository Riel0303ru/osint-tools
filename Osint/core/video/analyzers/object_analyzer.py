# core/video/analyzers/object_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
import cv2
from core.base.scan_result import ScanResult
from utils.logger import Logger


class ObjectAnalyzer:
    """
    Deteksi objek dalam frame menggunakan YOLOv8 (via ultralytics).
    Model diunduh otomatis pertama kali dan berjalan offline setelahnya.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.model = None

        try:
            from ultralytics import YOLO
            # Model nano: paling ringan, cocok untuk CPU
            self.model = YOLO("yolov8n.pt")
            self.logger.info("YOLOv8n loaded successfully (offline-ready)")
        except ImportError:
            self.logger.warning("ultralytics not installed. Install: pip install ultralytics")
            self.logger.warning("Fallback: object detection will not be available")
        except Exception as e:
            self.logger.error(f"Failed to load YOLOv8: {e}")
            self.model = None

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        """
        Deteksi objek di semua frame.
        """
        filename = os.path.basename(file_path)
        start_time = time.time()

        if self.model is None:
            return ScanResult(
                platform="Object Detection",
                username=filename,
                status="NOT_AVAILABLE",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={
                    "message": "YOLOv8 not available. Install: pip install ultralytics",
                    "install_command": "pip install ultralytics",
                },
            )

        all_objects = []
        object_counts = {}

        # Batasi 30 frame untuk performa
        frames_to_analyze = frame_paths[:30]

        for frame in frames_to_analyze:
            if not os.path.isfile(frame):
                continue

            try:
                results = self.model(frame, verbose=False)
                frame_name = os.path.basename(frame)

                for result in results:
                    boxes = result.boxes
                    if boxes is None:
                        continue

                    for box in boxes:
                        class_id = int(box.cls[0])
                        class_name = self.model.names[class_id]
                        confidence = float(box.conf[0])

                        if confidence > 0.4:  # threshold confidence
                            all_objects.append({
                                "frame": frame_name,
                                "object": class_name,
                                "confidence": round(confidence, 3),
                            })
                            object_counts[class_name] = object_counts.get(class_name, 0) + 1

            except Exception as e:
                self.logger.warning(f"Frame analysis failed: {e}")

        analysis_time = round(time.time() - start_time, 2)

        # Urutkan object counts dari terbanyak
        sorted_counts = dict(sorted(object_counts.items(), key=lambda x: x[1], reverse=True))

        return ScanResult(
            platform="Object Detection",
            username=filename,
            status="FOUND" if all_objects else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=0.95 if all_objects else 0.5,
            extra={
                "total_objects": len(all_objects),
                "object_counts": sorted_counts,
                "unique_objects": len(object_counts),
                "objects": all_objects[:200],
                "frames_analyzed": len(frames_to_analyze),
                "analysis_time_seconds": analysis_time,
                "method": "YOLOv8n (offline)",
            },
        )