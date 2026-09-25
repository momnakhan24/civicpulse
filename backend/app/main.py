from fastapi import FastAPI

app = FastAPI(title="CivicPulse API")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "civicpulse-backend", "status": "ok"}
