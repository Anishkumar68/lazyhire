from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App Info
    PROJECT_NAME: str = "LazyHire"
    VERSION: str = "0.1.0"
    ENV: str 
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: SecretStr

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database
    DATABASE_URL: str 
    # Redis & Celery
    REDIS_URL: str 
    CELERY_BROKER_URL: str 
    CELERY_RESULT_BACKEND: str 

    # LLM Settings
    PRIMARY_LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Execution & Anti-Detection
    BROWSER_HEADLESS: bool = False
    STOP_BEFORE_SUBMIT: bool = True
    CLICK_GAP_MIN: float = 1.5
    CLICK_GAP_MAX: float = 4.0


settings = Settings()
