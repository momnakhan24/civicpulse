import uuid

from app.providers.triage.simulated import SimulatedTriage
from app.services.triage_service import run_triage


def test_fallback_when_provider_raises():
    failing_provider = SimulatedTriage(should_fail=True)
    unique_text = f"Burst water main flooding street {uuid.uuid4()}"

    outcome = run_triage(failing_provider, unique_text, "Gulshan")

    assert outcome.triaged_by == "rules:fallback"
    assert outcome.fallback is True
    assert outcome.result.category is not None
    assert outcome.result.priority is not None


def test_normal_triage_no_fallback():
    working_provider = SimulatedTriage()
    unique_text = f"Streetlight not working near park {uuid.uuid4()}"

    outcome = run_triage(working_provider, unique_text, "Sector 5")

    assert outcome.triaged_by == "simulated"
    assert outcome.fallback is False
