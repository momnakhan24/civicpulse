from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.complaint_service import get_complaint_stats
from app.services.cache_service import get_cached_stats, set_cached_stats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats_endpoint(response: Response, db: Session = Depends(get_db)):
    cached = get_cached_stats()
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return cached

    stats = get_complaint_stats(db)
    set_cached_stats(stats)
    response.headers["X-Cache"] = "MISS"
    return stats
