from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Environment
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Database
    database_url: str = Field(
        default="postgresql://travelagent:password@localhost:5432/travelagent_db", alias="DATABASE_URL")
    postgres_user: str = Field(default="travelagent", alias="POSTGRES_USER")
    postgres_password: str = Field(
        default="password", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="travelagent_db", alias="POSTGRES_DB")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # OpenRouter (compatible with OpenAI API)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="openai/gpt-4", alias="OPENAI_MODEL")

    # Amadeus
    amadeus_api_key: Optional[str] = Field(
        default=None, alias="AMADEUS_API_KEY")
    amadeus_api_secret: Optional[str] = Field(
        default=None, alias="AMADEUS_API_SECRET")
    amadeus_base_url: str = Field(
        default="https://test.api.amadeus.com", alias="AMADEUS_BASE_URL")

    # Weather API
    weather_api_key: Optional[str] = Field(
        default=None, alias="WEATHER_API_KEY")
    weather_base_url: str = Field(
        default="https://api.openweathermap.org", alias="WEATHER_BASE_URL")
    # JWT & Security
    jwt_secret: str = Field(
        default="b4f4221f3d0e621e954d7eee86cfa7ec094fb3bf9f68e5c674edea029e10973d", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Service Ports
    api_gateway_port: int = Field(default=8000, alias="API_GATEWAY_PORT")
    chat_service_port: int = Field(default=8001, alias="CHAT_SERVICE_PORT")
    flight_service_port: int = Field(default=8002, alias="FLIGHT_SERVICE_PORT")
    hotel_service_port: int = Field(default=8003, alias="HOTEL_SERVICE_PORT")
    weather_service_port: int = Field(
        default=8004, alias="WEATHER_SERVICE_PORT")
    user_service_port: int = Field(default=8005, alias="USER_SERVICE_PORT")

    # Service URLs
    chat_service_url: str = Field(
        default="http://localhost:8001", alias="CHAT_SERVICE_URL")
    flight_service_url: str = Field(
        default="http://localhost:8002", alias="FLIGHT_SERVICE_URL")
    hotel_service_url: str = Field(
        default="http://localhost:8003", alias="HOTEL_SERVICE_URL")
    weather_service_url: str = Field(
        default="http://localhost:8004", alias="WEATHER_SERVICE_URL")
    user_service_url: str = Field(
        default="http://localhost:8005", alias="USER_SERVICE_URL")

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
