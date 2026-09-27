import uuid
from app.database import SessionLocal
from app.models import Complaint, Category, Priority, Status
from app.repositories.complaint_repository import (
    create_complaint, get_complaint_by_id, list_complaints, update_status, get_stats
)


def make_complaint(text_suffix=""):
    return Complaint(
        text=f"Test complaint text for repository {uuid.uuid4()}{text_suffix}",
        location="Test Location",
        category=Category.water,
        priority=Priority.high,
        status=Status.open,
        triaged_by="rules",
        triage_latency_ms=1,
    )


def test_create_and_get_complaint():
    db = SessionLocal()
    complaint = make_complaint()
    saved = create_complaint(db, complaint)
    fetched = get_complaint_by_id(db, saved.id)
    assert fetched is not None
    assert fetched.text == saved.text
    db.close()


def test_get_nonexistent_complaint_returns_none():
    db = SessionLocal()
    result = get_complaint_by_id(db, uuid.uuid4())
    assert result is None
    db.close()


def test_list_complaints_with_filter():
    db = SessionLocal()
    complaint = make_complaint()
    create_complaint(db, complaint)
    items, total = list_complaints(db, category=Category.water, page=1, page_size=100)
    assert total >= 1
    assert all(item.category == Category.water for item in items)
    db.close()


def test_update_status():
    db = SessionLocal()
    complaint = make_complaint()
    saved = create_complaint(db, complaint)
    updated = update_status(db, saved, Status.in_progress)
    assert updated.status == Status.in_progress
    db.close()


def test_get_stats_returns_dict():
    db = SessionLocal()
    stats = get_stats(db)
    assert "by_category" in stats
    assert "by_priority" in stats
    db.close()
