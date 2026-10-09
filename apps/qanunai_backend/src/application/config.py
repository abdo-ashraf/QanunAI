from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    rag_backend: Literal["pgvector", "qdrant"] = "pgvector"

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "qanunai_documents"
    qdrant_api_key: SecretStr | None = None

    pg_conn_str: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    pg_table_name: str = "qanunai_documents"

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
    retriever_score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    stores_path: str = "./stores"
    stores_index_on_startup: bool = True
    stores_chunk_size: int = 200
    stores_chunk_overlap: int = 20
    stores_manifest_path: str | None = None
    prompts_path: str = "prompts"

    generator_api_key: SecretStr
    generator_model: str = "gpt-4o-mini"
    generator_base_url: str | None = None

    langfuse_tracing_enabled: bool = False
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias=AliasChoices("LANGFUSE_BASE_URL", "LANGFUSE_HOST"),
    )
    langfuse_service_name: str = "qanunai-backend"


@lru_cache
def get_settings() -> Settings:
    return Settings()
