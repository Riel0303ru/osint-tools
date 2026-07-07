# core/company/providers/ssl_provider.py
from __future__ import annotations

import ssl
import asyncio
from typing import Dict, Any
from utils.logger import Logger


class SSLProvider:
    """SSL/TLS intelligence menggunakan koneksi langsung."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)

    async def analyze(self, domain: str) -> Dict[str, Any]:
        """Ambil sertifikat SSL dan analisis propertinya."""
        result = {
            "status": "NOT_FOUND",
            "issuer": {},
            "subject": {},
            "not_before": None,
            "not_after": None,
            "san": [],
            "serial_number": None,
            "version": None,
            "is_expired": False,
            "days_until_expiry": 0,
            "is_self_signed": False,
            "is_wildcard": False,
            "tls_version": None,
        }

        try:
            ctx = ssl.create_default_context()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(domain, 443, ssl=ctx), timeout=10
            )
            cert = writer.get_extra_info('ssl_object').getpeercert()
            tls_version = writer.get_extra_info('ssl_object').version()

            writer.close()
            await writer.wait_closed()

            if cert:
                result["status"] = "FOUND"
                result["issuer"] = dict(x[0] for x in cert.get("issuer", []))
                result["subject"] = dict(x[0] for x in cert.get("subject", []))
                result["not_before"] = cert.get("notBefore")
                result["not_after"] = cert.get("notAfter")
                result["san"] = cert.get("subjectAltName", [])
                result["serial_number"] = cert.get("serialNumber")
                result["version"] = cert.get("version")
                result["tls_version"] = tls_version

                # Deteksi self-signed
                issuer_org = result["issuer"].get("organizationName", "")
                subject_org = result["subject"].get("organizationName", "")
                if issuer_org and subject_org and issuer_org == subject_org:
                    result["is_self_signed"] = True

                # Deteksi wildcard
                common_name = result["subject"].get("commonName", "")
                if common_name.startswith("*."):
                    result["is_wildcard"] = True

                # Hitung hari sampai kadaluarsa
                if result["not_after"]:
                    from datetime import datetime
                    try:
                        expiry = datetime.strptime(result["not_after"], "%b %d %H:%M:%S %Y %Z")
                        delta = expiry - datetime.now()
                        result["days_until_expiry"] = delta.days
                        result["is_expired"] = delta.days < 0
                    except Exception:
                        pass

        except Exception as e:
            result["error"] = str(e)

        return result