# core/username/correlators/confidence_engine.py
from __future__ import annotations

from typing import Dict, List, Optional
from core.base.scan_result import ScanResult


class ConfidenceEngine:
    """
    Menghitung confidence score untuk setiap hasil scan
    berdasarkan validasi konten, status code, dan metadata.
    """

    @staticmethod
    def calculate(results: List[ScanResult]) -> List[ScanResult]:
        """
        Menghitung ulang confidence setiap ScanResult dan mengembalikan list yang sama (dimodifikasi).
        """
        for r in results:
            # Confidence awal dari scanner
            base = r.confidence

            # Jika tidak ada extra, tetap
            if not r.extra:
                continue

            # Validasi konten sudah dilakukan oleh scanner, kita bisa menambah faktor
            if r.extra.get("verified_in_content"):
                base = min(1.0, base + 0.1)
            if r.extra.get("possible_false_positive"):
                base = max(0.1, base - 0.3)

            # Status code bukan 200 → lebih rendah
            if r.status_code and r.status_code != 200:
                base = max(0.05, base - 0.2)

            r.confidence = round(base, 3)

        return results