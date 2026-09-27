import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text as sql_text

from app.database import engine
from app.config import settings

router = APIRouter(tags=["ops"])
logger = logging.getLogger("app")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    failed = []

    try:
        with engine.connect() as conn:
            conn.execute(sql_text("SELECT 1"))
    except Exception:
        failed.append("postgres")

    try:
        import redis

        r = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
    except Exception:
        failed.append("redis")

    if failed:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "failed_dependencies": failed},
        )

    return {"status": "ready"}
