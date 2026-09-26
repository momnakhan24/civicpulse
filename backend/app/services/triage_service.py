import logging
import time

from app.providers.triage.base import TriageProvider, TriageResult
from app.providers.triage.rules import RuleBasedTriage
from app.services.triage_observability import record_outcome
from app.services.triage_cache import get_cached_triage, set_cached_triage

logger = logging.getLogger("app")


class TriageOutcome:
    def __init__(self, result: TriageResult, triaged_by: str, latency_ms: int, fallback: bool):
        self.result = result
        self.triaged_by = triaged_by
        self.latency_ms = latency_ms
        self.fallback = fallback


def run_triage(provider: TriageProvider, text: str, location: str) -> TriageOutcome:
    start = time.monotonic()

    cached_result = get_cached_triage(text)
    if cached_result is not None:
        latency_ms = int((time.monotonic() - start) * 1000)
        record_outcome(f"{provider.name}:cached", latency_ms, False)
        return TriageOutcome(
            result=cached_result,
            triaged_by=f"{provider.name}:cached",
            latency_ms=latency_ms,
            fallback=False,
        )

    try:
        result = provider.triage(text, location)
        latency_ms = int((time.monotonic() - start) * 1000)
        set_cached_triage(text, result)
        record_outcome(provider.name, latency_ms, False)
        return TriageOutcome(
            result=result,
            triaged_by=provider.name,
            latency_ms=latency_ms,
            fallback=False,
        )
    except Exception as exc:
        logger.warning(
            f"Triage fallback triggered: provider={provider.name} error={type(exc).__name__}"
        )
        fallback_provider = RuleBasedTriage()
        result = fallback_provider.triage(text, location)
        latency_ms = int((time.monotonic() - start) * 1000)
        record_outcome("rules:fallback", latency_ms, True)
        return TriageOutcome(
            result=result,
            triaged_by="rules:fallback",
            latency_ms=latency_ms,
            fallback=True,
        )
