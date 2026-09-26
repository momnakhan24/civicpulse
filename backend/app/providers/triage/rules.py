from app.providers.triage.base import TriageResult, Category, Priority

KEYWORDS: dict[Category, list[str]] = {
    Category.water: ["water", "pipe", "leak", "flood", "burst main", "sewage"],
    Category.electricity: ["electricity", "power", "wire", "transformer", "outage", "shock"],
    Category.sanitation: ["garbage", "trash", "sanitation", "sewer", "waste", "drain"],
    Category.roads: ["road", "pothole", "street damage", "traffic", "footpath"],
    Category.streetlights: ["streetlight", "street light", "lamp", "lighting"],
}

URGENT_WORDS = ["flooding", "burst", "fire", "collapse", "danger", "urgent", "emergency", "shock"]


class RuleBasedTriage:
    name = "rules"

    def triage(self, text: str, location: str) -> TriageResult:
        lowered = text.lower()

        matched_category = Category.other
        for category, keywords in KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                matched_category = category
                break

        priority = Priority.high if any(w in lowered for w in URGENT_WORDS) else Priority.normal

        summary = text.strip()[:137] + "..." if len(text.strip()) > 140 else text.strip()

        return TriageResult(
            category=matched_category,
            priority=priority,
            summary=summary,
            confidence=0.5,
        )
