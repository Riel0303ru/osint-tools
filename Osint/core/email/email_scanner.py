# core/email/email_scanner.py
from __future__ import annotations

import asyncio
import hashlib
import re
import os
from pathlib import Path
from typing import List, Optional

import aiohttp
import dns.asyncresolver
import dns.exception
from dotenv import load_dotenv

from core.base.scan_result import ScanResult
from utils.logger import Logger

ENV_PATH = Path(__file__).resolve().parents[2] / ".env.local"
load_dotenv(ENV_PATH)


class EmailScanner:
    """
    Email OSINT powerhouse – multi‑layered intelligence.
    Fokus utama: Abstract Email Reputation (key disediakan).
    Layanan lain hanya aktif jika API key tersedia.
    """

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.abstract_email_key: Optional[str] = os.getenv("ABSTRACT_EMAIL_KEY")
        self.hibp_api_key: Optional[str] = os.getenv("HIBP_API_KEY")
        self.rapidapi_key: Optional[str] = os.getenv("BREACHDIRECTORY_RAPIDAPI_KEY")
        self.emailrep_api_key: Optional[str] = os.getenv("EMAILREP_API_KEY")
        self.hunter_api_key: Optional[str] = os.getenv("HUNTER_API_KEY")

    def is_valid_format(self, email: str) -> bool:
        return bool(self.EMAIL_REGEX.match(email))

    async def scan_email(self, email: str) -> List[ScanResult]:
        if not self.is_valid_format(email):
            return [ScanResult(
                platform="Email Validation",
                username=email,
                status="ERROR",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"error": "Invalid email format"}
            )]

        self.logger.info(f"Scanning email -> {email}")

        async with aiohttp.ClientSession() as session:
            tasks = {
                "Abstract Email Reputation": self._abstract_email_reputation(session, email),
                "Gravatar": self._check_gravatar(session, email),
                "MX Check": self._check_mx(email),
                "Disposable": self._check_disposable(session, email),
            }
            # Layanan opsional – hanya dijalankan jika key ada
            if self.hibp_api_key:
                tasks["HaveIBeenPwned"] = self._check_hibp(session, email)
            if self.rapidapi_key:
                tasks["BreachDirectory"] = self._check_breachdirectory_rapidapi(session, email)
            if self.emailrep_api_key:
                tasks["EmailRep"] = self._check_emailrep(session, email)
            if self.hunter_api_key:
                tasks["Hunter"] = self._check_hunter(session, email)

            results = []
            for name, coro in tasks.items():
                try:
                    result = await coro
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"{name} error: {e}")
                    results.append(ScanResult(
                        platform=name,
                        username=email,
                        status="ERROR",
                        status_code=0,
                        url="",
                        confidence=0.0,
                        extra={"error": str(e)}
                    ))

        # Jika ada layanan opsional yang tidak dijalankan, tambahkan NOT_AVAILABLE
        for svc in ["HaveIBeenPwned", "BreachDirectory", "EmailRep", "Hunter"]:
            if not any(r.platform == svc for r in results):
                results.append(ScanResult(
                    platform=svc,
                    username=email,
                    status="NOT_AVAILABLE",
                    status_code=0,
                    url="",
                    confidence=0.0,
                    extra={"message": "API key not configured"}
                ))

        # Cross‑validation & accuracy boost
        results = self._apply_cross_validation(results)

        self.logger.success(f"Email scan completed -> {email}")
        return results

    # ========================================================
    # RETRY HELPER (dipakai untuk layanan yang rawan rate limit)
    # ========================================================
    async def _retry_with_backoff(self, coro_func, max_retries=3, base_delay=2.0):
        for attempt in range(1, max_retries + 1):
            try:
                return await coro_func()
            except Exception as e:
                if "429" in str(e) and attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1))
                    self.logger.warning(f"Rate limited. Retrying in {delay:.1f}s (attempt {attempt}/{max_retries})")
                    await asyncio.sleep(delay)
                else:
                    raise

    # ========================================================
    # CROSS‑VALIDATION & ACCURACY
    # ========================================================
    def _apply_cross_validation(self, results: List[ScanResult]) -> List[ScanResult]:
        abstract = next((r for r in results if r.platform == "Abstract Email Reputation"), None)
        mx = next((r for r in results if r.platform == "MX Check"), None)

        if abstract and abstract.status == "FOUND":
            # Naikkan confidence Gravatar jika Abstract memberikan skor tinggi
            score = abstract.extra.get("quality_score", 0)
            if isinstance(score, (int, float)) and score > 0.7:
                gravatar = next((r for r in results if r.platform == "Gravatar"), None)
                if gravatar and gravatar.status == "FOUND":
                    gravatar.confidence = min(1.0, gravatar.confidence + 0.1)
                    gravatar.extra["boosted_by_abstract"] = True

        if mx and mx.status == "NOT_FOUND":
            for r in results:
                if r.platform not in ("Abstract Email Reputation", "MX Check"):
                    r.confidence = round(r.confidence * 0.8, 2)
                    r.extra["mx_invalid"] = True
        return results

    # ========================================================
    # ABSTRACT EMAIL REPUTATION (KEY KAMU)
    # ========================================================
    async def _abstract_email_reputation(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        if not self.abstract_email_key:
            return ScanResult(
                platform="Abstract Email Reputation",
                username=email,
                status="NOT_AVAILABLE",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"message": "Abstract Email API key not configured"}
            )
        url = f"https://emailreputation.abstractapi.com/v1/?api_key={self.abstract_email_key}&email={email}"
        try:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    deliverability = data.get("email_deliverability", {})
                    quality = data.get("email_quality", {})
                    sender = data.get("email_sender", {})
                    domain_info = data.get("email_domain", {})
                    risk = data.get("email_risk", {})
                    breaches = data.get("email_breaches", {})

                    extra = {
                        "deliverability_status": deliverability.get("status"),
                        "deliverability_detail": deliverability.get("status_detail"),
                        "is_format_valid": deliverability.get("is_format_valid"),
                        "is_smtp_valid": deliverability.get("is_smtp_valid"),
                        "is_mx_valid": deliverability.get("is_mx_valid"),
                        "mx_records": deliverability.get("mx_records", []),
                        "quality_score": quality.get("score"),
                        "is_free_email": quality.get("is_free_email"),
                        "is_username_suspicious": quality.get("is_username_suspicious"),
                        "is_disposable": quality.get("is_disposable"),
                        "is_catchall": quality.get("is_catchall"),
                        "is_role": quality.get("is_role"),
                        "is_dmarc_enforced": quality.get("is_dmarc_enforced"),
                        "is_spf_strict": quality.get("is_spf_strict"),
                        "minimum_age_days": quality.get("minimum_age"),
                        "first_name": sender.get("first_name"),
                        "last_name": sender.get("last_name"),
                        "email_provider": sender.get("email_provider_name"),
                        "organization": sender.get("organization_name"),
                        "organization_type": sender.get("organization_type"),
                        "domain": domain_info.get("domain"),
                        "domain_age_days": domain_info.get("domain_age"),
                        "is_live_site": domain_info.get("is_live_site"),
                        "registrar": domain_info.get("registrar"),
                        "date_registered": domain_info.get("date_registered"),
                        "date_expires": domain_info.get("date_expires"),
                        "is_risky_tld": domain_info.get("is_risky_tld"),
                        "address_risk_status": risk.get("address_risk_status"),
                        "domain_risk_status": risk.get("domain_risk_status"),
                        "total_breaches": breaches.get("total_breaches"),
                        "date_first_breached": breaches.get("date_first_breached"),
                        "date_last_breached": breaches.get("date_last_breached"),
                        "breached_domains": breaches.get("breached_domains", [])
                    }
                    return ScanResult(
                        platform="Abstract Email Reputation",
                        username=email,
                        status="FOUND",
                        status_code=200,
                        url="",
                        confidence=quality.get("score", 0.8),
                        extra=extra
                    )
                else:
                    return ScanResult(
                        platform="Abstract Email Reputation",
                        username=email,
                        status="ERROR",
                        status_code=resp.status,
                        url="",
                        confidence=0.0,
                        extra={"error": f"HTTP {resp.status}"}
                    )
        except Exception:
            raise

    # ========================================================
    # HAVE I BEEN PWNED (hanya jika API key ada)
    # ========================================================
    async def _check_hibp(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"hibp-api-key": self.hibp_api_key, "user-agent": "OSINT-Fusion"}
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                breaches = await resp.json()
                names = [b["Name"] for b in breaches]
                return ScanResult(
                    platform="HaveIBeenPwned",
                    username=email,
                    status="FOUND",
                    status_code=200,
                    url=f"https://haveibeenpwned.com/account/{email}",
                    confidence=1.0,
                    extra={
                        "breaches_count": len(breaches),
                        "breaches": names[:10],
                        "message": f"Found in {len(breaches)} data breaches"
                    }
                )
            elif resp.status == 404:
                return ScanResult(
                    platform="HaveIBeenPwned",
                    username=email,
                    status="NOT_FOUND",
                    status_code=404,
                    url="",
                    confidence=0.9,
                    extra={"message": "No pwnage found!"}
                )
            else:
                raise Exception(f"HTTP {resp.status}")

    # ========================================================
    # BREACHDIRECTORY via RAPIDAPI
    # ========================================================
    async def _check_breachdirectory_rapidapi(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        url = "https://breachdirectory.p.rapidapi.com/search"
        headers = {
            "x-api-key": self.rapidapi_key,
            "x-api-host": "breachdirectory.p.rapidapi.com",
            "Accept": "application/json",
        }
        params = {"func": "auto", "term": email}
        async with session.get(url, headers=headers, params=params, timeout=20) as resp:
            if resp.status == 200:
                data = await resp.json()
                count = len(data.get("result", []))
                return ScanResult(
                    platform="BreachDirectory",
                    username=email,
                    status="FOUND" if count > 0 else "NOT_FOUND",
                    status_code=200,
                    url="https://breachdirectory.org",
                    confidence=0.95 if count > 0 else 0.7,
                    extra={
                        "breaches_count": count,
                        "message": f"Found in {count} breaches (via RapidAPI)" if count else "Not found"
                    }
                )
            else:
                raise Exception(f"HTTP {resp.status}")

    # ========================================================
    # GRAVATAR
    # ========================================================
    async def _check_gravatar(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        email_hash = hashlib.md5(email.strip().lower().encode()).hexdigest()
        url = f"https://en.gravatar.com/{email_hash}.json"
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    entry = data.get("entry", [{}])[0]
                    return ScanResult(
                        platform="Gravatar",
                        username=email,
                        status="FOUND",
                        status_code=200,
                        url=f"https://gravatar.com/{email_hash}",
                        confidence=1.0,
                        extra={
                            "display_name": entry.get("displayName"),
                            "avatar_url": entry.get("thumbnailUrl"),
                            "profile_url": entry.get("profileUrl"),
                            "location": entry.get("currentLocation"),
                            "accounts": [a.get("shortname") for a in entry.get("accounts", [])]
                        }
                    )
                else:
                    return ScanResult(
                        platform="Gravatar",
                        username=email,
                        status="NOT_FOUND",
                        status_code=resp.status,
                        url="",
                        confidence=0.9
                    )
        except Exception:
            raise

    # ========================================================
    # EMAILREP.IO
    # ========================================================
    async def _check_emailrep(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        url = f"https://emailrep.io/{email}?summary=true"
        headers = {"Key": self.emailrep_api_key}
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                rep = data.get("reputation", "unknown")
                return ScanResult(
                    platform="EmailRep",
                    username=email,
                    status="FOUND" if rep not in ["none", "unknown"] else "NOT_FOUND",
                    status_code=200,
                    url=f"https://emailrep.io/{email}",
                    confidence=0.8 if rep not in ["none"] else 0.3,
                    extra={
                        "reputation": rep,
                        "suspicious": data.get("suspicious", False),
                        "details": data.get("details", {})
                    }
                )
            else:
                raise Exception(f"HTTP {resp.status}")

    # ========================================================
    # HUNTER
    # ========================================================
    async def _check_hunter(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={self.hunter_api_key}"
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()["data"]
                result = data.get("result")
                status_map = {"valid": "FOUND", "accept_all": "FOUND", "invalid": "NOT_FOUND", "unknown": "UNKNOWN"}
                return ScanResult(
                    platform="Hunter",
                    username=email,
                    status=status_map.get(result, "UNKNOWN"),
                    status_code=200,
                    url=f"https://hunter.io/email-verifier/{email}",
                    confidence=data.get("score", 0)/100.0,
                    extra={
                        "first_name": data.get("first_name"),
                        "last_name": data.get("last_name"),
                        "domain": data.get("domain"),
                        "disposable": data.get("disposable", False),
                        "webmail": data.get("webmail", False)
                    }
                )
            else:
                raise Exception(f"HTTP {resp.status}")

    # ========================================================
    # MX RECORD CHECK (DNS)
    # ========================================================
    async def _check_mx(self, email: str) -> ScanResult:
        domain = email.split("@")[1]
        try:
            answers = await dns.asyncresolver.resolve(domain, 'MX')
            mx_servers = [str(r.exchange) for r in answers]
            return ScanResult(
                platform="MX Check",
                username=email,
                status="FOUND" if mx_servers else "NOT_FOUND",
                status_code=200,
                url="",
                confidence=1.0 if mx_servers else 0.1,
                extra={"mx_servers": mx_servers, "message": "Domain accepts mail"}
            )
        except (dns.exception.DNSException, Exception):
            return ScanResult(
                platform="MX Check",
                username=email,
                status="NOT_FOUND",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"mx_servers": [], "message": "No MX records – domain may not receive email"}
            )

    # ========================================================
    # DISPOSABLE EMAIL DETECTION (Kickbox)
    # ========================================================
    async def _check_disposable(self, session: aiohttp.ClientSession, email: str) -> ScanResult:
        domain = email.split("@")[1]
        url = f"https://open.kickbox.com/v1/disposable/{domain}"
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    disposable = data.get("disposable", False)
                    return ScanResult(
                        platform="Disposable Email",
                        username=email,
                        status="FOUND" if disposable else "NOT_FOUND",
                        status_code=200,
                        url="",
                        confidence=1.0 if disposable else 0.8,
                        extra={"disposable": disposable, "message": "Disposable email" if disposable else "Not disposable"}
                    )
                else:
                    raise Exception(f"HTTP {resp.status}")
        except Exception:
            raise