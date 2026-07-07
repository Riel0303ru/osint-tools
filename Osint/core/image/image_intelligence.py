# core/image/image_intelligence.py
from __future__ import annotations

from typing import Dict


class ImageIntelligence:
    """
    Intelligence scoring for image analysis.
    Higher score = more OSINT value found.
    """

    @staticmethod
    def calculate(results: Dict) -> float:
        score = 0.0

        # OCR findings
        ocr = results.get("ocr", {})
        if ocr.get("usernames"):
            score += min(len(ocr["usernames"]) * 10, 20)
        if ocr.get("emails"):
            score += min(len(ocr["emails"]) * 15, 30)
        if ocr.get("phones"):
            score += min(len(ocr["phones"]) * 10, 20)
        if ocr.get("urls"):
            score += min(len(ocr["urls"]) * 5, 10)

        # EXIF GPS
        exif = results.get("exif", {})
        if exif.get("gps") == "FOUND":
            score += 20

        # Face detection
        faces = results.get("faces", {})
        if faces.get("faces_detected", 0) > 0:
            score += min(faces["faces_detected"] * 5, 15)

        # Metadata
        if exif.get("camera"):
            score += 5
        if exif.get("datetime"):
            score += 5

        # Steganography suspicion
        stego = results.get("steganography", {})
        if stego.get("suspicious"):
            score += 10

        return min(score, 100.0)