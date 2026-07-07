# core/video/analyzers/scene_analyzer.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any
import cv2
import numpy as np
from core.base.scan_result import ScanResult
from utils.logger import Logger


class SceneAnalyzer:
    """
    Klasifikasi tipe scene: indoor/outdoor, urban/rural, natural/built.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def analyze(self, frame_paths: List[str], file_path: str) -> ScanResult:
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()
        if not frame_paths:
            return ScanResult(platform="Scene Analysis", username=filename, status="NOT_FOUND",
                              status_code=404, url=file_path, confidence=0.0, extra={"error": "No frames"})

        indoor = outdoor = urban = rural = natural = built = 0
        total = 0
        for fp in frame_paths[:20]:
            img = cv2.imread(fp)
            if img is None:
                continue
            total += 1
            i, o, u, r, n, b = self._classify(img)
            indoor += i; outdoor += o; urban += u; rural += r; natural += n; built += b

        majority_io = "indoor" if indoor >= outdoor else "outdoor"
        majority_ur = "urban" if urban >= rural else "rural"
        majority_nb = "natural" if natural >= built else "built"

        confidence = (max(indoor, outdoor) + max(urban, rural) + max(natural, built)) / (3 * total) if total else 0
        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Scene Analysis",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=round(confidence, 2),
            extra={
                "indoor_outdoor": majority_io,
                "urban_rural": majority_ur,
                "natural_built": majority_nb,
                "indoor_frames": indoor, "outdoor_frames": outdoor,
                "urban_frames": urban, "rural_frames": rural,
                "natural_frames": natural, "built_frames": built,
                "total_frames": total,
                "analysis_time_seconds": analysis_time,
                "method": "Color histogram & texture analysis",
            },
        )

    def _classify(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = np.mean(gray)
        saturation = np.mean(hsv[:,:,1])

        # Indoor/outdoor
        indoor = 1 if brightness < 80 else 0
        outdoor = 1 - indoor

        # Urban/rural: urban biasanya memiliki banyak edge vertikal/horisontal (bangunan)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.mean(edges) / 255.0
        # Hijau dominan => rural
        h = hsv[:,:,0]
        green_mask = (h > 35) & (h < 85)
        green_ratio = np.mean(green_mask)
        if green_ratio > 0.2 or edge_density < 0.05:
            urban, rural = 0, 1
        else:
            urban, rural = 1, 0

        # Natural vs built: built memiliki banyak struktur lurus, natural lebih acak
        if edge_density > 0.1 and green_ratio < 0.1:
            natural, built = 0, 1
        else:
            natural, built = 1, 0

        return indoor, outdoor, urban, rural, natural, built