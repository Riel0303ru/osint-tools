from typing import List, Dict


class SearchAllocator:

    def __init__(self):

        self.priority_weight = 2.5
        self.normal_weight = 1.0

    def allocate(
        self,
        total_budget: int,
        platforms: List[str],
        priority: List[str]
    ) -> Dict[str, int]:

        weights = {}

        for p in platforms:

            if p in priority:
                weights[p] = self.priority_weight
            else:
                weights[p] = self.normal_weight

        total_weight = sum(weights.values())

        allocation = {}

        for p in platforms:

            share = (weights[p] / total_weight) * total_budget
            allocation[p] = max(1, int(share))

        return allocation