from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings
from backend.shared.models import HealthCheckResponse, ServiceStatus
from backend.shared.utils import setup_logger
from routes import router as flight_router

settings = get_settings()
logger = setup_logger("flight-service")

app = FastAPI(
    title="Flight Service",
    description="Flight search and booking service using Amadeus API",
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
app.include_router(flight_router, prefix="/api/flights", tags=["flights"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Flight Service",
        "version": "1.0.0",
        "status": "running",
        "provider": "Amadeus",
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        service="flight-service",
        status=ServiceStatus.HEALTHY,
        timestamp=datetime.now(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.flight_service_port,
        reload=True,
    )
