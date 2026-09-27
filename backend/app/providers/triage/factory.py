from app.config import settings
from app.providers.triage.base import TriageProvider
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage
from app.providers.triage.llm import LLMTriage
from app.providers.triage.ollama import OllamaTriage


def get_triage_provider() -> TriageProvider:
    provider_name = settings.triage_provider.lower()

    if provider_name == "rules":
        return RuleBasedTriage()
    if provider_name == "simulated":
        return SimulatedTriage()
    if provider_name == "llm":
        return LLMTriage()
    if provider_name == "ollama":
        return OllamaTriage()

    raise ValueError(f"Unknown TRIAGE_PROVIDER: {provider_name}")
