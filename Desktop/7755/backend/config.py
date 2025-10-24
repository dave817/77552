"""
Configuration settings for the dating chatbot
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # SenseChat API credentials
    SENSENOVA_ACCESS_KEY_ID: str
    SENSENOVA_SECRET_ACCESS_KEY: str
    SENSENOVA_API_KEY: str
    MODEL_NAME: str = "SenseChat-Character-Pro"

    # API endpoints
    API_BASE_URL: str = "https://api.sensenova.cn/v1/llm"
    CHARACTER_CHAT_ENDPOINT: str = "/character/chat-completions"

    # Database
    DATABASE_URL: str = "sqlite:///./dating_chatbot.db"

    # API settings
    MAX_NEW_TOKENS: int = 1024
    RATE_LIMIT_RPM: int = 60
    TOKEN_EXPIRY_SECONDS: int = 1800  # 30 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
