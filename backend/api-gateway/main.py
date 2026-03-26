from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import httpx
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings, get_db
from backend.shared.models import (
    HealthCheckResponse,
    ServiceStatus,
    UserCreate,
    UserResponse,
    Token,
)
from backend.shared.utils import (
    setup_logger,
    hash_password,
    verify_password,
    create_access_token,
    get_user_from_token,
)
from backend.database.models import User, Base
from backend.shared.config.database import engine

settings = get_settings()
logger = setup_logger("api-gateway")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

app = FastAPI(
    title="Travel Agent API Gateway",
    description="Central API gateway for the AI Travel Agent microservices platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup with retry logic"""
    import time
    max_retries = 10
    for i in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            break
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"Database not ready, retrying in 2s... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                logger.error(f"Failed to create database tables: {e}")
                raise


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Service registry
SERVICES = {
    "users": settings.user_service_url,
    "chat": settings.chat_service_url,
    "flights": settings.flight_service_url,
    "hotels": settings.hotel_service_url,
    "weather": settings.weather_service_url,
}


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AI Travel Agent API Gateway",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "users": f"{settings.user_service_url}",
            "chat": f"{settings.chat_service_url}",
            "flights": f"{settings.flight_service_url}",
            "hotels": f"{settings.hotel_service_url}",
            "weather": f"{settings.weather_service_url}",
        },
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        service="api-gateway",
        status=ServiceStatus.HEALTHY,
        timestamp=datetime.now(),
    )


@app.get("/health/services")
async def check_all_services():
    """Check health of all microservices"""
    health_status = {}

    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(
                    f"{service_url}/health", timeout=5.0
                )
                if response.status_code == 200:
                    health_status[service_name] = "healthy"
                else:
                    health_status[service_name] = "degraded"
            except Exception as e:
                health_status[service_name] = f"down: {str(e)}"
                logger.error(f"Service {service_name} health check failed: {e}")

    return {
        "gateway": "healthy",
        "services": health_status,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== Auth Endpoints ====================

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user_data = get_user_from_token(token)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_data["user_id"]).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@app.post("/api/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role.value,
        is_active=user_data.is_active,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/api/users/login", response_model=Token, tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me", response_model=UserResponse, tags=["auth"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ==================== Proxy Middleware ====================

# Proxy middleware for routing requests to services
@app.api_route(
    "/api/users/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["users"],
)
async def proxy_users(path: str, request: Request):
    """Proxy requests to User Service"""
    return await proxy_request("users", path, request)


@app.api_route(
    "/users/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["users"],
)
async def proxy_users_no_prefix(path: str, request: Request):
    """Proxy requests to User Service (without /api prefix)"""
    return await proxy_request("users", path, request)


@app.api_route(
    "/api/chat/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["chat"],
)
async def proxy_chat(path: str, request: Request):
    """Proxy requests to Chat Service"""
    return await proxy_request("chat", path, request)


@app.api_route(
    "/api/flights/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["flights"],
)
async def proxy_flights(path: str, request: Request):
    """Proxy requests to Flight Service"""
    return await proxy_request("flights", path, request)


@app.api_route(
    "/api/hotels/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["hotels"],
)
async def proxy_hotels(path: str, request: Request):
    """Proxy requests to Hotel Service"""
    return await proxy_request("hotels", path, request)


@app.api_route(
    "/api/weather/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["weather"],
)
async def proxy_weather(path: str, request: Request):
    """Proxy requests to Weather Service"""
    return await proxy_request("weather", path, request)


async def proxy_request(service: str, path: str, request: Request):
    """
    Proxy a request to a microservice

    Args:
        service: Service name (users, chat, flights, hotels, weather)
        path: API path
        request: Original FastAPI request

    Returns:
        Response from the microservice
    """
    service_url = SERVICES.get(service)

    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")

    # Build target URL
    target_url = f"{service_url}/api/{service}/{path}"

    # Get request body if exists
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()

    # Forward headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header

    # Get query parameters
    query_params = dict(request.query_params)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                params=query_params,
                timeout=60.0,
            )

            # Return the response
            try:
                resp_content = response.json() if response.text else None
            except Exception:
                resp_content = {"detail": response.text or "Unknown error from service"}

            # Filter out hop-by-hop headers that conflict with JSONResponse
            excluded_headers = {"content-length", "content-encoding", "transfer-encoding"}
            resp_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() not in excluded_headers
            }

            return JSONResponse(
                status_code=response.status_code,
                content=resp_content,
                headers=resp_headers,
            )

    except httpx.TimeoutException:
        logger.error(f"Timeout while proxying to {service}: {target_url}")
        raise HTTPException(
            status_code=504,
            detail=f"Service {service} timed out",
        )
    except httpx.RequestError as e:
        logger.error(f"Error while proxying to {service}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service {service} unavailable: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error while proxying to {service}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.api_gateway_port,
        reload=True,
    )
