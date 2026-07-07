# core/domain/domain_intelligence.py
class DomainIntelligence:
    def score(self, domain: str, results: list) -> float:
        score = 0.0
        # WHOIS
        if any(r.platform == "WHOIS" and r.status == "FOUND" for r in results):
            score += 15
        # DNS Records
        for r in results:
            if r.platform == "DNS Records" and r.status == "FOUND":
                records = r.extra.get("records", {})
                if len(records) > 3:
                    score += 15
                    break
        # Subdomain
        for r in results:
            if r.platform == "Subdomain":
                count = r.extra.get("count", 0)
                score += min(count * 2, 15)
                break
        # SSL
        if any(r.platform == "SSL Certificate" and r.status == "FOUND" for r in results):
            score += 10
        # Tech Stack
        if any(r.platform == "Tech Stack" and r.status == "FOUND" for r in results):
            score += 5
        # IP Geolocation
        if any(r.platform == "IP Geolocation" and r.status == "FOUND" for r in results):
            score += 10
        # Wayback
        if any(r.platform == "Wayback Machine" and r.status == "FOUND" for r in results):
            score += 10
        # Email Security
        for r in results:
            if r.platform == "Email Security":
                spf = r.extra.get("spf", False)
                dmarc = r.extra.get("dmarc", False)
                dkim = r.extra.get("dkim", False)
                score += sum([spf, dmarc, dkim]) * 5
                break
        # Security Headers
        for r in results:
            if r.platform == "Security Headers":
                found = len(r.extra.get("headers_found", []))
                score += found * 3
                break
        # Zone Transfer (kelemahan)
        if any(r.platform == "DNS Zone Transfer" and r.status == "FOUND" for r in results):
            score += 10  # berbahaya, tapi data berharga
        # Shodan
        if any(r.platform == "Shodan" and r.status == "FOUND" for r in results):
            score += 10
        # VirusTotal
        if any(r.platform == "VirusTotal" and r.status == "FOUND" for r in results):
            score += 10

        return min(score, 100.0)