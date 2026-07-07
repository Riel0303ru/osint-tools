# core/image/ocr_engine.py
from __future__ import annotations

import re
from typing import Dict, List, Optional


class OCREngine:
    """Optical Character Recognition using EasyOCR."""

    # Regex patterns
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_REGEX = re.compile(
        r"(\+?\d{1,3}[ -.]?)?\(?\d{2,4}\)?[ -.]?\d{2,4}[ -.]?\d{2,4}[ -.]?\d{2,4}"
    )
    USERNAME_REGEX = re.compile(r"@([a-zA-Z0-9._]{3,30})")
    URL_REGEX = re.compile(r"https?://[^\s]+")

    @staticmethod
    def extract_text(image_path: str) -> Dict:
        """
        Extract all text from image and detect emails, phones, usernames, and URLs.
        """
        try:
            import easyocr

            reader = easyocr.Reader(["en", "id"], gpu=False, verbose=False)
            results = reader.readtext(image_path, detail=0)
            raw_text = " ".join(results)
        except ImportError:
            return {
                "raw_text": "",
                "emails": [],
                "phones": [],
                "usernames": [],
                "urls": [],
                "error": "easyocr not installed. Run: pip install easyocr",
            }
        except Exception as e:
            return {
                "raw_text": "",
                "emails": [],
                "phones": [],
                "usernames": [],
                "urls": [],
                "error": str(e),
            }

        # Extract entities
        emails = list(set(OCREngine.EMAIL_REGEX.findall(raw_text)))
        phones = list(set(OCREngine.PHONE_REGEX.findall(raw_text)))
        # Filter out very short phone numbers
        phones = [p for p in phones if len(re.sub(r"\D", "", p)) >= 7]
        usernames = list(set(OCREngine.USERNAME_REGEX.findall(raw_text)))
        urls = list(set(OCREngine.URL_REGEX.findall(raw_text)))

        return {
            "raw_text": raw_text[:5000],  # limit to avoid huge output
            "emails": emails[:20],
            "phones": phones[:20],
            "usernames": usernames[:20],
            "urls": urls[:20],
            "total_characters": len(raw_text),
        }