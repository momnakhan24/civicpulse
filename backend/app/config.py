from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql://user:pass@localhost:5432/civicpulse"
    redis_url: str = "redis://localhost:6379/0"
    triage_provider: str = "simulated"
    groq_api_key: str = ""
    ollama_host: str = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()
