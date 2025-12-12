from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""

    USER = "user"
    ADMIN = "admin"


class TravelPreferences(BaseModel):
    """User travel preferences"""

    preferred_class: Optional[str] = "economy"  # economy, business, first
    preferred_airlines: List[str] = []
    preferred_hotel_rating: Optional[int] = 3
    budget_range: Optional[dict] = {"min": 0, "max": 10000}
    dietary_restrictions: List[str] = []
    accessibility_needs: List[str] = []
    preferred_locations: List[str] = []
    travel_purpose: Optional[str] = None  # business, leisure, both

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base user model"""

    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """User creation model"""

    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """User update model"""

    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[TravelPreferences] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """User response model"""

    id: int
    role: UserRole
    preferences: Optional[TravelPreferences] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """User model with hashed password"""

    hashed_password: str


class Token(BaseModel):
    """JWT token model"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""

    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
