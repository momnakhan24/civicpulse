from app.providers.triage.simulated import SimulatedTriage
from app.services.triage_service import run_triage


def test_fallback_when_provider_raises():
    failing_provider = SimulatedTriage(should_fail=True)

    outcome = run_triage(failing_provider, "Burst water main flooding Street 12", "Gulshan")

    assert outcome.triaged_by == "rules:fallback"
    assert outcome.fallback is True
    assert outcome.result.category is not None
    assert outcome.result.priority is not None


def test_normal_triage_no_fallback():
    working_provider = SimulatedTriage()

    outcome = run_triage(working_provider, "Streetlight not working near park", "Sector 5")

    assert outcome.triaged_by == "simulated"
    assert outcome.fallback is False
