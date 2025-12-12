from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import sys
import os

# Add shared modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings, get_db
from backend.shared.models import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    HealthCheckResponse,
    ServiceStatus,
    ResponseModel,
)
from backend.shared.utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_from_token,
    setup_logger,
)
from routes import router as user_router
from datetime import datetime

settings = get_settings()
logger = setup_logger("user-service")

app = FastAPI(
    title="User Service",
    description="Authentication and user management service",
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
app.include_router(user_router, prefix="/api/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "User Service",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        service="user-service",
        status=ServiceStatus.HEALTHY,
        timestamp=datetime.now(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.user_service_port,
        reload=True,
    )
