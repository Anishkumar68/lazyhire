from typing import Optional
from sqlalchemy import String, Boolean, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.models.base import TimestampMixin


class LLMProviderConfig(Base, TimestampMixin):
    __tablename__ = "llm_provider_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # openai, anthropic, gemini, deepseek, ollama
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    model_name: Mapped[str] = mapped_column(String(100))
    api_key_env_var: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=60)
    extra_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
