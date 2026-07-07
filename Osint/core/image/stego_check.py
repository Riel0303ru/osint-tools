# core/image/stego_check.py
from __future__ import annotations

from typing import Dict, Any
from PIL import Image
import numpy as np


class StegoCheck:
    """Basic steganography suspicion check using LSB entropy analysis."""

    @staticmethod
    def check_steganography(image_path: str) -> Dict[str, Any]:
        """
        Check for suspicious patterns that may indicate steganography.

        Returns:
            dict with keys:
                - suspicious (str): "True" if entropy suggests hidden data, else "False"
                - entropy_score (float): average entropy across R, G, B channels (0.0–1.0)
                - entropy_r, entropy_g, entropy_b (float): per-channel entropy
                - message (str): human-readable interpretation
        """
        try:
            img = Image.open(image_path).convert("RGB")
            pixels = np.array(img, dtype=np.uint8)

            # Use up to 10,000 pixels for better statistical sampling
            sample_size = min(10_000, pixels.shape[0] * pixels.shape[1])
            flat = pixels.reshape(-1, 3)[:sample_size]

            lsb_r = flat[:, 0] & 1
            lsb_g = flat[:, 1] & 1
            lsb_b = flat[:, 2] & 1

            # Proportion of 1s in each LSB channel
            prop_r = float(lsb_r.mean())
            prop_g = float(lsb_g.mean())
            prop_b = float(lsb_b.mean())

            # Entropy score: how close the proportion is to 0.5 (ideal randomness)
            # Score = 1 - 2 * |proportion - 0.5|
            entropy_r = 1.0 - abs(prop_r - 0.5) * 2.0
            entropy_g = 1.0 - abs(prop_g - 0.5) * 2.0
            entropy_b = 1.0 - abs(prop_b - 0.5) * 2.0

            avg_entropy = (entropy_r + entropy_g + entropy_b) / 3.0

            # Threshold: if average entropy > 0.7, LSB distribution is very random → suspicious
            suspicious = avg_entropy > 0.7

            return {
                "suspicious": str(suspicious),  # JSON-safe string
                "entropy_score": round(avg_entropy, 4),
                "entropy_r": round(entropy_r, 4),
                "entropy_g": round(entropy_g, 4),
                "entropy_b": round(entropy_b, 4),
                "message": (
                    "LSB pattern appears random – possible steganography"
                    if suspicious
                    else "LSB pattern appears normal"
                ),
            }
        except ImportError:
            return {
                "suspicious": "False",
                "entropy_score": 0.0,
                "error": "numpy or pillow not installed",
            }
        except Exception as e:
            return {
                "suspicious": "False",
                "entropy_score": 0.0,
                "error": str(e),
            }