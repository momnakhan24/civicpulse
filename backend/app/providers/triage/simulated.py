import hashlib

from app.providers.triage.base import TriageResult, Category, Priority


class SimulatedTriage:
    name = "simulated"

    def __init__(self, should_fail: bool = False, return_malformed: bool = False):
        self.should_fail = should_fail
        self.return_malformed = return_malformed

    def triage(self, text: str, location: str) -> TriageResult:
        if self.should_fail:
            raise RuntimeError("Simulated provider failure")

        if self.return_malformed:
            raise ValueError("Simulated malformed output from provider")

        digest = hashlib.md5(text.encode()).hexdigest()
        categories = list(Category)
        priorities = list(Priority)

        category = categories[int(digest[0], 16) % len(categories)]
        priority = priorities[int(digest[1], 16) % len(priorities)]

        summary = text.strip()[:137] + "..." if len(text.strip()) > 140 else text.strip()

        return TriageResult(
            category=category,
            priority=priority,
            summary=summary,
            confidence=0.9,
        )
