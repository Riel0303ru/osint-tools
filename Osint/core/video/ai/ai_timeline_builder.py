# core/video/ai/ai_timeline_builder.py
from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class AITimelineBuilder:
    """Gunakan Gemini untuk menyusun narasi timeline."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    def build_narrative(self, timeline_result: Optional[ScanResult], file_path: str = "") -> ScanResult:
        filename = os.path.basename(file_path) if file_path else "unknown"
        if not timeline_result or timeline_result.status != "FOUND":
            return ScanResult(platform="AI Timeline Builder", username=filename, status="NOT_FOUND",
                              status_code=404, url=file_path, confidence=0.0,
                              extra={"error": "No timeline data"})

        events = timeline_result.extra.get("events", [])[:30]  # batasi
        if not events:
            return ScanResult(platform="AI Timeline Builder", username=filename, status="NOT_FOUND",
                              status_code=404, url=file_path, confidence=0.0,
                              extra={"error": "No events in timeline"})

        prompt = f"""You are an OSINT analyst. Convert the following timeline events into a concise narrative summary (3-5 paragraphs) describing what happened in the video chronologically. Include key observations.

Events: {json.dumps(events, indent=2)}

Respond with JSON (no markdown fences):
{{"narrative": "..."}}"""

        narrative = ""
        method = "template"
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model)
                resp = model.generate_content(prompt)
                text = resp.text.strip()
                if text.startswith("```"):
                    lines = text.splitlines()
                    text = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else text
                data = json.loads(text)
                narrative = data.get("narrative", "")
                method = "gemini"
            except Exception as e:
                self.logger.warning(f"Gemini timeline failed: {e}")

        if not narrative:
            # Fallback template
            narrative = f"Timeline contains {len(events)} events."
            method = "template"

        return ScanResult(
            platform="AI Timeline Builder",
            username=filename,
            status="FOUND" if narrative else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=0.85,
            extra={"narrative": narrative, "method": method},
        )