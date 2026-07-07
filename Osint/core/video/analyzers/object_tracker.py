# core/video/analyzers/object_tracker.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from core.base.scan_result import ScanResult
from utils.logger import Logger


class ObjectTracker:
    """
    Melacak pergerakan objek antar frame menggunakan tracking sederhana
    (centroid-based association). Menghasilkan trajectory dan frekuensi.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        if not frame_paths:
            return ScanResult(
                platform="Object Tracking",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "No frames available"},
            )

        # Gunakan deteksi objek dari ObjectAnalyzer (atau YOLO langsung)
        # Di sini kita gunakan YOLOv8 untuk deteksi di setiap frame, lalu track
        try:
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt")
        except ImportError:
            return ScanResult(
                platform="Object Tracking",
                username=filename,
                status="NOT_AVAILABLE",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": "YOLOv8 not available. Install: pip install ultralytics"},
            )

        tracks: Dict[int, List[Dict]] = {}  # track_id -> [frame_idx, centroid, class, conf]
        next_id = 0

        for i, frame_path in enumerate(frame_paths[:30]):
            img = cv2.imread(frame_path)
            if img is None:
                continue
            results = model(frame_path, verbose=False)
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                for box in boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    if confidence < 0.5:
                        continue
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    centroid = ((x1 + x2) / 2, (y1 + y2) / 2)

                    # Asosiasi dengan track existing (IoU sederhana)
                    assigned = False
                    for tid, track in tracks.items():
                        if track[-1]["frame_index"] == i - 1:  # hanya dari frame sebelumnya
                            prev_bbox = track[-1]["bbox"]
                            iou = self._iou(prev_bbox, [x1, y1, x2, y2])
                            if iou > 0.3:
                                track.append({
                                    "frame_index": i,
                                    "timestamp": i * 2.0,
                                    "bbox": [x1, y1, x2, y2],
                                    "centroid": centroid,
                                    "class": class_name,
                                    "confidence": confidence,
                                })
                                assigned = True
                                break
                    if not assigned:
                        tracks[next_id] = [{
                            "frame_index": i,
                            "timestamp": i * 2.0,
                            "bbox": [x1, y1, x2, y2],
                            "centroid": centroid,
                            "class": class_name,
                            "confidence": confidence,
                        }]
                        next_id += 1

        # Filter tracks dengan >= 2 frame
        valid_tracks = {tid: t for tid, t in tracks.items() if len(t) >= 2}
        total_tracks = len(valid_tracks)

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Object Tracking",
            username=filename,
            status="FOUND" if valid_tracks else "NOT_FOUND",
            status_code=200 if valid_tracks else 404,
            url=file_path,
            confidence=0.85 if valid_tracks else 0.5,
            extra={
                "total_tracks": total_tracks,
                "tracks": {str(tid): t for tid, t in list(valid_tracks.items())[:20]},
                "analysis_time_seconds": analysis_time,
                "method": "YOLOv8 + Centroid-based tracking",
            },
        )

    @staticmethod
    def _iou(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-9)
        return iou