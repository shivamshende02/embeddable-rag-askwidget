from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Agentic RAG Widget API"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    BUSINESS_NAME: str
    SUPPORT_EMAIL: str
    ALLOWED_ORIGIN: str
    GREETING_MESSAGE: str = "Hi! How can I help you today?"


def get_settings() -> Settings:
    return Settings()