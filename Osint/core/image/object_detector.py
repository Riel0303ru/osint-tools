# core/image/object_detector.py
from __future__ import annotations

from typing import Dict, Any


class ObjectDetector:
    """
    Object detection placeholder.
    Future support: YOLO, HuggingFace Vision, Transformers.
    """

    @staticmethod
    def detect_objects(image_path: str) -> Dict[str, Any]:
        """
        Detect objects in image. Currently NOT_IMPLEMENTED.
        """
        return {
            "status": "NOT_IMPLEMENTED",
            "objects": [],
            "message": "Object detection module planned for future release",
        }