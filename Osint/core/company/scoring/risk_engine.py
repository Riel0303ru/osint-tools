# core/company/scoring/risk_engine.py
from __future__ import annotations

from typing import Dict, List, Any
from datetime import datetime


class RiskEngine:
    """Weighted multi-category risk scoring untuk perusahaan."""

    WEIGHTS = {
        "infrastructure_risk": 0.25,
        "dns_risk": 0.20,
        "email_security_risk": 0.15,
        "exposure_risk": 0.20,
        "reputation_risk": 0.10,
        "technology_risk": 0.10,
    }

    # --- Public API ---
    @classmethod
    def calculate(
        cls,
        domain: str,
        company_data: Dict,
        whois_data: Dict,
        dns_data: Dict,
        ssl_data: Dict,
        tech_data: Dict,
        subdomain_data: Dict,
        security_data: Dict,
    ) -> Dict:
        scores = {
            "infrastructure_risk": cls._infrastructure_risk(whois_data, dns_data, ssl_data),
            "dns_risk": cls._dns_risk(dns_data),
            "email_security_risk": cls._email_security_risk(dns_data),
            "exposure_risk": cls._exposure_risk(subdomain_data, tech_data, security_data),
            "reputation_risk": cls._reputation_risk(whois_data, company_data),
            "technology_risk": cls._technology_risk(tech_data),
        }
        total = sum(scores[cat] * cls.WEIGHTS[cat] for cat in scores)

        threat_level = (
            "CRITICAL" if total >= 70
            else "HIGH" if total >= 50
            else "MEDIUM" if total >= 30
            else "LOW" if total >= 15
            else "MINIMAL"
        )
        return {
            "domain": domain,
            "category_scores": scores,
            "total_risk_score": round(total, 1),
            "threat_level": threat_level,
            "confidence_score": cls._confidence_score(whois_data, dns_data, ssl_data, tech_data),
        }

    # --- Infrastructure Risk ---
    @classmethod
    def _infrastructure_risk(cls, whois: Dict, dns: Dict, ssl: Dict) -> float:
        score = 0.0
        if whois:
            if whois.get("registrar") and "privacy" in str(whois.get("registrar")).lower():
                score += 10
            creation = whois.get("creation_date")
            if creation:
                try:
                    age_days = (datetime.now() - datetime.strptime(str(creation)[:10], "%Y-%m-%d")).days
                    if age_days < 90:
                        score += 25
                    elif age_days < 365:
                        score += 15
                except Exception:
                    pass
        if dns and dns.get("cdn_detected"):
            score += 5
        if ssl and ssl.get("issuer"):
            issuer_str = str(ssl["issuer"]).lower()
            if "lets encrypt" in issuer_str:
                score += 5
            if "self signed" in issuer_str:
                score += 20
        return min(score, 100.0)

    # --- DNS Risk ---
    @classmethod
    def _dns_risk(cls, dns: Dict) -> float:
        score = 0.0
        if dns:
            if dns.get("dangling_cname"):
                score += len(dns["dangling_cname"]) * 15
            if dns.get("suspicious_txt"):
                score += len(dns["suspicious_txt"]) * 10
        return min(score, 100.0)

    # --- Email Security Risk ---
    @classmethod
    def _email_security_risk(cls, dns: Dict) -> float:
        score = 0.0
        if dns and dns.get("email_security"):
            sec = dns["email_security"]
            if not sec.get("spf"):
                score += 30
            elif sec.get("spf_weak"):
                score += 20
            if not sec.get("dmarc"):
                score += 30
            if not sec.get("dkim"):
                score += 20
        return min(score, 100.0)

    # --- Exposure Risk (MANDIRI – tidak import CompanyCorrelator) ---
    @classmethod
    def _exposure_risk(cls, subdomain: Dict, tech: Dict, security: Dict) -> float:
        score = 0.0
        if subdomain:
            count = subdomain.get("count", 0)
            if count > 100:
                score += 20
            elif count > 20:
                score += 10
            # Klasifikasi langsung di sini
            classification = cls._classify_subdomains(subdomain)
            score += classification.get("admin", 0) * 5
            score += classification.get("dev", 0) * 3
        if security:
            missing = security.get("missing", [])
            score += len(missing) * 5
        return min(score, 100.0)

    # --- Reputation Risk ---
    @classmethod
    def _reputation_risk(cls, whois: Dict, company: Dict) -> float:
        score = 0.0
        if whois:
            if whois.get("country") in ("CN", "RU", "KP", "IR"):
                score += 15
        return min(score, 100.0)

    # --- Technology Risk ---
    @classmethod
    def _technology_risk(cls, tech: Dict) -> float:
        score = 0.0
        if tech:
            tech_list = [t.lower() for t in tech.get("technologies", [])]
            outdated = [
                "jquery 1.", "jquery 2.", "php 5.", "php 7.0",
                "wordpress 4.", "wordpress 5.0",
            ]
            for t in tech_list:
                for o in outdated:
                    if o in t:
                        score += 10
                        break
        return min(score, 100.0)

    # --- Confidence Score ---
    @classmethod
    def _confidence_score(cls, whois: Dict, dns: Dict, ssl: Dict, tech: Dict) -> float:
        sources = sum([
            1 if whois and whois.get("registrar") else 0,
            1 if dns and dns.get("records") else 0,
            1 if ssl and ssl.get("issuer") else 0,
            1 if tech and tech.get("technologies") else 0,
        ])
        return min(sources / 4.0 * 100, 100.0)

    # --- Klasifikasi subdomain (dipindahkan dari CompanyCorrelator) ---
    @staticmethod
    def _classify_subdomains(subdomain_data: Dict) -> Dict[str, int]:
        subs = subdomain_data.get("subdomains", [])
        classification = {
            "api": 0, "admin": 0, "staging": 0, "dev": 0,
            "cdn": 0, "mail": 0, "vpn": 0, "monitoring": 0, "other": 0,
        }
        keywords = {
            "api": ["api", "graphql", "rest"],
            "admin": ["admin", "panel", "dashboard", "manage"],
            "staging": ["staging", "stage", "test", "testing"],
            "dev": ["dev", "development", "develop"],
            "cdn": ["cdn", "static", "assets", "media"],
            "mail": ["mail", "email", "smtp", "imap"],
            "vpn": ["vpn", "remote", "gateway"],
            "monitoring": ["monitor", "grafana", "kibana", "prometheus", "status"],
        }
        for sub in subs:
            classified = False
            for category, kws in keywords.items():
                if any(kw in sub.lower() for kw in kws):
                    classification[category] += 1
                    classified = True
                    break
            if not classified:
                classification["other"] += 1
        return classification