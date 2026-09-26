from app.config import settings
from app.providers.triage.base import TriageProvider
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage
from app.providers.triage.llm import LLMTriage


def get_triage_provider() -> TriageProvider:
    provider_name = settings.triage_provider.lower()

    if provider_name == "rules":
        return RuleBasedTriage()
    if provider_name == "simulated":
        return SimulatedTriage()
    if provider_name == "llm":
        return LLMTriage()

    raise ValueError(f"Unknown or not-yet-wired TRIAGE_PROVIDER: {provider_name}")
