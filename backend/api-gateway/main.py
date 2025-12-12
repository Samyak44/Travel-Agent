from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.shared.config import get_settings
from backend.shared.models import HealthCheckResponse, ServiceStatus
from backend.shared.utils import setup_logger

settings = get_settings()
logger = setup_logger("api-gateway")

app = FastAPI(
    title="Travel Agent API Gateway",
    description="Central API gateway for the AI Travel Agent microservices platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

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
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.text else None,
                headers=dict(response.headers),
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
