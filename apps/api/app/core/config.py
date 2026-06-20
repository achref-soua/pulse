from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://pulse:pulse_dev_only@db:5432/pulse"
    postgres_user: str = "pulse"
    postgres_password: str = "pulse_dev_only"
    postgres_db: str = "pulse"

    # Quiver
    quiver_url: str = "http://quiver:8080"
    quiver_api_key: str = "dev-quiver-key-change-me"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # JWT
    jwt_secret: str = "dev-jwt-secret-change-in-production-min-32-chars!!"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_router_model: str = "llama-3.1-8b-instant"
    groq_temperature: float = 0.3

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    rerank_enabled: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # App
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3100"]

    # Demo credentials (seed only)
    demo_surgeon_email: str = "surgeon@demo.pulse"
    demo_surgeon_password: str = "demo-surgeon-2024"
    demo_anesthetist_email: str = "anesthetist@demo.pulse"
    demo_anesthetist_password: str = "demo-anesthetist-2024"
    demo_nurse_email: str = "nurse@demo.pulse"
    demo_nurse_password: str = "demo-nurse-2024"
    demo_admin_email: str = "admin@demo.pulse"
    demo_admin_password: str = "demo-admin-2024"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    def check_production_secrets(self) -> None:
        """Raise at startup if any placeholder secret is used in production."""
        if self.environment != "production":
            return
        placeholder_prefix = "dev-"
        if self.jwt_secret.startswith(placeholder_prefix):
            raise RuntimeError("JWT_SECRET must be set to a real secret in production")
        if self.quiver_api_key.startswith(placeholder_prefix):
            raise RuntimeError("QUIVER_API_KEY must be set to a real key in production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
