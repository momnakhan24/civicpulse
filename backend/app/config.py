from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    redis_url: str
    triage_provider: str = "simulated"

    groq_api_key: str = "changeme"
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"

    log_level: str = "INFO"
    rate_limit_per_minute: int = 20


settings = Settings()
