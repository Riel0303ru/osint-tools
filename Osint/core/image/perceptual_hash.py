# core/image/perceptual_hash.py
from __future__ import annotations

from typing import Dict, Any
from PIL import Image
import imagehash


class PerceptualHash:
    """Generate perceptual hash for image deduplication."""

    @staticmethod
    def generate_hash(image_path: str) -> Dict[str, Any]:
        """
        Generate pHash for the given image.
        """
        try:
            img = Image.open(image_path)
            phash = str(imagehash.phash(img))
            dhash = str(imagehash.dhash(img))
            ahash = str(imagehash.average_hash(img))

            return {
                "hash": phash,
                "phash": phash,
                "dhash": dhash,
                "ahash": ahash,
                "algorithm": "phash (primary)",
            }
        except ImportError:
            return {
                "hash": "",
                "error": "imagehash not installed",
            }
        except Exception as e:
            return {
                "hash": "",
                "error": str(e),
            }