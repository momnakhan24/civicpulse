import signal
import sys

from fastapi import FastAPI
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware
from app.routes.complaints import router as complaints_router
from app.routes.ops import router as ops_router
from app.routes.meta import router as meta_router
from app.routes.metrics import router as metrics_router
from app.routes.stats import router as stats_router
from app.database import engine

setup_logging()

app = FastAPI(title="CivicPulse API")
app.add_middleware(RequestIdMiddleware)
app.include_router(complaints_router)
app.include_router(ops_router)
app.include_router(meta_router)
app.include_router(metrics_router)
app.include_router(stats_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "civicpulse-backend", "status": "ok"}


def _handle_sigterm(signum, frame):
    engine.dispose()
    sys.exit(0)


signal.signal(signal.SIGTERM, _handle_sigterm)
