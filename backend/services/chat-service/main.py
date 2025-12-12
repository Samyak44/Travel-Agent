from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings, get_db
from backend.shared.models import HealthCheckResponse, ServiceStatus
from backend.shared.utils import setup_logger
from routes import router as chat_router

settings = get_settings()
logger = setup_logger("chat-service")

app = FastAPI(
    title="Chat Service",
    description="AI-powered chat service using LangChain and OpenAI",
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
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Chat Service",
        "version": "1.0.0",
        "status": "running",
        "llm_provider": "OpenAI",
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        service="chat-service",
        status=ServiceStatus.HEALTHY,
        timestamp=datetime.now(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.chat_service_port,
        reload=True,
    )
