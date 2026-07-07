# core/document/extractors/pdf_extractor.py
from __future__ import annotations

import hashlib
from typing import Dict, Any, Optional
import fitz  # pymupdf


class PDFExtractor:
    """Ekstraktor untuk file PDF."""

    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        result = {
            "metadata": {},
            "text": "",
            "pages": 0,
            "embedded_files": [],
            "images_count": 0,
            "links": [],
        }

        try:
            doc = fitz.open(file_path)
            result["pages"] = len(doc)
            result["metadata"] = dict(doc.metadata) if doc.metadata else {}

            full_text = []
            for page in doc:
                full_text.append(page.get_text())
                # Ekstrak link
                for link in page.get_links():
                    if link.get("uri"):
                        result["links"].append(link["uri"])
                # Hitung gambar
                result["images_count"] += len(page.get_images())

            result["text"] = "\n".join(full_text)

            # Embedded files
            for i in range(doc.embfile_count()):
                info = doc.embfile_info(i)
                if info:
                    result["embedded_files"].append(info.get("filename", f"embedded_{i}"))

            doc.close()
        except Exception as e:
            result["error"] = str(e)

        return result