# core/ai/ai_prompt_builder.py
from __future__ import annotations

import json
from typing import Dict, List, Union
from core.base.scan_result import ScanResult


class AIPromptBuilder:

    def build(
        self,
        target: str,
        module_name: str,
        results: List[Union[ScanResult, Dict]]
    ) -> str:
        """Susun prompt untuk Gemini berdasarkan hasil scan."""

        # Konversi ke dict jika perlu
        compact = []
        for r in results[:100]:  # batasi jumlah
            if isinstance(r, ScanResult):
                d = r.to_dict()
            else:
                d = r
            compact.append({
                "platform": d.get("platform", ""),
                "status": d.get("status", ""),
                "url": d.get("url", ""),
                "confidence": d.get("confidence", 0),
                "intelligence_score": d.get("intelligence_score", 0),
                "extra": d.get("extra", {})
            })

        payload = {
            "target": target,
            "module": module_name,
            "results": compact
        }

        prompt = f"""
You are an elite OSINT intelligence analyst.

Analyze the following OSINT investigation data.

Tasks:
1. Generate executive summary
2. Generate risk assessment
3. Detect correlations
4. Identify suspicious findings
5. Estimate confidence score
6. Generate investigation insights
7. Produce professional cybersecurity narrative

Return ONLY valid JSON with these keys:
- "summary": string
- "risk_level": "low"|"medium"|"high"|"critical"
- "risk_score": number 0-100
- "correlations": list of strings
- "suspicious_findings": list of strings
- "confidence_estimate": number 0-100
- "insights": list of strings
- "narrative": string

DATA:
{json.dumps(payload, indent=2)}
"""
        return prompt