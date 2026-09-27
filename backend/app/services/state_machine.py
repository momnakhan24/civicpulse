from app.models import Status

ALLOWED_TRANSITIONS: dict[Status, set[Status]] = {
    Status.open: {Status.in_progress, Status.rejected},
    Status.in_progress: {Status.resolved, Status.rejected},
    Status.resolved: set(),
    Status.rejected: set(),
}


def is_transition_allowed(current: Status, new: Status) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())
