# core/ip/analyzers/service_analyzer.py
from __future__ import annotations

import asyncio
from typing import Dict, List, Optional
import aiohttp
from utils.logger import Logger

# Port umum dan layanannya
COMMON_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    465: "SMTPS",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "Oracle DB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    9200: "Elasticsearch",
    9300: "Elasticsearch Node",
    11211: "Memcached",
    27017: "MongoDB",
    5000: "Docker Registry",
    6443: "Kubernetes API",
    9090: "Prometheus",
    3000: "Grafana",
    8086: "InfluxDB",
    15672: "RabbitMQ Management",
}

class ServiceAnalyzer:
    """Analisis layanan yang berjalan pada IP berdasarkan port umum."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.max_ports_to_check = 30  # Batasi untuk kecepatan

    async def analyze(self, ip: str) -> Dict:
        """
        Periksa port umum dan identifikasi layanan.
        """
        results = []
        ports_to_check = list(COMMON_SERVICES.keys())[:self.max_ports_to_check]

        async with aiohttp.ClientSession() as session:
            tasks = [self._check_port(session, ip, port) for port in ports_to_check]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        findings = []
        for res in results:
            if isinstance(res, dict) and res.get("open"):
                findings.append(res)

        return {
            "total_checked": len(ports_to_check),
            "open_ports": len(findings),
            "findings": findings,
        }

    async def _check_port(self, session: aiohttp.ClientSession, ip: str, port: int) -> Dict:
        service_name = COMMON_SERVICES.get(port, f"Unknown-{port}")
        try:
            # Coba koneksi TCP sederhana
            connector = aiohttp.TCPConnector(force_close=True)
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as sock_session:
                try:
                    async with sock_session.get(f"http://{ip}:{port}", timeout=3) as resp:
                        return {
                            "port": port,
                            "service": service_name,
                            "open": True,
                            "status_code": resp.status,
                            "banner": "",
                        }
                except asyncio.TimeoutError:
                    # Timeout berarti port mungkin terbuka tapi tidak merespons HTTP
                    return {"port": port, "service": service_name, "open": True, "status_code": None, "banner": "Timeout (non-HTTP)"}
                except aiohttp.ClientConnectorError:
                    return {"port": port, "service": service_name, "open": False}
                except Exception:
                    return {"port": port, "service": service_name, "open": False}
        except Exception:
            return {"port": port, "service": service_name, "open": False}