# core/video/extractors/metadata_extractor.py
from __future__ import annotations

import os
from typing import Dict, Any, List
from core.base.scan_result import ScanResult
from core.video.providers.ffmpeg_provider import FFmpegProvider


class MetadataExtractor:
    """Ekstraktor metadata video dengan deteksi manipulasi."""

    def __init__(self, base_dir: str = "Osint"):
        self.ffmpeg = FFmpegProvider(base_dir)

    def extract(self, file_path: str) -> ScanResult:
        """Ekstrak metadata dan kembalikan sebagai ScanResult."""
        filename = os.path.basename(file_path)
        metadata = self.ffmpeg.get_metadata(file_path)

        if "error" in metadata:
            return ScanResult(
                platform="Video Metadata",
                username=filename,
                status="ERROR",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": metadata["error"]},
            )

        # Deteksi manipulasi
        integrity = self._detect_manipulation(metadata)

        return ScanResult(
            platform="Video Metadata",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=0.95,
            extra={
                **metadata,
                "integrity_check": integrity,
            },
        )

    @staticmethod
    def _detect_manipulation(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Deteksi tanda-tanda manipulasi metadata."""
        findings = []
        tags = metadata.get("tags", {})

        # Cek apakah ada tanggal yang tidak konsisten
        creation_time = tags.get("creation_time", "")
        if not creation_time:
            findings.append("No creation time found – possible metadata removal")

        # Cek software encoder
        encoder = tags.get("encoder", "")
        if encoder and any(w in encoder.lower() for w in ["obs", "shotcut", "capcut"]):
            findings.append(f"Edited with {encoder}")

        return {
            "suspicious": len(findings) > 0,
            "findings": findings,
            "confidence": max(0.5, 1.0 - len(findings) * 0.2),
        }