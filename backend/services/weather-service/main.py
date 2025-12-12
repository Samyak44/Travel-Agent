from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings
from backend.shared.models import HealthCheckResponse, ServiceStatus
from backend.shared.utils import setup_logger
from routes import router as weather_router

settings = get_settings()
logger = setup_logger("weather-service")

app = FastAPI(
    title="Weather Service",
    description="Weather information service using OpenWeatherMap API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather_router, prefix="/api/weather", tags=["weather"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Weather Service",
        "version": "1.0.0",
        "status": "running",
        "provider": "OpenWeatherMap",
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        service="weather-service",
        status=ServiceStatus.HEALTHY,
        timestamp=datetime.now(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.weather_service_port,
        reload=True,
    )
