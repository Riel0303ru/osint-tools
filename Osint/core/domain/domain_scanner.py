# core/domain/domain_scanner.py
from __future__ import annotations

import asyncio
import re
import ssl
from typing import List, Dict, Any, Optional

import aiohttp
import dns.asyncresolver
import dns.exception
import dns.query
import dns.zone
import whois

from core.base.scan_result import ScanResult
from utils.logger import Logger


class DomainScanner:
    """
    Async domain OSINT scanner – 13+ platform intelijen dengan peningkatan akurasi.
    """

    def __init__(self, base_dir: str = "Osint"):
        self.logger = Logger(base_dir=base_dir)
        self.shodan_api_key: Optional[str] = None
        self.virustotal_api_key: Optional[str] = None

    async def scan_domain(self, domain: str) -> List[ScanResult]:
        clean = self._clean_domain(domain)
        if not clean:
            return [ScanResult(
                platform="Domain Validation",
                username=domain,
                status="ERROR",
                status_code=0,
                url=domain,
                confidence=0.0,
                extra={"error": "Invalid domain format"}
            )]

        self.logger.info(f"Scanning domain -> {clean}")

        async with aiohttp.ClientSession() as session:
            tasks = {
                "WHOIS": self._whois_lookup(clean),
                "DNS Records": self._dns_all_records(clean),
                "Subdomain": self._subdomain_enumeration(session, clean),
                "SSL Certificate": self._ssl_certificate_check(clean),
                "Tech Stack": self._tech_stack_detect(session, clean),
                "IP Geolocation": self._ip_geolocation(clean),
                "Wayback Machine": self._wayback_machine(session, clean),
                "Email Security": self._email_security(clean),
                "Security Headers": self._security_headers_check(session, clean),
                "DNS Zone Transfer": self._dns_zone_transfer(clean),
                "Shodan": self._shodan_lookup(session, clean),
                "VirusTotal": self._virustotal_lookup(session, clean),
                "HTTP Check": self._http_check(session, clean),   # tambahan
            }

            results = []
            for name, coro in tasks.items():
                try:
                    result = await coro
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"{name} error: {e}")
                    results.append(ScanResult(
                        platform=name,
                        username=clean,
                        status="ERROR",
                        status_code=0,
                        url=clean,
                        confidence=0.0,
                        extra={"error": str(e)}
                    ))

        # === CROSS‑VALIDATION & ACCURACY BOOST ===
        results = self._apply_cross_validation(results)

        self.logger.success(f"Domain scan completed -> {clean}")
        return results

    # =========================================================
    # CROSS‑VALIDATION
    # =========================================================
    def _apply_cross_validation(self, results: List[ScanResult]) -> List[ScanResult]:
        """
        Sesuaikan confidence berdasarkan konsistensi antar sumber:
        - Jika DNS A record ada dan HTTP Check berhasil, keduanya saling menguatkan.
        - Jika WHOIS dan DNS memiliki NS yang cocok, confidence WHOIS naik.
        - Jika subdomain banyak dan HTTP Check gagal untuk domain utama,
          turunkan sedikit confidence subdomain (mungkin parked domain).
        """
        # Ambil referensi
        dns_result = next((r for r in results if r.platform == "DNS Records"), None)
        http_result = next((r for r in results if r.platform == "HTTP Check"), None)
        whois_result = next((r for r in results if r.platform == "WHOIS"), None)
        subdomain_result = next((r for r in results if r.platform == "Subdomain"), None)

        # 1. DNS + HTTP cross‑validation
        if dns_result and http_result:
            dns_a = dns_result.extra.get("records", {}).get("A", [])
            if dns_a and http_result.status == "FOUND":
                # DNS A record ada dan HTTP bisa diakses → sangat yakin domain hidup
                dns_result.confidence = min(1.0, dns_result.confidence + 0.1)
                http_result.confidence = min(1.0, http_result.confidence + 0.1)
                http_result.extra["dns_cross_validated"] = True
                self.logger.info("Cross‑validation: DNS A + HTTP success")
            elif not dns_a and http_result.status == "FOUND":
                # Mungkin DNS record A tidak ditemukan, tapi HTTP bisa → bisa jadi ada A record tidak terambil
                http_result.confidence = min(1.0, http_result.confidence + 0.05)
            elif dns_a and http_result.status != "FOUND":
                # DNS A ada tapi HTTP tidak bisa → mungkin server down atau firewall
                http_result.confidence = max(0.1, http_result.confidence - 0.2)
                dns_result.extra["http_failed"] = True

        # 2. WHOIS + DNS NS cross‑validation
        if whois_result and dns_result:
            whois_ns = [ns.lower() for ns in whois_result.extra.get("name_servers", [])]
            dns_ns = [ns.lower() for ns in dns_result.extra.get("records", {}).get("NS", [])]
            if whois_ns and dns_ns:
                if any(ns in dns_ns for ns in whois_ns):
                    whois_result.confidence = min(1.0, whois_result.confidence + 0.1)
                    whois_result.extra["cross_validated_with_dns"] = True
                    self.logger.info("Cross‑validation: WHOIS NS matches DNS NS")
                else:
                    whois_result.confidence = max(0.3, whois_result.confidence - 0.2)
                    whois_result.extra["dns_mismatch"] = True
                    self.logger.warning("WHOIS NS does not match DNS NS")

        # 3. Subdomain vs HTTP
        if subdomain_result and subdomain_result.status == "FOUND" and http_result:
            if http_result.status != "FOUND":
                # Domain utama tidak bisa HTTP, tapi banyak subdomain di CT log? Mungkin parked.
                subdomain_result.confidence = max(0.4, subdomain_result.confidence - 0.2)
                subdomain_result.extra["low_confidence_reason"] = "Main domain not reachable via HTTP"

        return results

    # =========================================================
    # HELPERS
    # =========================================================
    def _clean_domain(self, domain: str) -> str:
        domain = domain.strip().lower()
        for prefix in ["https://", "http://"]:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]
        if domain.startswith("www."):
            domain = domain[4:]
        if "." not in domain or len(domain) < 3:
            return ""
        return domain

    # =========================================================
    # HTTP CHECK (BARU)
    # =========================================================
    async def _http_check(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        """
        Coba akses HTTP dan HTTPS untuk memastikan domain benar-benar aktif.
        Mengembalikan FOUND jika salah satu berhasil.
        """
        for protocol, port, url in [("http", 80, f"http://{domain}"), ("https", 443, f"https://{domain}")]:
            try:
                async with session.get(url, timeout=8, allow_redirects=True) as resp:
                    if resp.status == 200:
                        return ScanResult(
                            platform="HTTP Check",
                            username=domain,
                            status="FOUND",
                            status_code=200,
                            url=url,
                            confidence=1.0,
                            extra={
                                "accessible": True,
                                "protocol": protocol,
                                "status_code": resp.status
                            }
                        )
            except Exception:
                continue
        return ScanResult(
            platform="HTTP Check",
            username=domain,
            status="NOT_FOUND",
            status_code=0,
            url=f"http://{domain}",
            confidence=0.1,
            extra={"accessible": False, "message": "Neither HTTP nor HTTPS responded"}
        )

    # =========================================================
    # WHOIS
    # =========================================================
    async def _whois_lookup(self, domain: str) -> ScanResult:
        try:
            w = await asyncio.to_thread(whois.whois, domain)
            if w.domain_name:
                return ScanResult(
                    platform="WHOIS",
                    username=domain,
                    status="FOUND",
                    status_code=200,
                    url=f"https://www.whois.com/whois/{domain}",
                    confidence=1.0,
                    extra={
                        "registrar": w.registrar,
                        "creation_date": str(w.creation_date) if w.creation_date else None,
                        "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                        "name_servers": w.name_servers[:5] if w.name_servers else [],
                        "country": w.country,
                        "org": w.org,
                    }
                )
            else:
                return ScanResult(platform="WHOIS", username=domain, status="NOT_FOUND", status_code=404, url="", confidence=0.5, extra={"message": "No WHOIS data found"})
        except Exception:
            return ScanResult(platform="WHOIS", username=domain, status="ERROR", status_code=0, url="", confidence=0.0, extra={"error": "WHOIS lookup failed"})

    # =========================================================
    # DNS RECORDS (ALL)
    # =========================================================
    async def _dns_all_records(self, domain: str) -> ScanResult:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME", "SRV"]
        records: Dict[str, List[str]] = {}
        found_any = False
        for rtype in record_types:
            try:
                answers = await dns.asyncresolver.resolve(domain, rtype)
                records[rtype] = [str(r) for r in answers]
                found_any = True
            except (dns.exception.DNSException, Exception):
                records[rtype] = []
        if found_any:
            return ScanResult(
                platform="DNS Records", username=domain, status="FOUND", status_code=200,
                url=f"https://dns.google.com/resolve?name={domain}&type=ANY",
                confidence=1.0, extra={"records": records}
            )
        else:
            return ScanResult(
                platform="DNS Records", username=domain, status="NOT_FOUND", status_code=404,
                url="", confidence=0.2, extra={"records": records, "message": "No DNS records found"}
            )

    # =========================================================
    # SUBDOMAIN ENUMERATION (crt.sh + Anubis + AlienVault)
    # =========================================================
    async def _subdomain_enumeration(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        subdomains = set()

        # crt.sh
        try:
            async with session.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data:
                        name_value = entry.get("name_value", "")
                        for name in name_value.split("\n"):
                            name = name.strip().lower()
                            if name.endswith(f".{domain}") or name == domain:
                                subdomains.add(name)
        except Exception:
            pass

        # Anubis (jldc.me)
        try:
            async with session.get(f"https://jldc.me/anubis/subdomains/{domain}", timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for sub in data:
                        sub = sub.strip().lower()
                        if sub.endswith(f".{domain}") or sub == domain:
                            subdomains.add(sub)
        except Exception:
            pass

        # AlienVault OTX (Passive DNS)
        try:
            async with session.get(
                f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns",
                timeout=10
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data.get("passive_dns", []):
                        hostname = entry.get("hostname", "").strip().lower()
                        if hostname and (hostname.endswith(f".{domain}") or hostname == domain):
                            subdomains.add(hostname)
        except Exception:
            pass

        subdomain_list = sorted(list(subdomains))
        return ScanResult(
            platform="Subdomain",
            username=domain,
            status="FOUND" if subdomain_list else "NOT_FOUND",
            status_code=200,
            url=f"https://crt.sh/?q=%25.{domain}",
            confidence=0.9 if subdomain_list else 0.5,
            extra={"subdomains": subdomain_list[:100], "count": len(subdomain_list)}
        )

    # =========================================================
    # SSL CERTIFICATE
    # =========================================================
    async def _ssl_certificate_check(self, domain: str) -> ScanResult:
        try:
            ctx = ssl.create_default_context()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(domain, 443, ssl=ctx), timeout=10
            )
            cert = writer.get_extra_info('ssl_object').getpeercert()
            writer.close()
            await writer.wait_closed()

            return ScanResult(
                platform="SSL Certificate", username=domain, status="FOUND", status_code=200,
                url=f"https://{domain}", confidence=1.0,
                extra={
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "subject": dict(x[0] for x in cert.get("subject", [])),
                    "not_before": cert.get("notBefore"),
                    "not_after": cert.get("notAfter"),
                    "san": cert.get("subjectAltName", [])
                }
            )
        except Exception:
            return ScanResult(
                platform="SSL Certificate", username=domain, status="NOT_FOUND", status_code=0,
                url=f"https://{domain}", confidence=0.3,
                extra={"message": "No SSL certificate found or connection failed"}
            )

    # =========================================================
    # TECH STACK
    # =========================================================
    async def _tech_stack_detect(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        url = f"https://{domain}"
        try:
            async with session.get(url, timeout=10) as resp:
                headers = dict(resp.headers)
                body = await resp.text()
                tech = []
                if "x-powered-by" in headers:
                    tech.append(headers["x-powered-by"])
                if "server" in headers:
                    tech.append(headers["server"])
                # Deteksi dari body
                if "wp-content" in body: tech.append("WordPress")
                if "shopify" in body: tech.append("Shopify")
                if "cloudflare" in body: tech.append("Cloudflare")
                tech = list(set(tech))

                return ScanResult(
                    platform="Tech Stack", username=domain, status="FOUND" if tech else "NOT_FOUND",
                    status_code=resp.status, url=url, confidence=0.7 if tech else 0.4,
                    extra={
                        "technologies": tech,
                        "status_code": resp.status,
                        "headers": {
                            "Server": headers.get("server", ""),
                            "X-Powered-By": headers.get("x-powered-by", ""),
                            "Content-Type": headers.get("content-type", "")
                        }
                    }
                )
        except Exception:
            return ScanResult(platform="Tech Stack", username=domain, status="ERROR", status_code=0, url=url, confidence=0.0, extra={"error": "Tech detection failed"})

    # =========================================================
    # IP GEOLOCATION (ip-api.com)
    # =========================================================
    async def _ip_geolocation(self, domain: str) -> ScanResult:
        try:
            answers = await dns.asyncresolver.resolve(domain, 'A')
            ip = str(answers[0])
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ip-api.com/json/{ip}", timeout=10) as resp:
                    if resp.status == 200:
                        geo = await resp.json()
                        if geo.get("status") == "success":
                            return ScanResult(
                                platform="IP Geolocation", username=domain,
                                status="FOUND", status_code=200,
                                url=f"http://ip-api.com/#{ip}",
                                confidence=0.9,
                                extra={
                                    "ip": ip,
                                    "country": geo.get("country"),
                                    "region": geo.get("regionName"),
                                    "city": geo.get("city"),
                                    "isp": geo.get("isp"),
                                    "lat": geo.get("lat"),
                                    "lon": geo.get("lon"),
                                }
                            )
            return ScanResult(platform="IP Geolocation", username=domain, status="NOT_FOUND", status_code=0, url="", confidence=0.0)
        except Exception:
            return ScanResult(platform="IP Geolocation", username=domain, status="ERROR", status_code=0, url="", confidence=0.0, extra={"error": "Geolocation failed"})

    # =========================================================
    # WAYBACK MACHINE
    # =========================================================
    async def _wayback_machine(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        try:
            url = f"http://archive.org/wayback/available?url={domain}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    archived = data.get("archived_snapshots", {}).get("closest", {})
                    if archived and archived.get("available"):
                        timestamp = archived.get("timestamp", "")
                        return ScanResult(
                            platform="Wayback Machine", username=domain,
                            status="FOUND", status_code=200,
                            url=f"https://web.archive.org/web/*/{domain}",
                            confidence=1.0,
                            extra={
                                "first_snapshot": timestamp,
                                "url": archived.get("url", "")
                            }
                        )
            return ScanResult(
                platform="Wayback Machine", username=domain,
                status="NOT_FOUND", status_code=200, url=f"https://web.archive.org/web/*/{domain}",
                confidence=0.6, extra={"message": "No snapshots found"}
            )
        except Exception:
            return ScanResult(platform="Wayback Machine", username=domain, status="ERROR", status_code=0, url="", confidence=0.0)

    # =========================================================
    # EMAIL SECURITY (SPF, DMARC, DKIM)
    # =========================================================
    async def _email_security(self, domain: str) -> ScanResult:
        spf = False
        dmarc = False
        dkim = False
        details = {}

        # SPF
        try:
            answers = await dns.asyncresolver.resolve(domain, 'TXT')
            for r in answers:
                txt = r.to_text().strip('"')
                if txt.startswith("v=spf1"):
                    spf = True
                    details["spf_record"] = txt
                    break
        except Exception:
            pass

        # DMARC
        try:
            answers = await dns.asyncresolver.resolve(f"_dmarc.{domain}", 'TXT')
            for r in answers:
                txt = r.to_text().strip('"')
                if txt.startswith("v=DMARC1"):
                    dmarc = True
                    details["dmarc_record"] = txt
                    break
        except Exception:
            pass

        # DKIM - simplified: check default selector "default._domainkey"
        try:
            answers = await dns.asyncresolver.resolve(f"default._domainkey.{domain}", 'TXT')
            for r in answers:
                txt = r.to_text().strip('"')
                if "v=DKIM1" in txt:
                    dkim = True
                    details["dkim_record"] = txt
                    break
        except Exception:
            pass

        status = "FOUND" if (spf or dmarc or dkim) else "NOT_FOUND"
        score = sum([spf, dmarc, dkim]) * 30
        return ScanResult(
            platform="Email Security", username=domain,
            status=status, status_code=200 if status == "FOUND" else 404,
            url="", confidence=min(score, 100) / 100.0,
            extra={
                "spf": spf,
                "dmarc": dmarc,
                "dkim": dkim,
                "details": details
            }
        )

    # =========================================================
    # SECURITY HEADERS
    # =========================================================
    async def _security_headers_check(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        url = f"https://{domain}"
        try:
            async with session.get(url, timeout=10) as resp:
                headers = resp.headers
                checks = {
                    "Strict-Transport-Security": "hsts" in headers,
                    "Content-Security-Policy": "content-security-policy" in headers,
                    "X-Frame-Options": "x-frame-options" in headers,
                    "X-Content-Type-Options": "x-content-type-options" in headers,
                    "Referrer-Policy": "referrer-policy" in headers,
                }
                present = [h for h, v in checks.items() if v]
                return ScanResult(
                    platform="Security Headers",
                    username=domain,
                    status="FOUND" if present else "NOT_FOUND",
                    status_code=resp.status,
                    url=url,
                    confidence=len(present) / 5.0,
                    extra={
                        "headers_found": present,
                        "missing": [h for h, v in checks.items() if not v],
                    }
                )
        except Exception:
            return ScanResult(
                platform="Security Headers", username=domain,
                status="ERROR", status_code=0, url=url, confidence=0.0,
                extra={"error": "Failed to fetch headers"}
            )

    # =========================================================
    # DNS ZONE TRANSFER (AXFR)
    # =========================================================
    async def _dns_zone_transfer(self, domain: str) -> ScanResult:
        try:
            ns_answers = await dns.asyncresolver.resolve(domain, 'NS')
            nameservers = [str(ns) for ns in ns_answers]
            for ns in nameservers:
                try:
                    ns_ip = await dns.asyncresolver.resolve(ns, 'A')
                    ip = str(ns_ip[0])
                    zone = dns.zone.from_xfr(await dns.query.xfr(ip, domain, timeout=5))
                    if zone:
                        return ScanResult(
                            platform="DNS Zone Transfer",
                            username=domain,
                            status="FOUND",
                            status_code=200,
                            url=ns,
                            confidence=1.0,
                            extra={"message": "Zone transfer successful", "nameserver": ns}
                        )
                except Exception:
                    continue
            return ScanResult(
                platform="DNS Zone Transfer",
                username=domain,
                status="NOT_FOUND",
                status_code=0,
                url="",
                confidence=0.8,
                extra={"message": "Zone transfer failed or not allowed"}
            )
        except Exception:
            return ScanResult(
                platform="DNS Zone Transfer",
                username=domain,
                status="ERROR",
                status_code=0,
                url="",
                confidence=0.0,
                extra={"error": "NS lookup failed"}
            )

    # =========================================================
    # SHODAN (optional)
    # =========================================================
    async def _shodan_lookup(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        if not self.shodan_api_key:
            return ScanResult(
                platform="Shodan", username=domain, status="NOT_AVAILABLE",
                status_code=0, url="", confidence=0.0,
                extra={"message": "API key not configured"}
            )
        try:
            answers = await dns.asyncresolver.resolve(domain, 'A')
            ip = str(answers[0])
            url = f"https://api.shodan.io/shodan/host/{ip}?key={self.shodan_api_key}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ports = data.get("ports", [])
                    services = [f"{port}: {data.get('data', [{}])[0].get('product', 'unknown')}" for port in ports]
                    return ScanResult(
                        platform="Shodan", username=domain,
                        status="FOUND" if ports else "NOT_FOUND",
                        status_code=200, url=f"https://www.shodan.io/host/{ip}",
                        confidence=0.9 if ports else 0.5,
                        extra={
                            "ip": ip,
                            "ports": ports,
                            "services": services,
                            "os": data.get("os"),
                        }
                    )
                else:
                    return ScanResult(platform="Shodan", username=domain, status="ERROR", status_code=resp.status, url="", confidence=0.0)
        except Exception:
            return ScanResult(platform="Shodan", username=domain, status="ERROR", status_code=0, url="", confidence=0.0, extra={"error": "Shodan lookup failed"})

    # =========================================================
    # VirusTotal (optional)
    # =========================================================
    async def _virustotal_lookup(self, session: aiohttp.ClientSession, domain: str) -> ScanResult:
        if not self.virustotal_api_key:
            return ScanResult(
                platform="VirusTotal", username=domain, status="NOT_AVAILABLE",
                status_code=0, url="", confidence=0.0,
                extra={"message": "API key not configured"}
            )
        try:
            url = f"https://www.virustotal.com/api/v3/domains/{domain}"
            headers = {"x-apikey": self.virustotal_api_key}
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    attributes = data.get("data", {}).get("attributes", {})
                    return ScanResult(
                        platform="VirusTotal", username=domain,
                        status="FOUND", status_code=200,
                        url=f"https://www.virustotal.com/gui/domain/{domain}",
                        confidence=0.9,
                        extra={
                            "reputation": attributes.get("reputation"),
                            "last_analysis_stats": attributes.get("last_analysis_stats"),
                        }
                    )
                elif resp.status == 404:
                    return ScanResult(platform="VirusTotal", username=domain, status="NOT_FOUND", status_code=404, url="", confidence=0.5)
                else:
                    return ScanResult(platform="VirusTotal", username=domain, status="ERROR", status_code=resp.status, url="", confidence=0.0)
        except Exception:
            return ScanResult(platform="VirusTotal", username=domain, status="ERROR", status_code=0, url="", confidence=0.0, extra={"error": "VirusTotal lookup failed"})