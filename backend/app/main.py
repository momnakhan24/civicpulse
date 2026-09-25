from fastapi import FastAPI
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware
from app.routes.complaints import router as complaints_router

setup_logging()

app = FastAPI(title="CivicPulse API")
app.add_middleware(RequestIdMiddleware)
app.include_router(complaints_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "civicpulse-backend", "status": "ok"}
