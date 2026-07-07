# core/document/document_scanner.py
from __future__ import annotations

import os
import hashlib
import time
from typing import Dict, Any, List
from pathlib import Path

from core.document.extractors.pdf_extractor import PDFExtractor
from core.document.extractors.docx_extractor import DOCXExtractor
from core.document.extractors.xlsx_extractor import XLSXExtractor
from core.document.extractors.pptx_extractor import PPTXExtractor
from core.document.extractors.txt_extractor import TXTExtractor
from core.document.analyzers.metadata_analyzer import MetadataAnalyzer
from core.document.analyzers.sensitive_data_detector import SensitiveDataDetector
from core.document.analyzers.security_analyzer import SecurityAnalyzer
from core.base.scan_result import ScanResult
from utils.logger import Logger


class DocumentScanner:
    """Orchestrator utama Document Intelligence."""

    EXTRACTORS = {
        ".pdf": PDFExtractor,
        ".docx": DOCXExtractor,
        ".xlsx": XLSXExtractor,
        ".pptx": PPTXExtractor,
        ".txt": TXTExtractor,
    }

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def scan(self, file_path: str) -> List[ScanResult]:
        """
        Pindai dokumen dan kembalikan list ScanResult.
        """
        self.logger.info(f"Scanning document -> {file_path}")

        # 1. Validasi
        if not os.path.isfile(file_path):
            return [
                ScanResult(
                    platform="Document Validation",
                    username=os.path.basename(file_path),
                    status="ERROR",
                    status_code=0,
                    url=file_path,
                    confidence=0.0,
                    extra={"error": "File not found"},
                )
            ]

        filename = os.path.basename(file_path)
        ext = Path(file_path).suffix.lower()

        if ext not in self.EXTRACTORS:
            return [
                ScanResult(
                    platform="Document Validation",
                    username=filename,
                    status="ERROR",
                    status_code=0,
                    url=file_path,
                    confidence=0.0,
                    extra={"error": f"Unsupported file type: {ext}"},
                )
            ]

        results = []

        # 2. File Information
        file_info = self._get_file_info(file_path)
        results.append(ScanResult(
            platform="File Information",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=1.0,
            extra=file_info,
        ))

        # 3. Ekstraksi
        extractor = self.EXTRACTORS[ext]()
        start_time = time.time()
        extract_result = extractor.extract(file_path)
        extraction_time = round(time.time() - start_time, 2)

        results.append(ScanResult(
            platform=f"{ext.upper()[1:]} Extraction",
            username=filename,
            status="FOUND" if "error" not in extract_result else "ERROR",
            status_code=200 if "error" not in extract_result else 500,
            url=file_path,
            confidence=0.95 if "error" not in extract_result else 0.0,
            extra={**extract_result, "extraction_time_seconds": extraction_time},
        ))

        # 4. Metadata Analysis
        metadata = extract_result.get("metadata", {})
        if metadata:
            meta_analysis = MetadataAnalyzer.analyze(metadata)
            results.append(ScanResult(
                platform="Metadata Analysis",
                username=filename,
                status="FOUND",
                status_code=200,
                url=file_path,
                confidence=0.9,
                extra=meta_analysis,
            ))

        # 5. Sensitive Data Detection
        text = extract_result.get("text", "")
        sensitive = SensitiveDataDetector.detect(text)
        has_sensitive = any(v for v in sensitive.values() if v)
        results.append(ScanResult(
            platform="Sensitive Data Detection",
            username=filename,
            status="FOUND" if has_sensitive else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=0.95 if has_sensitive else 0.5,
            extra=sensitive,
        ))

        # 6. Security Analysis
        security = SecurityAnalyzer.analyze(file_path, extract_result)
        results.append(ScanResult(
            platform="Security Analysis",
            username=filename,
            status="FOUND" if security["total_findings"] > 0 else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=0.9,
            extra=security,
        ))

        self.logger.success(f"Document scan completed -> {filename}")
        return results

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Kumpulkan informasi file."""
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)

        # Hash
        with open(file_path, "rb") as f:
            content = f.read()
            md5_hash = hashlib.md5(content).hexdigest()
            sha256_hash = hashlib.sha256(content).hexdigest()

        return {
            "filename": filename,
            "file_path": file_path,
            "file_size_bytes": stat.st_size,
            "file_type": Path(file_path).suffix.lower(),
            "md5": md5_hash,
            "sha256": sha256_hash,
            "created": str(time.ctime(stat.st_ctime)),
            "modified": str(time.ctime(stat.st_mtime)),
        }