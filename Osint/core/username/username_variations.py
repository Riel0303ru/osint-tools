from __future__ import annotations

import re
from typing import List, Set


class UsernameVariations:

    def __init__(self):

        self.separators = ["", "_", ".", "-"]

        self.priority_numbers = [
            "1", "2", "3", "5", "7", "9",
            "10", "11", "12", "13", "21",
            "22", "33", "69", "77", "88",
            "99", "123", "777"
        ]

        self.linkedin_separator = "+"

    def normalize(self, text: str) -> str:

        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text

    def split(self, text: str) -> List[str]:

        return [
            w for w in self.normalize(text).split()
            if w
        ]

    def basic_variations(self, words: List[str]) -> Set[str]:

        out = set()

        if not words:
            return out

        if len(words) == 1:
            return {words[0]}

        first = words[0]
        last = words[-1]

        out.add(first)
        out.add(last)
        out.add(first + last)
        out.add(first + last[0])
        out.add(first[0] + last)

        for s in self.separators:
            out.add(s.join(words))
            out.add(first + s + last)

        return out

    def initials_variations(self, words: List[str]) -> Set[str]:

        out = set()

        if len(words) < 2:
            return out

        initials = "".join(w[0] for w in words if w)

        first = words[0]
        last = words[-1]

        out.add(initials)
        out.add(first[0] + last)
        out.add(first + last[0])

        for s in self.separators:
            out.add(first[0] + s + last)
            out.add(first + s + last[0])

        return out

    def linkedin_variations(self, words: List[str]) -> Set[str]:

        out = set()

        if not words:
            return out

        out.add(self.linkedin_separator.join(words))

        if len(words) >= 2:
            out.add(words[0] + self.linkedin_separator + words[-1])
            out.add(self.linkedin_separator.join(words[:2]))

        if len(words) >= 3:
            out.add(self.linkedin_separator.join(words[:3]))

        return out

    def numeric_variations(self, base: Set[str], limit: int = 10) -> Set[str]:

        out = set()
        numbers = self.priority_numbers[:limit]

        for b in base:
            for n in numbers:
                out.add(f"{b}{n}")

        return out

    def generate(self, target: str) -> List[str]:

        words = self.split(target)

        base: Set[str] = set()

        base.update(self.basic_variations(words))
        base.update(self.initials_variations(words))
        base.update(self.linkedin_variations(words))

        final: Set[str] = set(base)

        if len(base) < 60:
            final.update(self.numeric_variations(base, limit=8))

        cleaned = [
            x for x in final
            if 3 <= len(x) <= 30
        ]

        return sorted(cleaned)