# core/document/extractors/docx_extractor.py
from __future__ import annotations

from typing import Dict, Any
import docx


class DOCXExtractor:
    """Ekstraktor untuk file DOCX."""

    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        result = {
            "metadata": {},
            "text": "",
            "paragraphs_count": 0,
        }

        try:
            doc = docx.Document(file_path)

            # Metadata
            props = doc.core_properties
            result["metadata"] = {
                "author": props.author,
                "created": str(props.created) if props.created else None,
                "modified": str(props.modified) if props.modified else None,
                "last_modified_by": props.last_modified_by,
                "revision": props.revision,
                "title": props.title,
                "subject": props.subject,
                "keywords": props.keywords,
                "category": props.category,
            }

            # Text
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            result["text"] = "\n".join(paragraphs)
            result["paragraphs_count"] = len(paragraphs)

        except Exception as e:
            result["error"] = str(e)

        return result