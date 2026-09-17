"""Settings. Values come from .env — never hardcoded, never logged."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    app_env: str = "local"
    log_level: str = "info"

    database_url: str = "postgresql+asyncpg://nadi:nadi@localhost:5432/nadi"
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str = "http://localhost:11434"

    gemini_api_key: str = ""
    groq_api_key: str = ""

    llm_cache_dir: str = ".cache/llm"
    router_seed: int = 1337

    # Free-tier rate limits, verified at /setup and re-verified on the provider console.
    # Written here so the token bucket has a real number instead of a guess.
    gemini_rpm: int = 10
    groq_rpm: int = 30


settings = Settings()
