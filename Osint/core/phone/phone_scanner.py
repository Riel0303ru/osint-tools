# core/phone/phone_scanner.py
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

import aiohttp
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from dotenv import load_dotenv

from core.base.scan_result import ScanResult
from utils.logger import Logger

ENV_PATH = Path(__file__).resolve().parents[2] / ".env.local"
load_dotenv(ENV_PATH)


class PhoneScanner:
    """Phone OSINT scanner – multi‑source dengan fallback & retry."""

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.numverify_api_key: Optional[str] = os.getenv("NUMVERIFY_API_KEY")
        self.abstract_phone_intel_key: Optional[str] = os.getenv("ABSTRACT_PHONE_INTELLIGENCE_KEY")
        self.hibp_api_key: Optional[str] = os.getenv("HIBP_API_KEY")

    # =========================================================
    # RETRY + BACKOFF HELPER
    # =========================================================
    async def _retry_with_backoff(self, coro_func, max_retries=3, base_delay=2.0):
        """
        Memanggil coro_func dengan exponential backoff jika gagal karena rate limit (429).
        """
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

    # =========================================================
    # MAIN SCAN
    # =========================================================
    async def scan_phone(self, phone: str) -> List[ScanResult]:
        self.logger.info(f"Scanning phone -> {phone}")

        try:
            parsed = phonenumbers.parse(phone, None)
        except Exception:
            return [ScanResult(
                platform="Phone Validation",
                username=phone,
                status="ERROR",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"error": "Failed to parse phone number"}
            )]

        is_valid = phonenumbers.is_valid_number(parsed)
        formatted_e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        formatted_international = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        country_code = parsed.country_code
        national_number = parsed.national_number
        region = phonenumbers.region_code_for_number(parsed)
        carrier_name = carrier.name_for_number(parsed, "en") or "Unknown"
        geo_desc = geocoder.description_for_number(parsed, "en") or "Unknown"
        timezones = timezone.time_zones_for_number(parsed)

        validation_result = ScanResult(
            platform="Phone Validation",
            username=formatted_e164,
            status="FOUND" if is_valid else "NOT_FOUND",
            status_code=200 if is_valid else 400,
            url="",
            confidence=1.0 if is_valid else 0.5,
            extra={
                "valid": is_valid,
                "country_code": country_code,
                "national_number": national_number,
                "region": region,
                "carrier": carrier_name,
                "location": geo_desc,
                "timezones": list(timezones),
                "international_format": formatted_international,
                "e164": formatted_e164
            }
        )
        results = [validation_result]

        async with aiohttp.ClientSession() as session:
            # Coba Numverify dulu (dengan retry)
            numverify_result = None
            if self.numverify_api_key:
                try:
                    numverify_result = await self._retry_with_backoff(
                        lambda: self._numverify_lookup(session, formatted_e164, country_code, national_number)
                    )
                except Exception as e:
                    self.logger.warning(f"Numverify failed after retries: {e}")
                    numverify_result = ScanResult(
                        platform="Numverify",
                        username=formatted_e164,
                        status="ERROR",
                        status_code=0,
                        url="",
                        confidence=0.0,
                        extra={"error": str(e)}
                    )
            else:
                numverify_result = ScanResult(
                    platform="Numverify",
                    username=formatted_e164,
                    status="NOT_AVAILABLE",
                    status_code=0,
                    url="",
                    confidence=0.0,
                    extra={"message": "API key not configured"}
                )
            results.append(numverify_result)

            # Abstract Phone Intel (dengan retry)
            abstract_result = None
            if self.abstract_phone_intel_key:
                try:
                    abstract_result = await self._retry_with_backoff(
                        lambda: self._abstract_phone_intelligence(session, formatted_e164)
                    )
                except Exception as e:
                    self.logger.warning(f"Abstract Phone Intel failed after retries: {e}")
                    abstract_result = ScanResult(
                        platform="Abstract Phone Intel",
                        username=formatted_e164,
                        status="ERROR",
                        status_code=0,
                        url="",
                        confidence=0.0,
                        extra={"error": str(e)}
                    )
            else:
                abstract_result = ScanResult(
                    platform="Abstract Phone Intel",
                    username=formatted_e164,
                    status="NOT_AVAILABLE",
                    status_code=0,
                    url="",
                    confidence=0.0,
                    extra={"message": "API key not configured"}
                )
            results.append(abstract_result)

            # WhatsApp, Telegram, BreachDirectory, HIBP tetap paralel
            tasks = {
                "WhatsApp": self._whatsapp_check(session, formatted_e164),
                "Telegram": self._telegram_check(session, formatted_e164),
                "BreachDirectory": self._breachdirectory_search(session, formatted_e164),
                "HaveIBeenPwned": self._hibp_phone_check(session, formatted_e164),
            }
            for name, coro in tasks.items():
                try:
                    res = await coro
                    results.append(res)
                except Exception as e:
                    self.logger.warning(f"{name} error: {e}")
                    results.append(ScanResult(
                        platform=name,
                        username=formatted_e164,
                        status="ERROR",
                        status_code=0,
                        url="",
                        confidence=0.0,
                        extra={"error": str(e)}
                    ))

        self.logger.success(f"Phone scan completed -> {formatted_e164}")
        return results

    # ========================================================
    # NUMVERIFY
    # ========================================================
    async def _numverify_lookup(self, session, e164: str, cc: int, ns: int) -> ScanResult:
        url = f"http://apilayer.net/api/validate?access_key={self.numverify_api_key}&number={ns}&country_code={cc}&format=1"
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("valid"):
                    return ScanResult(
                        platform="Numverify",
                        username=e164,
                        status="FOUND",
                        status_code=200,
                        url="",
                        confidence=0.9,
                        extra={
                            "valid": True,
                            "local_format": data.get("local_format"),
                            "line_type": data.get("line_type"),
                            "carrier": data.get("carrier"),
                            "location": data.get("location"),
                        }
                    )
                else:
                    return ScanResult(
                        platform="Numverify", username=e164, status="NOT_FOUND",
                        status_code=200, url="", confidence=0.5, extra={"valid": False}
                    )
            else:
                raise Exception(f"HTTP {resp.status}")

    # ========================================================
    # ABSTRACT PHONE INTELLIGENCE
    # ========================================================
    async def _abstract_phone_intelligence(self, session, e164: str) -> ScanResult:
        url = f"https://phoneintelligence.abstractapi.com/v1/?api_key={self.abstract_phone_intel_key}&phone={e164}"
        async with session.get(url, timeout=15) as resp:
            if resp.status == 200:
                data = await resp.json()
                valid = data.get("phone_validation", {}).get("is_valid", False)
                carrier_info = data.get("phone_carrier", {})
                location = data.get("phone_location", {})
                risk = data.get("phone_risk", {})
                messaging = data.get("phone_messaging", {})
                registration = data.get("phone_registration", {})
                breaches = data.get("phone_breaches", {})
                fmt = data.get("phone_format", {})

                extra = {
                    "valid": valid,
                    "carrier": carrier_info.get("name", ""),
                    "line_type": carrier_info.get("line_type", ""),
                    "country": location.get("country_name", ""),
                    "region": location.get("region", ""),
                    "city": location.get("city", ""),
                    "timezone": location.get("timezone", ""),
                    "risk_level": risk.get("risk_level", ""),
                    "is_disposable": risk.get("is_disposable", False),
                    "is_abuse_detected": risk.get("is_abuse_detected", False),
                    "sms_domain": messaging.get("sms_domain", ""),
                    "sms_email": messaging.get("sms_email", ""),
                    "registered_name": registration.get("name", ""),
                    "registration_type": registration.get("type", ""),
                    "total_breaches": breaches.get("total_breaches", 0),
                    "date_first_breached": breaches.get("date_first_breached", ""),
                    "date_last_breached": breaches.get("date_last_breached", ""),
                    "breached_domains": breaches.get("breached_domains", []),
                    "international_format": fmt.get("international", ""),
                    "national_format": fmt.get("national", ""),
                }
                return ScanResult(
                    platform="Abstract Phone Intel",
                    username=e164,
                    status="FOUND" if valid else "NOT_FOUND",
                    status_code=200,
                    url="",
                    confidence=0.95 if valid else 0.6,
                    extra=extra
                )
            elif resp.status == 422:
                raise Exception("Quota reached (422)")
            else:
                raise Exception(f"HTTP {resp.status}")

    # ========================================================
    # WHATSAPP (wa.me HEAD)
    # ========================================================
    async def _whatsapp_check(self, session, e164: str) -> ScanResult:
        try:
            number = e164.lstrip("+")
            url = f"https://wa.me/{number}"
            async with session.head(url, allow_redirects=True, timeout=15) as resp:
                final_url = str(resp.url).lower()
                if resp.status == 200:
                    if "web.whatsapp.com" in final_url or "api.whatsapp.com" in final_url:
                        return ScanResult(
                            platform="WhatsApp",
                            username=e164,
                            status="FOUND",
                            status_code=200,
                            url=f"https://wa.me/{number}",
                            confidence=0.95,
                            extra={"registered": True, "redirect_url": final_url}
                        )
                    else:
                        return ScanResult(
                            platform="WhatsApp",
                            username=e164,
                            status="FOUND",
                            status_code=200,
                            url=f"https://wa.me/{number}",
                            confidence=0.8,
                            extra={"registered": True, "final_url": final_url}
                        )
                elif resp.status == 404:
                    return ScanResult(
                        platform="WhatsApp", username=e164, status="NOT_FOUND",
                        status_code=404, url=f"https://wa.me/{number}",
                        confidence=0.9, extra={"registered": False}
                    )
                else:
                    return ScanResult(
                        platform="WhatsApp", username=e164, status="UNKNOWN",
                        status_code=resp.status, url=f"https://wa.me/{number}",
                        confidence=0.4, extra={"registered": None}
                    )
        except asyncio.TimeoutError:
            return ScanResult(platform="WhatsApp", username=e164, status="ERROR",
                            status_code=0, url="", confidence=0.0, extra={"error": "Timeout"})
        except Exception:
            raise

    # ========================================================
    # TELEGRAM (t.me HEAD)
    # ========================================================
    async def _telegram_check(self, session, e164: str) -> ScanResult:
        try:
            number = e164.lstrip("+")
            url = f"https://t.me/{number}"
            async with session.head(url, allow_redirects=True, timeout=15) as resp:
                final_url = str(resp.url).lower()
                if resp.status == 200:
                    if f"t.me/{number}" not in final_url and "t.me/" in final_url:
                        return ScanResult(
                            platform="Telegram", username=e164, status="NOT_FOUND",
                            status_code=200, url=f"https://t.me/{number}",
                            confidence=0.7, extra={"registered": False}
                        )
                    else:
                        return ScanResult(
                            platform="Telegram", username=e164, status="FOUND",
                            status_code=200, url=f"https://t.me/{number}",
                            confidence=0.75, extra={"registered": True, "final_url": final_url}
                        )
                elif resp.status == 404:
                    return ScanResult(
                        platform="Telegram", username=e164, status="NOT_FOUND",
                        status_code=404, url=f"https://t.me/{number}",
                        confidence=0.85, extra={"registered": False}
                    )
                else:
                    return ScanResult(
                        platform="Telegram", username=e164, status="UNKNOWN",
                        status_code=resp.status, url=f"https://t.me/{number}",
                        confidence=0.3, extra={"registered": None}
                    )
        except asyncio.TimeoutError:
            return ScanResult(platform="Telegram", username=e164, status="ERROR",
                            status_code=0, url="", confidence=0.0, extra={"error": "Timeout"})
        except Exception:
            raise

    # ========================================================
    # BREACHDIRECTORY
    # ========================================================
    async def _breachdirectory_search(self, session, e164: str) -> ScanResult:
        url = f"https://breachdirectory.org/api?func=auto&term={e164}"
        try:
            async with session.get(url, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    count = len(data.get("result", []))
                    return ScanResult(
                        platform="BreachDirectory",
                        username=e164,
                        status="FOUND" if count > 0 else "NOT_FOUND",
                        status_code=200,
                        url="https://breachdirectory.org",
                        confidence=0.9 if count > 0 else 0.7,
                        extra={"breaches_count": count,
                               "message": f"Found in {count} breaches" if count else "Not found"}
                    )
                else:
                    return ScanResult(platform="BreachDirectory", username=e164,
                                    status="ERROR", status_code=resp.status, url="", confidence=0.0)
        except Exception:
            raise

    # ========================================================
    # HAVE I BEEN PWNED (opsional)
    # ========================================================
    async def _hibp_phone_check(self, session, e164: str) -> ScanResult:
        if not self.hibp_api_key:
            return ScanResult(
                platform="HaveIBeenPwned",
                username=e164,
                status="NOT_AVAILABLE",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"message": "HIBP API key not configured"}
            )
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{e164}"
        headers = {"hibp-api-key": self.hibp_api_key, "user-agent": "OSINT-Fusion"}
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    breaches = await resp.json()
                    names = [b["Name"] for b in breaches]
                    return ScanResult(
                        platform="HaveIBeenPwned",
                        username=e164,
                        status="FOUND",
                        status_code=200,
                        url=f"https://haveibeenpwned.com/account/{e164}",
                        confidence=1.0,
                        extra={"breaches_count": len(breaches), "breaches": names[:10]}
                    )
                elif resp.status == 404:
                    return ScanResult(platform="HaveIBeenPwned", username=e164,
                                    status="NOT_FOUND", status_code=404, url="", confidence=0.9)
                else:
                    return ScanResult(platform="HaveIBeenPwned", username=e164,
                                    status="ERROR", status_code=resp.status, url="", confidence=0.0)
        except Exception:
            raise