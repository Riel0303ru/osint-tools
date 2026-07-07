# core/video/ai/ai_report_generator.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class AIReportGenerator:
    """Gunakan Gemini untuk menghasilkan laporan investigasi final."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    def generate_report(self, all_results: List[ScanResult], file_path: str = "") -> ScanResult:
        filename = os.path.basename(file_path) if file_path else "unknown"
        # Sari temuan penting
        report_data = {}
        for r in all_results:
            extra = r.extra or {}
            if r.platform == "AI Analysis" and extra.get("executive_summary"):
                report_data["executive_summary"] = extra["executive_summary"]
            if r.platform == "Geolocation Analysis":
                report_data["geolocation"] = extra.get("candidates", [])
            if r.platform == "Timeline Analysis":
                report_data["timeline_events"] = extra.get("events", [])[:10]
            if r.platform == "Risk Assessment":
                report_data["risk"] = {"level": extra.get("threat_level"), "score": extra.get("threat_score")}

        if not self.api_key:
            return ScanResult(
                platform="AI Report Generator",
                username=filename,
                status="NOT_AVAILABLE",
                status_code=0,
                url=file_path,
                confidence=0.0,
                extra={"error": "GEMINI_API_KEY not set"},
            )

        prompt = f"""You are an OSINT report generator. Create a structured investigation report (JSON) from the following data. Include sections: executive_summary, location_assessment, timeline_summary, risk_assessment, entities_found, recommended_actions.

Data: {json.dumps(report_data, indent=2)}

Respond with valid JSON only (no fences)."""

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            resp = model.generate_content(prompt)
            text = resp.text.strip()
            if text.startswith("```"):
                lines = text.splitlines()
                text = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else text
            report = json.loads(text)
        except Exception as e:
            self.logger.error(f"Gemini report generation failed: {e}")
            report = {"error": str(e), "executive_summary": "Report generation failed"}

        return ScanResult(
            platform="AI Report Generator",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=0.9,
            extra={"report": report, "method": "gemini"},
        )