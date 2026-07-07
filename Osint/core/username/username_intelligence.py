from __future__ import annotations

from typing import List, Dict


class UsernameIntelligence:

    def score(self, username: str) -> float:

        score = 0.0

        length = len(username)

        # optimal length
        if 6 <= length <= 15:
            score += 0.2

        # separators boost
        if "." in username or "_" in username:
            score += 0.2

        # full name pattern
        if any(x in username for x in ["gabriel", "hizkia"]):
            score += 0.2

        # initials pattern
        if len(username) <= 5:
            score += 0.1

        # numeric realism
        if any(c.isdigit() for c in username):
            if username[-1].isdigit():
                score += 0.1
            else:
                score += 0.05

        # linkedin style bonus
        if "+" in username:
            score += 0.25

        return round(min(score, 1.0), 2)

    def rank(self, usernames: List[str]) -> List[Dict]:

        ranked = []

        for u in usernames:
            ranked.append({
                "username": u,
                "score": self.score(u)
            })

        return sorted(
            ranked,
            key=lambda x: x["score"],
            reverse=True
        )