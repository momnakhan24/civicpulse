from collections import deque

from app.metrics import TRIAGE_LATENCY, TRIAGE_FALLBACK_COUNT

_recent_outcomes: deque = deque(maxlen=20)


def record_outcome(provider: str, latency_ms: int, fallback: bool) -> None:
    _recent_outcomes.appendleft(
        {"provider": provider, "latency_ms": latency_ms, "fallback": fallback}
    )
    TRIAGE_LATENCY.observe(latency_ms / 1000)
    if fallback:
        TRIAGE_FALLBACK_COUNT.inc()


def get_recent_outcomes() -> list[dict]:
    return list(_recent_outcomes)
