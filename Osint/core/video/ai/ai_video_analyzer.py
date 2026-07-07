# core/video/ai/ai_video_analyzer.py
from __future__ import annotations

import os
import json
import time
from typing import List, Dict, Any, Optional
from core.base.scan_result import ScanResult
from utils.logger import Logger


class AIVideoAnalyzer:
    """
    AI-Powered Investigation Assistant menggunakan Google Gemini API.
    Menghasilkan executive summary, hipotesis lokasi, threat analysis,
    dan rekomendasi langkah investigasi selanjutnya.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.fallback_model = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

    def analyze(
        self,
        all_results: List[ScanResult],
        file_path: str = "",
    ) -> ScanResult:
        """
        Analisis semua hasil dan hasilkan ringkasan AI menggunakan Gemini.
        """
        filename = os.path.basename(file_path) if file_path else "unknown"
        findings = self._extract_findings(all_results)

        # Bangun prompt
        prompt = self._build_prompt(filename, findings)

        # Panggil Gemini API
        ai_summary = self._call_gemini(prompt)

        # Jika gagal, gunakan template fallback
        if not ai_summary:
            ai_summary = self._template_summary(findings, filename)

        return ScanResult(
            platform="AI Analysis",
            username=filename,
            status="FOUND",
            status_code=200,
            url=file_path,
            confidence=0.9 if ai_summary.get("executive_summary") else 0.5,
            extra={
                "executive_summary": ai_summary.get("executive_summary", ""),
                "investigation_summary": ai_summary.get("investigation_summary", ""),
                "location_hypothesis": ai_summary.get("location_hypothesis", ""),
                "timeline_summary": ai_summary.get("timeline_summary", ""),
                "threat_analysis": ai_summary.get("threat_analysis", ""),
                "risk_explanation": ai_summary.get("risk_explanation", ""),
                "recommended_steps": ai_summary.get("recommended_steps", []),
                "cross_module_insights": ai_summary.get("cross_module_insights", ""),
                "method": "gemini" if "gemini" in str(ai_summary.get("method", "")) else "template",
            },
        )

    def _extract_findings(self, results: List[ScanResult]) -> Dict[str, Any]:
        """Ekstrak temuan penting dari semua ScanResult."""
        findings = {
            "metadata": {},
            "faces": {},
            "objects": {},
            "ocr": {},
            "audio": {},
            "environment": {},
            "language": {},
            "geolocation": {},
            "risk": {},
        }
        for r in results:
            extra = r.extra or {}
            platform = r.platform
            if platform == "Video Metadata":
                findings["metadata"] = {
                    "duration": extra.get("duration_seconds"),
                    "resolution": extra.get("video", {}).get("resolution"),
                    "has_gps": bool(extra.get("gps", {}).get("raw")),
                }
            elif platform == "Face Detection":
                findings["faces"] = {"total": extra.get("total_faces", 0)}
            elif platform == "Object Detection":
                findings["objects"] = extra.get("object_counts", {})
            elif platform == "OCR Analysis":
                findings["ocr"] = {
                    "emails": extra.get("emails", [])[:5],
                    "phones": extra.get("phones", [])[:5],
                    "urls": extra.get("urls", [])[:5],
                    "text_sample": extra.get("full_text", "")[:300],
                }
            elif platform == "Audio Analysis":
                findings["audio"] = {
                    "transcript_sample": extra.get("transcript", "")[:300],
                    "language": extra.get("language"),
                }
            elif platform == "Environment Analysis":
                findings["environment"] = {
                    "setting": extra.get("indoor_outdoor"),
                    "time": extra.get("time_of_day"),
                    "weather": extra.get("weather"),
                }
            elif platform == "Language Analysis":
                findings["language"] = {
                    "detected": extra.get("combined_language"),
                    "confidence": extra.get("combined_confidence"),
                }
            elif platform == "Geolocation Analysis":
                findings["geolocation"] = {
                    "candidates": [
                        f"{c.get('country', '?')} (conf: {c.get('country_confidence', 0):.0%})"
                        for c in extra.get("candidates", [])[:3]
                    ],
                }
            elif platform == "Risk Assessment":
                findings["risk"] = {
                    "level": extra.get("threat_level"),
                    "score": extra.get("threat_score"),
                }
        return findings

    def _build_prompt(self, filename: str, findings: Dict[str, Any]) -> str:
        """Bangun prompt untuk Gemini."""
        return f"""You are an expert OSINT investigator. Analyze the following video intelligence data and provide a detailed report.

Video file: {filename}

Metadata: {json.dumps(findings.get('metadata', {}), indent=2)}
Environment: {json.dumps(findings.get('environment', {}), indent=2)}
Language: {json.dumps(findings.get('language', {}), indent=2)}
Geolocation candidates: {json.dumps(findings.get('geolocation', {}), indent=2)}
Faces detected: {json.dumps(findings.get('faces', {}), indent=2)}
Objects detected: {json.dumps(findings.get('objects', {}), indent=2)}
OCR extracts: {json.dumps(findings.get('ocr', {}), indent=2)}
Audio transcript (sample): {json.dumps(findings.get('audio', {}), indent=2)}
Risk Assessment: {json.dumps(findings.get('risk', {}), indent=2)}

Please provide a JSON response with these fields (do NOT include markdown code fences):
{{
  "executive_summary": "2-3 sentence summary of key findings",
  "investigation_summary": "detailed summary of what was found",
  "location_hypothesis": "where this video was likely recorded, with confidence and evidence",
  "timeline_summary": "summary of events in the video",
  "threat_analysis": "what threats or risks this video represents",
  "risk_explanation": "why the risk level is what it is",
  "recommended_steps": ["step 1", "step 2", ...],
  "cross_module_insights": "what other OSINT modules could be correlated with these findings"
}}"""

    def _call_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Panggil Gemini API dan parse respons JSON."""
        if not self.api_key:
            self.logger.warning("GEMINI_API_KEY not set – using template fallback")
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)

            if not response.text:
                return None

            # Bersihkan markdown code fences jika ada
            text = response.text.strip()
            if text.startswith("```"):
                # Hapus ```json ... ```
                lines = text.splitlines()
                lines = lines[1:-1] if lines[-1].startswith("```") else lines[1:]
                text = "\n".join(lines)

            parsed = json.loads(text)
            parsed["method"] = "gemini"
            return parsed

        except ImportError:
            self.logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Gemini response: {e}")
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")

        return None

    def _template_summary(self, findings: Dict, filename: str) -> Dict[str, Any]:
        """Fallback template jika Gemini gagal."""
        # ... (sama seperti sebelumnya) ...
        return {
            "executive_summary": f"Video '{filename}' analyzed with OSINT Fusion.",
            "investigation_summary": "No AI analysis available.",
            "location_hypothesis": "Unknown",
            "timeline_summary": "See Timeline Analysis",
            "threat_analysis": "Unknown",
            "risk_explanation": "Risk engine evaluated",
            "recommended_steps": ["Correlate with other modules"],
            "cross_module_insights": "Feed entities to Correlation Engine",
            "method": "template",
        }