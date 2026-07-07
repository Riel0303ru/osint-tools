# core/ai/ai_workflow.py
from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Union

from core.ai.ai_analyzer import AIAnalyzer
from core.ai.ai_prompt_builder import AIPromptBuilder
from core.ai.ai_report_generator import AIReportGenerator
from core.ai.ai_risk_engine import AIRiskEngine
from core.base.scan_result import ScanResult


class AIWorkflow:
    def __init__(self):
        self.analyzer = AIAnalyzer()
        self.prompt_builder = AIPromptBuilder()
        self.report_generator = AIReportGenerator()
        self.risk_engine = AIRiskEngine()
        self.base_dir = Path("Osint")          # ← folder output: Osint/results/ai/

    async def execute(
        self,
        target: str,
        module_name: str,
        results: List[Union[ScanResult, Dict]]
    ) -> dict:
        # 1. Build prompt
        prompt = self.prompt_builder.build(target, module_name, results)

        # 2. Panggil Gemini
        ai_response = await self.analyzer.analyze(prompt)
        analysis = ai_response.get("analysis", {})

        # 3. Hitung risk score lokal (fallback)
        local_risk = self.risk_engine.calculate(results)
        final_risk = analysis.get("risk_score", local_risk)
        if not isinstance(final_risk, (int, float)):
            final_risk = local_risk

        # 4. Sanitasi nama target untuk folder
        safe_target = self._sanitize_target(target)

        # 5. Direktori output
        output_dir = self.base_dir / "results" / "ai" / safe_target
        output_dir.mkdir(parents=True, exist_ok=True)

        # 6. Ekspor
        export_data = {
            "target": target,
            "module": module_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "risk_score": final_risk,
            "ai_analysis": analysis
        }
        self.report_generator.export_json(output_dir, export_data)
        self.report_generator.export_markdown(output_dir, analysis)

        return export_data

    @staticmethod
    def _sanitize_target(target: str) -> str:
        # Jika target adalah path (mengandung \ atau /), ambil nama file saja
        if "\\" in target or "/" in target:
            target = Path(target).stem
        # Ganti karakter ilegal Windows/Unix
        target = re.sub(r'[<>:"/\\|?*]', '_', target)
        return target[:100] if len(target) > 100 else target