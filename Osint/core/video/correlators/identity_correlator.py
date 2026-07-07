# core/video/correlators/identity_correlator.py
from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from core.video.models.video_entity import VideoEntity
from utils.logger import Logger


class IdentityCorrelator:
    """
    Menghubungkan temuan dari video (email, username, phone, wajah)
    ke potensi identitas individu. Membantu mengungkap pemilik/pelaku.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    def correlate(
        self,
        entities: List[VideoEntity],
        face_result: Optional[ScanResult] = None,
        ocr_result: Optional[ScanResult] = None,
        audio_analysis: Optional[ScanResult] = None,
        file_path: str = "",
    ) -> ScanResult:
        """
        Korelasikan entitas dan deteksi wajah untuk membangun
        kandidat identitas.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        identity_clues = []

        # 1. Kumpulkan email, username, phone sebagai identitas potensial
        for e in entities:
            if e.entity_type in ("email", "username", "phone"):
                identity_clues.append({
                    "type": e.entity_type,
                    "value": e.value,
                    "source": e.source,
                    "confidence": e.confidence,
                })

        # 2. Jumlah wajah dan clustering sederhana
        face_info = {}
        if face_result and face_result.status == "FOUND":
            face_info = {
                "total_faces": face_result.extra.get("total_faces", 0),
                "clusters": face_result.extra.get("clusters", []),
            }

        # 3. Hubungan: jika ada email + wajah, asumsikan identitas
        identity_candidates = []
        if identity_clues and face_info.get("total_faces", 0) > 0:
            identity_candidates.append({
                "clue_count": len(identity_clues),
                "clues": identity_clues,
                "faces": face_info["total_faces"],
                "hypothesis": "Possible identity based on email/username/phone and facial presence.",
            })

        analysis_time = round(time.time() - start_time, 2)

        return ScanResult(
            platform="Identity Correlation",
            username=filename,
            status="FOUND" if identity_candidates else "NOT_FOUND",
            status_code=200 if identity_candidates else 404,
            url=file_path,
            confidence=0.8 if identity_candidates else 0.3,
            extra={
                "identity_clues": identity_clues,
                "face_info": face_info,
                "identity_candidates": identity_candidates,
                "total_candidates": len(identity_candidates),
                "analysis_time_seconds": analysis_time,
                "ready_for_global_correlation": True,
            },
        )