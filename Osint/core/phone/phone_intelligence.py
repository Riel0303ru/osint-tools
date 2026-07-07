class PhoneIntelligence:
    def score(self, phone: str, results: list) -> float:
        score = 0.0
        # Validasi dasar
        if any(r.platform == "Phone Validation" and r.status == "FOUND" for r in results):
            score += 20
        # Carrier / operator
        if any(r.platform == "Numverify" and r.status == "FOUND" for r in results):
            score += 25
        # WhatsApp
        if any(r.platform == "WhatsApp" and r.status == "FOUND" for r in results):
            score += 20
        # Telegram
        if any(r.platform == "Telegram" and r.status == "FOUND" for r in results):
            score += 15
        # Breach
        for r in results:
            if r.platform == "BreachDirectory" and r.status == "FOUND":
                count = r.extra.get("breaches_count", 0)
                score += min(count * 5, 20)
                break
        return min(score, 100.0)