import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Complaint, Status, Category, Priority


def create_complaint(db: Session, complaint: Complaint) -> Complaint:
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaint_by_id(db: Session, complaint_id: uuid.UUID) -> Complaint | None:
    return db.get(Complaint, complaint_id)


def list_complaints(
    db: Session,
    category: Category | None = None,
    priority: Priority | None = None,
    status: Status | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Complaint], int]:
    query = select(Complaint)

    if category is not None:
        query = query.where(Complaint.category == category)
    if priority is not None:
        query = query.where(Complaint.priority == priority)
    if status is not None:
        query = query.where(Complaint.status == status)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    query = query.order_by(Complaint.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    items = list(db.scalars(query).all())
    return items, total


def update_status(db: Session, complaint: Complaint, new_status: Status) -> Complaint:
    complaint.status = new_status
    complaint.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_stats(db: Session) -> dict:
    by_category = dict(
        db.execute(
            select(Complaint.category, func.count()).group_by(Complaint.category)
        ).all()
    )
    by_priority = dict(
        db.execute(
            select(Complaint.priority, func.count()).group_by(Complaint.priority)
        ).all()
    )
    return {
        "by_category": {k.value: v for k, v in by_category.items()},
        "by_priority": {k.value: v for k, v in by_priority.items()},
    }
