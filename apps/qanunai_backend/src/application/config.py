from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "qanunai_documents"
    qdrant_api_key: SecretStr | None = None

    @field_validator("qdrant_api_key", mode="before")
    @classmethod
    def _blank_qdrant_api_key_is_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    embedding_api_key: SecretStr
    embedding_model: str = "nomic-embed-text-v2-moe:latest"
    embedding_base_url: str | None = None
    embedding_dim: int = 768

    retriever_top_k: int = 5

    generator_api_key: SecretStr
    generator_model: str = "gpt-4o-mini"
    generator_base_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
