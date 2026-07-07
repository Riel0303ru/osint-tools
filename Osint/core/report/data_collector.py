# core/report/data_collector.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from core.base.storage import Storage


class DataCollector:
    """Mengumpulkan semua data OSINT untuk satu target dari storage dan file export."""

    def __init__(self, storage: Storage, results_base: str = "Osint/results"):
        self.storage = storage
        self.results_base = Path(results_base)

    def collect_all(self, target: str) -> Dict:
        data = {
            "target": target,
            "scans": {},
            "export_files": {},
        }

        # 1. Ambil dari storage (SQLite)
        timestamps = self.storage.get_distinct_timestamps(target)
        if timestamps:
            latest = self.storage.get_scan_snapshot(target, timestamps[0])
            for r in latest:
                module = self._guess_module(r.platform)
                if module not in data["scans"]:
                    data["scans"][module] = []
                data["scans"][module].append(r.to_dict() if hasattr(r, 'to_dict') else r)

        # 2. Baca file export di results/<category>/<target>/
        safe_target = self._sanitize_target(target)

        for category in ["username", "email", "domain", "phone", "image"]:
            user_dir = self.results_base / category / safe_target
            if user_dir.exists():
                data["export_files"][category] = {}
                for file in user_dir.glob("*"):
                    if file.suffix in [".csv", ".xlsx", ".json"]:
                        data["export_files"][category][file.stem] = str(file)
                # Khusus image, baca report JSON jika ada
                if category == "image":
                    report_json = user_dir / "image_report.json"
                    if report_json.exists():
                        try:
                            with open(report_json, encoding="utf-8") as f:
                                data["export_files"]["image"]["report"] = json.load(f)
                        except Exception:
                            pass

        # 3. AI report
        ai_dir = self.results_base / "ai" / safe_target
        if ai_dir.exists():
            ai_json = ai_dir / "ai_analysis.json"
            if ai_json.exists():
                try:
                    with open(ai_json, encoding="utf-8") as f:
                        data["ai_analysis"] = json.load(f)
                except Exception:
                    pass

        return data

    def _sanitize_target(self, target: str) -> str:
        """
        Samakan logika sanitasi dengan AIWorkflow.
        Jika target berupa path, ambil nama file tanpa ekstensi.
        """
        if "\\" in target or "/" in target:
            target = Path(target).stem
        # Ganti karakter ilegal
        target = re.sub(r'[<>:"/\\|?*]', '_', target)
        return target[:100] if len(target) > 100 else target

    def _guess_module(self, platform: str) -> str:
        p = platform.lower()
        if any(w in p for w in ["instagram","github","twitter","tiktok","reddit","linkedin",
                                 "facebook","telegram","discord","snapchat","youtube","twitch"]):
            return "username"
        if any(w in p for w in ["haveibeenpwned","breach","gravatar","emailrep","hunter",
                                 "mx check","disposable"]):
            return "email"
        if any(w in p for w in ["whois","dns records","ssl","subdomain","tech stack",
                                 "ip geolocation","wayback","email security","security headers",
                                 "zone transfer","shodan","virustotal","http check"]):
            return "domain"
        if any(w in p for w in ["phone validation","numverify","whatsapp","telegram",
                                 "abstract","hibp"]):
            return "phone"
        if any(w in p for w in ["exif","ocr","face detection","perceptual hash",
                                 "steganography","google lens","yandex images"]):
            return "image"
        return "other"