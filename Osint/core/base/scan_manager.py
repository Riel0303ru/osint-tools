# core/base/scan_manager.py
from __future__ import annotations

import asyncio
import os
import re
from typing import Dict, List, Optional, Tuple

import aiohttp

from utils.logger import Logger
from core.base.scan_result import ScanResult
from core.base.storage import Storage

from core.username.async_username_scanner import AsyncUsernameScanner
from core.username.search_allocator import SearchAllocator
from core.username.username_intelligence import UsernameIntelligence
from core.email.email_scanner import EmailScanner
from core.domain.domain_scanner import DomainScanner
from core.domain.domain_intelligence import DomainIntelligence
from core.phone.phone_scanner import PhoneScanner
from core.phone.phone_intelligence import PhoneIntelligence
from core.image.image_scanner import ImageScanner
from core.ip.ip_scanner import IPScanner
from core.ip.ip_intelligence import IPIntelligence
from core.company.company_engine import CompanyEngine
from core.correlation.correlation_workflow import CorrelationWorkflow
from core.document.document_scanner import DocumentScanner
from core.document.document_intelligence import DocumentIntelligence
from core.darkweb.darkweb_scanner import DarkwebScanner
from core.darkweb.darkweb_intelligence import DarkwebIntelligence

# Korelasi identitas & persona untuk username
from core.username.correlators.identity_correlator import IdentityCorrelator
from core.username.correlators.persona_classifier import PersonaClassifier
from core.username.correlators.confidence_engine import ConfidenceEngine

# Video Intelligence (NEW)
from core.video.video_scanner import VideoScanner
from core.video.video_intelligence import VideoIntelligence


class ScanManager:
    """
    Manajer pemindaian pusat – dengan peningkatan akurasi & validasi silang.
    Semua modul kini dilengkapi mekanisme cross‑validation dan enrichment metadata.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.base_dir = base_dir
        self.logger = Logger(base_dir=base_dir)

        # Storage untuk history & delta detection
        self.storage = Storage(
            db_path=os.path.join(base_dir, "data", "osint_history.db")
        )

        # Modul scanner
        self.username_scanner = AsyncUsernameScanner(base_dir=base_dir)
        self.allocator = SearchAllocator()
        self.intelligence = UsernameIntelligence()
        self.email_scanner = EmailScanner(base_dir=base_dir)
        self.domain_scanner = DomainScanner(base_dir=base_dir)
        self.domain_intelligence = DomainIntelligence()
        self.phone_scanner = PhoneScanner(base_dir=base_dir)
        self.phone_intelligence = PhoneIntelligence()
        self.image_scanner = ImageScanner(base_dir=base_dir)
        self.ip_scanner = IPScanner(base_dir=base_dir)
        self.ip_intelligence = IPIntelligence()
        
        # Company Engine (menggantikan CompanyScanner & CompanyIntelligence)
        self.company_engine = CompanyEngine(storage=self.storage, base_dir=base_dir)

        # Korelasi identitas & persona untuk username
        self.identity_correlator = IdentityCorrelator()
        self.persona_classifier = PersonaClassifier()
        self.confidence_engine = ConfidenceEngine()
        
        self.correlation_workflow = CorrelationWorkflow(storage=self.storage, base_dir=base_dir)
        
        # Document Intelligence
        self.document_scanner = DocumentScanner(base_dir=base_dir)
        
        # Dark Web Intelligence
        self.darkweb_scanner = DarkwebScanner(base_dir=base_dir)

        # Video Intelligence (NEW)
        self.video_scanner = VideoScanner(base_dir=base_dir)

    # =========================================================
    # KONVERSI BANTUAN (dengan validasi confidence)
    # =========================================================
    def _dict_to_scanresult(self, d: Dict) -> ScanResult:
        """Konversi dictionary hasil scanner ke ScanResult dengan adjustment confidence."""
        confidence = d.get("confidence", 1.0)
        if d.get("status") == "ERROR":
            confidence = min(confidence, 0.3)
        return ScanResult(
            platform=d.get("platform", "unknown"),
            username=d.get("username", ""),
            status=d.get("status", "UNKNOWN"),
            status_code=d.get("status_code", 0),
            url=d.get("url", ""),
            confidence=confidence,
            extra=d.get("extra", {})
        )

    # =========================================================
    # CROSS-VALIDATION (mengurangi false positive)
    # =========================================================
    async def _validate_found(self, result: ScanResult) -> ScanResult:
        if not result.url:
            result.extra["validation_skipped"] = True
            return result

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    result.url,
                    timeout=10,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    allow_redirects=True
                ) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if result.username.lower() not in text.lower():
                            result.confidence *= 0.5
                            result.extra["possible_false_positive"] = True
                            self.logger.warning(
                                f"Username '{result.username}' not found in page content of "
                                f"{result.platform}, lowering confidence to {result.confidence:.2f}"
                            )
                        else:
                            result.confidence = min(1.0, result.confidence * 1.1)
                            result.extra["verified_in_content"] = True
                    elif resp.status == 404:
                        result.status = "NOT_FOUND"
                        result.status_code = 404
                        result.confidence = 0.95
                        result.extra["corrected_to_not_found"] = True
                        self.logger.info(
                            f"Corrected {result.platform} to NOT_FOUND (got 404)"
                        )
        except Exception:
            result.extra["validation_skipped"] = True

        return result

    # =========================================================
    # USERNAME SCAN CORE
    # =========================================================
    async def run_username_scan(
        self,
        username: str,
        budget: int = 100,
        priority_platforms: Optional[List[str]] = None
    ) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Starting OSINT username scan -> {username}")

        priority_platforms = priority_platforms or []

        raw_results = await self.username_scanner.scan_username_async(
            username=username,
            budget=budget,
            priority_platforms=priority_platforms
        )

        results = []
        for r in raw_results:
            if isinstance(r, dict):
                sr = self._dict_to_scanresult(r)
            else:
                sr = r
            if sr.status == "FOUND" and sr.url:
                validated = await self._validate_found(sr)
                results.append(validated)
            else:
                results.append(sr)

        self.logger.success(f"Scan completed -> {username}")
        return results

    # =========================================================
    # EMAIL SCAN CORE
    # =========================================================
    async def run_email_scan(self, email: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Starting OSINT email scan -> {email}")
        results = await self.email_scanner.scan_email(email)
        self.logger.success(f"Email scan completed -> {email}")
        return results

    # =========================================================
    # PHONE SCAN CORE
    # =========================================================
    async def run_phone_scan(self, phone: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Starting OSINT phone scan -> {phone}")
        results = await self.phone_scanner.scan_phone(phone)
        self.logger.success(f"Phone scan completed -> {phone}")
        return results

    # =========================================================
    # WORKFLOW USERNAME (DILENGKAPI KORELASI & PERSONA)
    # =========================================================
    async def execute_username_workflow(
        self,
        username: str,
        budget: int = 100,
        priority_platforms: Optional[List[str]] = None
    ) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT username workflow -> {username}")

        results = await self.run_username_scan(
            username=username,
            budget=budget,
            priority_platforms=priority_platforms
        )

        enriched = self._enrich_with_intelligence(results)
        enriched = await self._fetch_extra_info(enriched)

        validated = []
        for r in enriched:
            if r.status == "FOUND" and not r.extra.get("verified_in_content") and not r.extra.get("possible_false_positive"):
                validated.append(await self._validate_found(r))
            else:
                validated.append(r)
        enriched = validated

        # ---------- KORELASI IDENTITAS & PERSONA ----------
        # Confidence Engine
        enriched = self.confidence_engine.calculate(enriched)

        # Korelasi identitas antar platform
        linked_accounts = self.identity_correlator.correlate(enriched)

        # Klasifikasi persona digital
        persona = self.persona_classifier.classify(enriched)

        # Tambahkan sebagai ScanResult agar ikut tersimpan & ditampilkan
        enriched.append(ScanResult(
            platform="Identity Correlation",
            username=username,
            status="FOUND" if linked_accounts else "NOT_FOUND",
            status_code=200 if linked_accounts else 404,
            url="",
            confidence=0.9 if linked_accounts else 0.3,
            extra={"linked_accounts": linked_accounts}
        ))
        enriched.append(ScanResult(
            platform="Persona Classification",
            username=username,
            status="FOUND",
            status_code=200,
            url="",
            confidence=persona.get("confidence", 0.0),
            extra={"persona": persona}
        ))
        # ---------- AKHIR KORELASI & PERSONA ----------

        timestamp = self.storage.save_scan(username, enriched)
        self.logger.info(f"Scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(enriched)
        self.logger.success(
            f"Workflow done -> {username} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return enriched

    # =========================================================
    # WORKFLOW EMAIL
    # =========================================================
    async def execute_email_workflow(self, email: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT email workflow -> {email}")

        results = await self.run_email_scan(email)
        enriched = self._enrich_email_intelligence(results)

        timestamp = self.storage.save_scan(email, enriched)
        self.logger.info(f"Email scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(enriched)
        self.logger.success(
            f"Email workflow done -> {email} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return enriched

    # =========================================================
    # WORKFLOW DOMAIN
    # =========================================================
    async def execute_domain_workflow(self, domain: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT domain workflow -> {domain}")

        results = await self.domain_scanner.scan_domain(domain)
        await self._cross_validate_domain(results)

        for r in results:
            r.intelligence_score = self.domain_intelligence.score(domain, results)

        timestamp = self.storage.save_scan(domain, results)
        self.logger.info(f"Domain scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(results)
        self.logger.success(
            f"Domain workflow done -> {domain} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return results

    async def _cross_validate_domain(self, results: List[ScanResult]) -> None:
        whois_result = next((r for r in results if r.platform == "WHOIS"), None)
        dns_result = next((r for r in results if r.platform == "DNS Records"), None)

        if whois_result and dns_result:
            whois_ns = [ns.lower() for ns in whois_result.extra.get("name_servers", [])]
            dns_ns = [ns.lower() for ns in dns_result.extra.get("records", {}).get("NS", [])]
            if whois_ns and dns_ns:
                if any(ns in dns_ns for ns in whois_ns):
                    whois_result.confidence = min(1.0, whois_result.confidence + 0.1)
                    whois_result.extra["cross_validated_with_dns"] = True
                    self.logger.info(f"WHOIS-DNS cross-validation passed for domain")

    # =========================================================
    # WORKFLOW PHONE
    # =========================================================
    async def execute_phone_workflow(self, phone: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT phone workflow -> {phone}")

        results = await self.run_phone_scan(phone)
        for r in results:
            r.intelligence_score = self.phone_intelligence.score(phone, results)

        numverify = next((r for r in results if r.platform == "Numverify" and r.status == "FOUND"), None)
        if numverify:
            for r in results:
                if r.platform in ["WhatsApp", "Telegram"] and r.status == "FOUND":
                    r.confidence = min(1.0, r.confidence + 0.1)
                    r.extra["boosted_by_numverify"] = True

        timestamp = self.storage.save_scan(phone, results)
        self.logger.info(f"Phone scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(results)
        self.logger.success(
            f"Phone workflow done -> {phone} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return results

    # =========================================================
    # WORKFLOW IMAGE
    # =========================================================
    async def execute_image_workflow(self, image_path: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT image workflow -> {image_path}")

        scan_results, raw_data = await self.image_scanner.scan_image(image_path)

        timestamp = self.storage.save_scan(image_path, scan_results)
        self.logger.info(f"Image scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(scan_results)
        self.logger.success(
            f"Image workflow done -> {image_path} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return scan_results

    # =========================================================
    # WORKFLOW IP
    # =========================================================
    async def execute_ip_workflow(self, ip_address: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT IP workflow -> {ip_address}")

        results = await self.ip_scanner.scan_ip(ip_address)
        for r in results:
            r.intelligence_score = self.ip_intelligence.score(ip_address, results)

        timestamp = self.storage.save_scan(ip_address, results)
        self.logger.info(f"IP scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(results)
        self.logger.success(
            f"IP workflow done -> {ip_address} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return results

    # =========================================================
    # WORKFLOW COMPANY (MENGGUNAKAN COMPANY ENGINE)
    # =========================================================
    async def execute_company_workflow(self, domain: str) -> Tuple[List[ScanResult], Dict]:
        """
        Jalankan Company Intelligence Engine lengkap.
        Mengembalikan (scan_results, full_report).
        """
        return await self.company_engine.execute_full(domain)

    # =========================================================
    # WORKFLOW DOCUMENT
    # =========================================================
    async def execute_document_workflow(self, file_path: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing OSINT document workflow -> {file_path}")

        results = await self.document_scanner.scan(file_path)
        for r in results:
            r.intelligence_score = DocumentIntelligence.score(file_path, results)

        timestamp = self.storage.save_scan(file_path, results)
        self.logger.info(f"Document scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(results)
        self.logger.success(
            f"Document workflow done -> {file_path} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return results

    # =========================================================
    # WORKFLOW DARKWEB
    # =========================================================
    async def execute_darkweb_workflow(self, target: str) -> List[ScanResult]:
        self.logger.divider()
        self.logger.info(f"Executing Dark Web Intelligence workflow -> {target}")

        results = await self.darkweb_scanner.scan(target)
        for r in results:
            r.intelligence_score = DarkwebIntelligence.score(target, results)

        timestamp = self.storage.save_scan(target, results)
        self.logger.info(f"Dark web scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(results)
        self.logger.success(
            f"Dark web workflow done -> {target} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return results

    # =========================================================
    # WORKFLOW VIDEO (NEW)
    # =========================================================
    async def execute_video_workflow(self, file_path: str) -> List[ScanResult]:
        """
        Jalankan pipeline Video Intelligence penuh.
        Skor intelijen dihitung per hasil, disimpan ke history.
        """
        self.logger.divider()
        self.logger.info(f"Executing Video Intelligence workflow -> {file_path}")

        results = await self.video_scanner.scan(file_path)

        # Hitung skor intelijen untuk setiap tahap
        total_score = VideoIntelligence.score(file_path, results)
        for r in results:
            r.intelligence_score = total_score

        timestamp = self.storage.save_scan(file_path, results)
        self.logger.info(f"Video scan saved to history with timestamp {timestamp}")

        stats = self.generate_statistics(results)
        self.logger.success(
            f"Video workflow done -> {file_path} | "
            f"FOUND={stats['found']} | "
            f"TOTAL={stats['total']}"
        )
        self.logger.divider()
        return results

    # =========================================================
    # INTELLIGENCE ENRICHMENT
    # =========================================================
    def _enrich_with_intelligence(self, results: List[ScanResult]) -> List[ScanResult]:
        for r in results:
            try:
                base_score = self.intelligence.score(r.username)
                r.intelligence_score = base_score * r.confidence
            except Exception:
                r.intelligence_score = 0.0

        results.sort(key=lambda x: x.intelligence_score, reverse=True)
        return results

    def _enrich_email_intelligence(self, results: List[ScanResult]) -> List[ScanResult]:
        for r in results:
            if r.platform == "HaveIBeenPwned" and r.status == "FOUND":
                breach_count = r.extra.get("breaches_count", 0)
                r.intelligence_score = min(breach_count * 8.0, 100.0)
            elif r.platform == "BreachDirectory" and r.status == "FOUND":
                breach_count = r.extra.get("breaches_count", 0)
                r.intelligence_score = min(breach_count * 6.0, 70.0)
            elif r.status == "FOUND":
                r.intelligence_score = 40.0
            elif r.status == "ERROR":
                r.intelligence_score = 0.0
            else:
                r.intelligence_score = 5.0

            r.intelligence_score *= r.confidence

        results.sort(key=lambda x: x.intelligence_score, reverse=True)
        return results

    # =========================================================
    # METADATA ENRICHMENT
    # =========================================================
    async def _fetch_extra_info(self, results: List[ScanResult]) -> List[ScanResult]:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for r in results:
                if r.platform.lower() == "github" and r.status == "FOUND":
                    tasks.append(self._github_extra(session, r))
                elif r.platform.lower() in ("x (twitter)", "twitter") and r.status == "FOUND":
                    tasks.append(self._twitter_extra(session, r))
                elif r.platform.lower() == "instagram" and r.status == "FOUND":
                    tasks.append(self._instagram_extra(session, r))
            await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def _github_extra(self, session, result: ScanResult):
        try:
            url = f"https://api.github.com/users/{result.username}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result.extra["bio"] = data.get("bio") or ""
                    result.extra["avatar_url"] = data.get("avatar_url") or ""
                    result.extra["name"] = data.get("name") or ""
                    result.extra["blog"] = data.get("blog") or ""
                    result.extra["company"] = data.get("company") or ""
                    result.extra["public_repos"] = data.get("public_repos", 0)
                    result.extra["followers"] = data.get("followers", 0)
        except Exception:
            pass

    async def _twitter_extra(self, session, result: ScanResult):
        result.extra["profile_url"] = f"https://twitter.com/{result.username}"

    async def _instagram_extra(self, session, result: ScanResult):
        try:
            async with session.get(
                f"https://instagram.com/{result.username}", timeout=10
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    match = re.search(
                        r'<meta property="og:description" content="([^"]+)"', text
                    )
                    if match:
                        result.extra["bio"] = match.group(1)[:200]
        except Exception:
            pass

    # =========================================================
    # FILTER & STATISTIK
    # =========================================================
    def filter_results_by_status(
        self, results: List[ScanResult], status: str
    ) -> List[ScanResult]:
        status = status.upper()
        return [r for r in results if r.status.upper() == status]

    def get_found_results(self, results: List[ScanResult]) -> List[ScanResult]:
        return self.filter_results_by_status(results, "FOUND")

    def get_error_results(self, results: List[ScanResult]) -> List[ScanResult]:
        return self.filter_results_by_status(results, "ERROR")

    def generate_statistics(self, results: List[ScanResult]) -> Dict[str, int]:
        return {
            "total": len(results),
            "found": len(self.get_found_results(results)),
            "errors": len(self.get_error_results(results)),
        }

    def print_statistics(self, results: List[ScanResult]) -> None:
        stats = self.generate_statistics(results)
        self.logger.info(
            f"STATISTICS | "
            f"TOTAL={stats['total']} | "
            f"FOUND={stats['found']} | "
            f"ERRORS={stats['errors']}"
        )

    # =========================================================
    # MODULE REGISTRY
    # =========================================================
    def get_available_modules(self) -> Dict[str, bool]:
        return {
            "username": True,
            "email": True,
            "domain": True,
            "phone": True,
            "image": True,
            "ip": True,
            "company": True,
            "document": True,
            "darkweb": True,
            "video": True,    # <-- MODUL VIDEO SUDAH TERSEDIA
            "ai": False,
        }

    def module_exists(self, module_name: str) -> bool:
        return self.get_available_modules().get(module_name.lower(), False)