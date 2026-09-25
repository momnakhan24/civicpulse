from fastapi import FastAPI
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware
from app.routes.complaints import router as complaints_router
from app.routes.ops import router as ops_router
from app.routes.meta import router as meta_router
from app.routes.metrics import router as metrics_router

setup_logging()

app = FastAPI(title="CivicPulse API")
app.add_middleware(RequestIdMiddleware)
app.include_router(complaints_router)
app.include_router(ops_router)
app.include_router(meta_router)
app.include_router(metrics_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "civicpulse-backend", "status": "ok"}
