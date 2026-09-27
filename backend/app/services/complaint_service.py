import uuid

from sqlalchemy.orm import Session

from app.models import Complaint, Status
from app.providers.triage.base import TriageProvider
from app.repositories.complaint_repository import (
    create_complaint,
    get_complaint_by_id,
    list_complaints,
    update_status,
    get_stats,
)
from app.services.triage_service import run_triage
from app.services.state_machine import is_transition_allowed
from app.services.cache_service import invalidate_stats_cache


class InvalidTransitionError(Exception):
    def __init__(self, current: Status, attempted: Status):
        self.current = current
        self.attempted = attempted
        super().__init__(f"Cannot transition from {current.value} to {attempted.value}")


def submit_complaint(
    db: Session,
    provider: TriageProvider,
    text: str,
    location: str,
    reporter_contact: str | None,
) -> Complaint:
    outcome = run_triage(provider, text, location)

    complaint = Complaint(
        text=text,
        location=location,
        reporter_contact=reporter_contact,
        category=outcome.result.category,
        priority=outcome.result.priority,
        status=Status.open,
        ai_summary=outcome.result.summary,
        triaged_by=outcome.triaged_by,
        triage_latency_ms=outcome.latency_ms,
    )

    saved = create_complaint(db, complaint)
    invalidate_stats_cache()
    return saved


def get_complaint(db: Session, complaint_id: uuid.UUID) -> Complaint | None:
    return get_complaint_by_id(db, complaint_id)


def get_complaints_page(
    db: Session,
    category=None,
    priority=None,
    status=None,
    page: int = 1,
    page_size: int = 20,
):
    return list_complaints(db, category, priority, status, page, page_size)


def change_status(db: Session, complaint: Complaint, new_status: Status) -> Complaint:
    if not is_transition_allowed(complaint.status, new_status):
        raise InvalidTransitionError(complaint.status, new_status)
    return update_status(db, complaint, new_status)


def get_complaint_stats(db: Session) -> dict:
    return get_stats(db)
