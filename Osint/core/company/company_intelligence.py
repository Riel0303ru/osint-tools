# core/company/company_intelligence.py
class CompanyIntelligence:
    """Scoring intelligence gabungan: Abstract API + Domain Intel."""

    def score(self, domain: str, results: list) -> float:
        score = 0.0

        # 1. Data dari Abstract Company Enrichment
        for r in results:
            if r.platform == "Company Enrichment" and r.status == "FOUND":
                extra = r.extra or {}
                if extra.get("company_name"):
                    score += 10
                if extra.get("description"):
                    score += 5
                if extra.get("industry"):
                    score += 10
                if extra.get("employee_count") or extra.get("employee_range"):
                    score += 5
                if extra.get("annual_revenue") or extra.get("revenue_range"):
                    score += 5
                if extra.get("phone_numbers"):
                    score += min(len(extra["phone_numbers"]) * 3, 10)
                if extra.get("email_addresses"):
                    score += min(len(extra["email_addresses"]) * 3, 10)
                if extra.get("technologies"):
                    score += min(len(extra["technologies"]) * 2, 10)
                break

        # 2. Data dari Domain Intelligence (WHOIS, DNS, SSL, dll.)
        whois = next((r for r in results if r.platform == "WHOIS" and r.status == "FOUND"), None)
        if whois:
            score += 10
            extra = whois.extra or {}
            if extra.get("registrar"):
                score += 5
            if extra.get("creation_date"):
                score += 5

        dns = next((r for r in results if r.platform == "DNS Records" and r.status == "FOUND"), None)
        if dns:
            score += 10
            records = dns.extra.get("records", {})
            if records.get("MX"):
                score += 5
            if records.get("TXT"):
                score += 5

        subdomain = next((r for r in results if r.platform == "Subdomain" and r.status == "FOUND"), None)
        if subdomain:
            count = subdomain.extra.get("count", 0)
            score += min(count * 2, 15)

        ssl = next((r for r in results if r.platform == "SSL Certificate" and r.status == "FOUND"), None)
        if ssl:
            score += 10

        tech = next((r for r in results if r.platform == "Tech Stack" and r.status == "FOUND"), None)
        if tech:
            score += 5

        sec_headers = next((r for r in results if r.platform == "Security Headers" and r.status == "FOUND"), None)
        if sec_headers:
            found = len(sec_headers.extra.get("headers_found", []))
            score += found * 3

        email_sec = next((r for r in results if r.platform == "Email Security" and r.status == "FOUND"), None)
        if email_sec:
            if email_sec.extra.get("spf"):
                score += 5
            if email_sec.extra.get("dmarc"):
                score += 5
            if email_sec.extra.get("dkim"):
                score += 5

        return min(score, 100.0)