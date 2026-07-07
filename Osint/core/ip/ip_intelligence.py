# core/ip/ip_intelligence.py
class IPIntelligence:
    """Scoring intelligence untuk IP Intelligence."""

    def score(self, ip: str, results: list) -> float:
        score = 0.0
        for r in results:
            if r.platform == "Abstract IP Intelligence" and r.status == "FOUND":
                extra = r.extra or {}
                if extra.get("is_vpn"):
                    score += 25
                if extra.get("is_proxy"):
                    score += 25
                if extra.get("is_tor"):
                    score += 30
                if extra.get("is_abuse"):
                    score += 20
                if extra.get("is_hosting"):
                    score += 10
                if extra.get("is_relay"):
                    score += 15
                if extra.get("city"):
                    score += 5
                if extra.get("region"):
                    score += 5
                if extra.get("country"):
                    score += 5
                break
        return min(score, 100.0)