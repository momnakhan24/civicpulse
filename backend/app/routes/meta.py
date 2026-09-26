from fastapi import APIRouter

from app.config import settings
from app.services.triage_observability import get_recent_outcomes
from app.services.triage_cache import get_cache_hit_rate

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/providers")
def get_provider_meta():
    return {
        "active_provider": settings.triage_provider,
        "recent_outcomes": get_recent_outcomes(),
        "triage_cache_hit_rate": get_cache_hit_rate(),
    }
