# core/ai/ai_analyzer.py
from __future__ import annotations

import asyncio
import json
from typing import Dict, Any, Optional

import httpx

from utils.config_manager import ConfigManager


class AIAnalyzer:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        self.api_key = ConfigManager.get_env(
            "GEMINI_API_KEY"
        )

        # PRIMARY MODEL
        self.model = ConfigManager.get_env(
            "GEMINI_MODEL",
            "gemini-1.5-flash"
        )

        # FALLBACK MODEL
        self.fallback_model = ConfigManager.get_env(
            "GEMINI_FALLBACK_MODEL",
            "gemini-1.5-flash"
        )

        # API SETTINGS
        self.timeout = 120
        self.max_retries = 3

        # PROMPT SAFETY
        self.max_prompt_length = 12000

    # =========================================================
    # URL BUILDER
    # =========================================================

    def build_url(self, model: str) -> str:

        return (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
        )

    # =========================================================
    # PROMPT SANITIZER
    # =========================================================

    def sanitize_prompt(
        self,
        prompt: str
    ) -> str:

        if not prompt:
            return "No prompt provided."

        # HARD LIMIT
        prompt = prompt[:self.max_prompt_length]

        return prompt.strip()

    # =========================================================
    # REQUEST PAYLOAD
    # =========================================================

    def build_payload(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        return {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

    # =========================================================
    # HEADERS
    # =========================================================

    def build_headers(self) -> Dict[str, str]:

        return {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

    # =========================================================
    # REQUEST ENGINE
    # =========================================================

    async def send_request(
        self,
        model: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        url = self.build_url(model)

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.post(
                url,
                headers=self.build_headers(),
                json=payload
            )

            response.raise_for_status()

            return response.json()

    # =========================================================
    # RESPONSE TEXT EXTRACTOR
    # =========================================================

    def extract_text(
        self,
        data: Dict[str, Any]
    ) -> str:

        try:

            return (
                data["candidates"][0]
                ["content"]["parts"][0]
                ["text"]
            )

        except Exception:

            return str(data)

    # =========================================================
    # MARKDOWN CLEANER
    # =========================================================

    def clean_markdown_json(
        self,
        text: str
    ) -> str:

        if "```json" in text:

            text = (
                text
                .split("```json")[1]
                .split("```")[0]
                .strip()
            )

        elif "```" in text:

            text = (
                text
                .split("```")[1]
                .split("```")[0]
                .strip()
            )

        return text

    # =========================================================
    # JSON PARSER
    # =========================================================

    def parse_analysis(
        self,
        text: str
    ) -> Dict[str, Any]:

        cleaned_text = self.clean_markdown_json(text)

        try:

            parsed = json.loads(cleaned_text)

            return {
                "summary": parsed.get("summary", ""),
                "risk_level": parsed.get("risk_level", "unknown"),
                "risk_score": parsed.get("risk_score", 0),
                "correlations": parsed.get("correlations", []),
                "suspicious_findings": parsed.get(
                    "suspicious_findings",
                    []
                ),
                "confidence_estimate": parsed.get(
                    "confidence_estimate",
                    0
                ),
                "insights": parsed.get("insights", []),
                "narrative": parsed.get("narrative", "")
            }

        except Exception:

            # FALLBACK NARRATIVE MODE
            return {
                "summary": (
                    "AI returned narrative output "
                    "instead of structured JSON."
                ),
                "risk_level": "unknown",
                "risk_score": 0,
                "correlations": [],
                "suspicious_findings": [],
                "confidence_estimate": 0,
                "insights": [],
                "narrative": cleaned_text
            }

    # =========================================================
    # MAIN ANALYSIS ENGINE
    # =========================================================

    async def analyze(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        # ============================================
        # API KEY CHECK
        # ============================================

        if not self.api_key:

            return {
                "success": False,
                "error": "Gemini API key is missing."
            }

        # ============================================
        # SANITIZE
        # ============================================

        prompt = self.sanitize_prompt(prompt)

        payload = self.build_payload(prompt)

        models = [
            self.model,
            self.fallback_model
        ]

        # ============================================
        # MODEL LOOP
        # ============================================

        for model in models:

            # ========================================
            # RETRY LOOP
            # ========================================

            for attempt in range(self.max_retries):

                try:

                    data = await self.send_request(
                        model=model,
                        payload=payload
                    )

                    text = self.extract_text(data)

                    analysis = self.parse_analysis(text)

                    return {
                        "success": True,
                        "model": model,
                        "raw": data,
                        "analysis": analysis
                    }

                # ====================================
                # HTTP ERRORS
                # ====================================

                except httpx.HTTPStatusError as e:

                    status = e.response.status_code

                    # RATE LIMIT
                    if status == 429:

                        wait_time = 2 ** attempt

                        print(
                            f"[RATE LIMIT] "
                            f"Retrying in {wait_time}s..."
                        )

                        await asyncio.sleep(wait_time)

                        continue

                    # BAD REQUEST
                    elif status == 400:

                        return {
                            "success": False,
                            "error": (
                                "Bad Gemini request "
                                "(400). Prompt may be "
                                "too large or malformed."
                            )
                        }

                    # FORBIDDEN
                    elif status == 403:

                        return {
                            "success": False,
                            "error": (
                                "Gemini access denied "
                                "(403 Forbidden)."
                            )
                        }

                    # OTHER ERRORS
                    else:

                        return {
                            "success": False,
                            "error": str(e)
                        }

                # ====================================
                # NETWORK ERRORS
                # ====================================

                except httpx.TimeoutException:

                    return {
                        "success": False,
                        "error": "Gemini request timeout."
                    }

                except httpx.ConnectError:

                    return {
                        "success": False,
                        "error": (
                            "Unable to connect "
                            "to Gemini API."
                        )
                    }

                # ====================================
                # UNKNOWN ERRORS
                # ====================================

                except Exception as e:

                    return {
                        "success": False,
                        "error": str(e)
                    }

        # ============================================
        # FINAL FAIL
        # ============================================

        return {
            "success": False,
            "error": (
                "Gemini analysis failed "
                "after multiple retries."
            )
        }

