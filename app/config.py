from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Configuración de la aplicación obtenida del entorno."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "Agente profesional de Mario"
    app_version: str = "0.1.0"
    app_environment: str = "development"

    # Clave que protege la entrada al agente. Es independiente de las claves de
    # los proveedores de IA y puede rotarse sin modificar el código.
    agent_api_key: SecretStr | None = None

    # Controles de abuso del endpoint público. El límite de cuerpo se expresa
    # en bytes y se aplica antes de que FastAPI deserialice el JSON.
    max_request_body_bytes: int = Field(default=524_288, ge=1_024)
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = Field(default=20, ge=1)

    openai_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_generation_model: str = "gpt-5.6-luna"
    openai_reasoning_effort: Literal[
        "none", "low", "medium", "high", "xhigh", "max"
    ] = "none"
    openai_text_verbosity: Literal["low", "medium", "high"] = "low"
    openai_timeout_seconds: float = 30.0
    openai_max_retries: int = 2
    generation_max_output_tokens: int = 500

    knowledge_dir: Path = PROJECT_ROOT / "knowledge"
    chroma_path: Path = PROJECT_ROOT / "data" / "chroma"
    chroma_collection: str = "banorte_cv_v1"

    rag_top_k: int = 4
    rag_candidate_k: int = 16
    rag_max_per_document: int = 2
    rag_source_breadth_penalty: float = 0.005
    rag_lexical_bonus: float = 0.05
    rag_min_score: float | None = None

    rag_chunk_min_tokens: int = 150
    rag_chunk_target_tokens: int = 350
    rag_chunk_max_tokens: int = 450
    rag_chunk_overlap_tokens: int = 50

    @field_validator("knowledge_dir", "chroma_path")
    @classmethod
    def resolve_project_path(cls, value: Path) -> Path:
        return value if value.is_absolute() else PROJECT_ROOT / value


@lru_cache
def get_settings() -> Settings:
    return Settings()
