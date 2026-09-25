"""Settings — the only place apps/api reads the repo-root .env from.

pydantic-settings only; never read `.env` with open()/dotenv directly elsewhere.
NEVER log or echo a value from this module. `__repr_args__` is overridden (not
just `__repr__`) because pydantic v2's `BaseModel.__str__` and `__repr__` both
build their output from `__repr_args__` — overriding only `__repr__` would still
let `str(settings)` leak a secret.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Local infra — non-secret, defaults match docker-compose.yml / .env.example.
    DATABASE_URL: str = "postgresql+asyncpg://daari:daari@localhost:5432/daari"
    REDIS_URL: str = "redis://localhost:6379/0"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # LLM / live-source keys — secret, optional, never defaulted to a real value.
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    ADZUNA_APP_ID: str | None = None
    ADZUNA_APP_KEY: str | None = None
    SERPAPI_KEY: str | None = None
    SERPAPI_MONTHLY_BUDGET: int = 100

    # App config — non-secret.
    LLM_CACHE_DIR: str = ".cache/llm"
    TTS_VOICE_TE: str = "te-IN-ShrutiNeural"
    TTS_VOICE_HI: str = "hi-IN-SwaraNeural"
    TTS_VOICE_EN: str = "en-IN-NeerjaNeural"
    DAARI_SEED: int = 1337
    APP_ENV: str = "local"
    LOG_LEVEL: str = "info"
    DEFAULT_DISTRICT: str = "Guntur"

    def __repr_args__(self):
        """Both __repr__ and __str__ derive from this in pydantic v2 — keep it secret-free."""
        return [("app_env", self.APP_ENV)]


settings = Settings()
