from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseModel(BaseModel):
    """Standard API response model"""

    success: bool
    message: str
    data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel):
    """Paginated response model"""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class ServiceStatus(str, Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    service: str
    status: ServiceStatus
    timestamp: datetime
    version: str = "1.0.0"

    model_config = ConfigDict(from_attributes=True)
