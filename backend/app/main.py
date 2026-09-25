from fastapi import FastAPI
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware

setup_logging()

app = FastAPI(title="CivicPulse API")
app.add_middleware(RequestIdMiddleware)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "civicpulse-backend", "status": "ok"}
