from app.models import Status
from app.services.state_machine import is_transition_allowed


def test_open_to_in_progress_allowed():
    assert is_transition_allowed(Status.open, Status.in_progress) is True


def test_open_to_rejected_allowed():
    assert is_transition_allowed(Status.open, Status.rejected) is True


def test_open_to_resolved_not_allowed():
    assert is_transition_allowed(Status.open, Status.resolved) is False


def test_in_progress_to_resolved_allowed():
    assert is_transition_allowed(Status.in_progress, Status.resolved) is True


def test_in_progress_to_rejected_allowed():
    assert is_transition_allowed(Status.in_progress, Status.rejected) is True


def test_resolved_is_terminal():
    assert is_transition_allowed(Status.resolved, Status.open) is False
    assert is_transition_allowed(Status.resolved, Status.in_progress) is False


def test_rejected_is_terminal():
    assert is_transition_allowed(Status.rejected, Status.open) is False
