from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Environment
    environment: str = "development"

    # Database
    database_url: str
    postgres_user: str = "travelagent"
    postgres_password: str
    postgres_db: str = "travelagent_db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"

    # Amadeus
    amadeus_api_key: Optional[str] = None
    amadeus_api_secret: Optional[str] = None
    amadeus_base_url: str = "https://test.api.amadeus.com"

    # Weather API
    weather_api_key: Optional[str] = None
    weather_base_url: str = "https://api.openweathermap.org/data/2.5"

    # JWT & Security
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Service Ports
    api_gateway_port: int = 8000
    chat_service_port: int = 8001
    flight_service_port: int = 8002
    hotel_service_port: int = 8003
    weather_service_port: int = 8004
    user_service_port: int = 8005

    # Service URLs
    chat_service_url: str = "http://localhost:8001"
    flight_service_url: str = "http://localhost:8002"
    hotel_service_url: str = "http://localhost:8003"
    weather_service_url: str = "http://localhost:8004"
    user_service_url: str = "http://localhost:8005"

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
