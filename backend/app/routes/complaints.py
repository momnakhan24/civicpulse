import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
    StatusUpdateRequest,
)
from app.models import Category, Priority, Status
from app.providers.triage.factory import get_triage_provider
from app.services.complaint_service import (
    submit_complaint,
    get_complaint,
    get_complaints_page,
    change_status,
    InvalidTransitionError,
)

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintResponse, status_code=201)
def create_complaint_endpoint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    provider = get_triage_provider()
    complaint = submit_complaint(
        db, provider, payload.text, payload.location, payload.reporter_contact
    )
    return complaint


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint_endpoint(complaint_id: uuid.UUID, db: Session = Depends(get_db)):
    complaint = get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.get("", response_model=ComplaintListResponse)
def list_complaints_endpoint(
    category: Category | None = None,
    priority: Priority | None = None,
    status: Status | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = get_complaints_page(db, category, priority, status, page, page_size)
    return ComplaintListResponse(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def update_status_endpoint(
    complaint_id: uuid.UUID, payload: StatusUpdateRequest, db: Session = Depends(get_db)
):
    complaint = get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")

    try:
        updated = change_status(db, complaint, payload.status)
        return updated
    except InvalidTransitionError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition from {exc.current.value} to {exc.attempted.value}",
        )
