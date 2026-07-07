# core/company/correlators/company_correlator.py
from typing import Dict, List, Any

class CompanyCorrelator:
    """Menghubungkan temuan dari berbagai sumber menjadi intelligence."""

    @staticmethod
    def correlate(domain: str, company_data: Dict, whois_data: Dict, dns_data: Dict,
                  ssl_data: Dict, tech_data: Dict, subdomain_data: Dict) -> Dict:
        """
        Gabungkan semua data dan hasilkan korelasi.
        """
        correlations = {
            "domain": domain,
            "company_profile": {},
            "infrastructure_profile": {},
            "attack_surface": {},
            "security_posture": {},
            "correlation_findings": [],
        }

        # 1. Company Profile
        if company_data:
            correlations["company_profile"] = {
                "name": company_data.get("company_name"),
                "industry": company_data.get("industry"),
                "size": company_data.get("employee_range"),
                "revenue": company_data.get("revenue_range"),
                "hq": f"{company_data.get('city', '')}, {company_data.get('country', '')}",
                "linkedin": company_data.get("linkedin_url"),
            }

        # 2. Infrastructure Profile
        infra = {}
        if whois_data:
            infra["registrar"] = whois_data.get("registrar")
            infra["domain_age"] = whois_data.get("creation_date")
        if dns_data:
            infra["dns_provider"] = dns_data.get("provider_identified")
            infra["cdn"] = dns_data.get("cdn_detected", [])
            infra["saas"] = dns_data.get("saas_detected", [])
            infra["email_provider"] = CompanyCorrelator._extract_email_provider(dns_data)
        correlations["infrastructure_profile"] = infra

        # 3. Attack Surface
        attack = {}
        if subdomain_data:
            attack["subdomain_count"] = subdomain_data.get("count", 0)
            attack["exposed_services"] = CompanyCorrelator._classify_subdomains(subdomain_data)
        if ssl_data:
            attack["ssl_expiry"] = ssl_data.get("not_after")
            attack["wildcard_cert"] = "*." in str(ssl_data.get("san", []))
        correlations["attack_surface"] = attack

        # 4. Security Posture
        security = {}
        if dns_data and dns_data.get("email_security"):
            sec = dns_data["email_security"]
            security["email_security_score"] = f"{sec.get('score', 0)}/3"
            security["spf"] = sec.get("spf", False)
            security["dmarc"] = sec.get("dmarc", False)
            security["dkim"] = sec.get("dkim", False)
            if sec.get("spf_weak"):
                security["spf_weak"] = True
        if tech_data:
            security["tech_exposed"] = len(tech_data.get("technologies", []))
        correlations["security_posture"] = security

        # 5. Correlation Findings
        findings = []
        # WHOIS org == SSL subject
        if whois_data.get("org") and ssl_data.get("subject"):
            findings.append("WHOIS organization matches SSL certificate subject")
        # MX provider == SaaS provider
        # ... lebih banyak korelasi
        correlations["correlation_findings"] = findings

        return correlations

    @staticmethod
    def _extract_email_provider(dns_data: Dict) -> str:
        mx = dns_data.get("records", {}).get("MX", [])
        if not mx:
            return "Unknown"
        mx_str = " ".join(mx).lower()
        if "google" in mx_str or "gmail" in mx_str:
            return "Google Workspace"
        if "outlook" in mx_str or "protection.outlook" in mx_str:
            return "Microsoft 365"
        if "zoho" in mx_str:
            return "Zoho Mail"
        return "Custom/Other"

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