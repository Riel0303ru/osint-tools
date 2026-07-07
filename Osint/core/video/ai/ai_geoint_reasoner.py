# core/video/ai/ai_geoint_reasoner.py
from __future__ import annotations

import os
import json
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class AIGeoINTReasoner:
    """
    AI-powered Geolocation Reasoner menggunakan Google Gemini.
    Menganalisis semua petunjuk visual dan audio untuk menyimpulkan lokasi
    dengan reasoning chain yang dapat dijelaskan.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    def reason(
        self,
        geolocation_result: Optional[ScanResult],
        language_result: Optional[ScanResult],
        environment_result: Optional[ScanResult],
        landmark_result: Optional[ScanResult],
        weather_result: Optional[ScanResult],
        file_path: str = "",
    ) -> ScanResult:
        filename = os.path.basename(file_path) if file_path else "unknown"
        start_time = time.time()

        # Kumpulkan petunjuk
        clues = {
            "geolocation_candidates": geolocation_result.extra.get("candidates", []) if geolocation_result else [],
            "language": language_result.extra.get("combined_language") if language_result else None,
            "environment": environment_result.extra if environment_result else {},
            "landmarks": landmark_result.extra.get("candidates", []) if landmark_result else [],
            "weather": weather_result.extra.get("weather") if weather_result else None,
        }

        # Jika tidak ada petunjuk, return early
        if not any([clues["geolocation_candidates"], clues["language"], clues["landmarks"], clues["environment"]]):
            return ScanResult(
                platform="AI GeoINT Reasoner",
                username=filename,
                status="NOT_FOUND",
                status_code=404,
                url=file_path,
                confidence=0.0,
                extra={"error": "No geolocation clues available"},
            )

        # Coba Gemini
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)

                prompt = self._build_prompt(clues)
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                text = response.text.strip()
                if text.startswith("```"):
                    lines = text.splitlines()
                    text = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else text[3:]
                data = json.loads(text)
                reasoning = data.get("reasoning", "")
                candidates = data.get("candidates", [])
                confidence = data.get("confidence", 0.7)
                method = "gemini"
            except Exception as e:
                self.logger.error(f"Gemini GeoINT failed: {e}")
                reasoning, candidates, confidence, method = self._fallback_reason(clues)
        else:
            reasoning, candidates, confidence, method = self._fallback_reason(clues)

        analysis_time = round(time.time() - start_time, 2)
        return ScanResult(
            platform="AI GeoINT Reasoner",
            username=filename,
            status="FOUND" if candidates else "NOT_FOUND",
            status_code=200,
            url=file_path,
            confidence=confidence,
            extra={
                "reasoning": reasoning,
                "candidates": candidates,
                "analysis_time_seconds": analysis_time,
                "method": method,
            },
        )

    def _build_prompt(self, clues: Dict) -> str:
        return f"""You are a GEOINT expert. Based on the following clues extracted from a video, determine the most likely location(s).

Clues:
- Geolocation candidates from other analyzers: {json.dumps(clues['geolocation_candidates'])}
- Detected language: {clues['language']}
- Environment: indoor/outdoor: {clues['environment'].get('indoor_outdoor')}, time: {clues['environment'].get('time_of_day')}, weather: {clues['environment'].get('weather')}
- Landmark hints: {json.dumps(clues['landmarks'])}
- Weather: {clues['weather']}

Provide a JSON response (no markdown fences) with these fields:
{{
  "reasoning": "step-by-step reasoning chain explaining how you arrived at the conclusion",
  "candidates": [
    {{"country": "...", "region": "...", "city": "...", "confidence": 0.XX, "evidence": ["..."]}}
  ],
  "confidence": 0.XX
}}"""

    def _fallback_reason(self, clues: Dict) -> tuple:
        reasoning = "Fallback heuristic: "
        candidates = []
        confidence = 0.5
        if clues["language"] == "id":
            reasoning += "Indonesian language detected. Likely Indonesia."
            candidates.append({"country": "Indonesia", "confidence": 0.9, "evidence": ["Indonesian language"]})
            confidence = 0.9
        elif clues["language"] == "en":
            reasoning += "English detected. Could be US, UK, AU, etc."
            candidates.append({"country": "English-speaking country", "confidence": 0.5})
        if clues["weather"]:
            reasoning += f" Weather: {clues['weather']}."
        return reasoning, candidates, confidence, "template"