from typing import List, Dict


class UsernameFilter:

    def filter_by_budget(
        self,
        ranked: List[Dict],
        budget: int
    ) -> List[str]:

        # only take top budget %
        limit = max(1, int(len(ranked) * (budget / 100)))

        return [
            r["username"]
            for r in ranked[:limit]
        ]