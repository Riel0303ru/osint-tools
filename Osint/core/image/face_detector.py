# core/image/face_detector.py
from __future__ import annotations

from typing import Dict, List, Any
import cv2
import numpy as np


class FaceDetector:
    """Detect faces in an image using OpenCV Haar Cascades."""

    @staticmethod
    def detect_faces(image_path: str) -> Dict[str, Any]:
        """
        Detect faces and return count plus bounding box coordinates.
        """
        try:
            # Load the cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {
                    "faces_detected": 0,
                    "coordinates": [],
                    "error": "Failed to load image",
                }

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            coordinates = []
            for x, y, w, h in faces:
                coordinates.append([int(x), int(y), int(w), int(h)])

            return {
                "faces_detected": len(faces),
                "coordinates": coordinates,
            }
        except ImportError:
            return {
                "faces_detected": 0,
                "coordinates": [],
                "error": "opencv-python not installed",
            }
        except Exception as e:
            return {
                "faces_detected": 0,
                "coordinates": [],
                "error": str(e),
            }