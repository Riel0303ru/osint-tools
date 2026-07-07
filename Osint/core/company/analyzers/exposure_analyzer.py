# core/company/analyzers/exposure_analyzer.py
from __future__ import annotations

import asyncio
from typing import Dict, Any, List
import aiohttp
from utils.logger import Logger


class ExposureAnalyzer:
    """Memindai exposure & misconfiguration pada domain."""

    EXPOSURE_PATHS = [
        # Development & Debug
        "/.git/HEAD",
        "/.env",
        "/.env.local",
        "/.env.production",
        "/.env.development",
        "/debug/",
        "/phpinfo.php",
        "/info.php",
        "/test.php",
        # Admin panels
        "/admin/",
        "/administrator/",
        "/wp-admin/",
        "/login/",
        "/phpmyadmin/",
        "/swagger/",
        "/api-docs/",
        "/graphql",
        "/api/swagger.json",
        # Config & Backups
        "/backup/",
        "/wp-config.php",
        "/config.php",
        "/configuration.php",
        "/web.config",
        "/docker-compose.yml",
        "/Dockerfile",
        # Monitoring
        "/grafana/",
        "/kibana/",
        "/prometheus/",
        "/elasticsearch/",
        "/status/",
        "/health",
        "/actuator/health",
        # Storage
        "/storage/",
        "/uploads/",
        "/wp-content/uploads/",
        "/sitemap.xml",
        "/robots.txt",
        # Firebase / Cloud
        "/.well-known/",
        "/.htaccess",
        "/server-status",
    ]

    SEVERITY_MAP = {
        "/.git/HEAD": "CRITICAL",
        "/.env": "CRITICAL",
        "/.env.local": "CRITICAL",
        "/.env.production": "CRITICAL",
        "/phpinfo.php": "HIGH",
        "/wp-config.php": "CRITICAL",
        "/docker-compose.yml": "MEDIUM",
        "/Dockerfile": "MEDIUM",
        "/phpmyadmin/": "HIGH",
        "/swagger/": "MEDIUM",
        "/api-docs/": "MEDIUM",
        "/grafana/": "HIGH",
        "/kibana/": "HIGH",
        "/prometheus/": "MEDIUM",
        "/elasticsearch/": "HIGH",
        "/backup/": "HIGH",
        "/wp-admin/": "MEDIUM",
        "/admin/": "MEDIUM",
        "/actuator/health": "MEDIUM",
        "/storage/": "LOW",
        "/uploads/": "LOW",
    }

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def scan(self, domain: str) -> Dict[str, Any]:
        result = {
            "findings": [],
            "severity_summary": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
            "total_exposed": 0,
        }

        async with aiohttp.ClientSession() as session:
            tasks = []
            for path in self.EXPOSURE_PATHS:
                tasks.append(self._check_path(session, domain, path))

            findings = await asyncio.gather(*tasks, return_exceptions=True)

        for finding in findings:
            if isinstance(finding, dict) and finding.get("exposed"):
                result["findings"].append(finding)
                severity = finding.get("severity", "INFO")
                result["severity_summary"][severity] += 1

        result["total_exposed"] = len(result["findings"])

        # Urutkan berdasarkan severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        result["findings"].sort(key=lambda x: severity_order.get(x.get("severity", "INFO"), 99))

        return result

    async def _check_path(self, session: aiohttp.ClientSession, domain: str, path: str) -> Dict:
        url = f"https://{domain}{path}"
        try:
            async with session.get(url, timeout=10, allow_redirects=False) as resp:
                if resp.status in (200, 301, 302, 403):
                    return {
                        "url": url,
                        "path": path,
                        "exposed": True,
                        "status_code": resp.status,
                        "severity": self.SEVERITY_MAP.get(path, "INFO"),
                        "message": f"Potentially exposed: {path} (HTTP {resp.status})",
                    }
                else:
                    return {"path": path, "exposed": False}
        except Exception:
            return {"path": path, "exposed": False, "error": True}