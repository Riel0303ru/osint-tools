# core/document/extractors/txt_extractor.py
from __future__ import annotations

from typing import Dict, Any


class TXTExtractor:
    """Ekstraktor untuk file TXT."""

    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        result = {
            "metadata": {},
            "text": "",
            "lines_count": 0,
        }

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            result["text"] = text
            result["lines_count"] = len(text.splitlines())
        except Exception as e:
            result["error"] = str(e)

        return result