from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings, get_db
from backend.shared.models import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    ResponseModel,
    TravelPreferences,
)
from backend.shared.utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_from_token,
)
from backend.database.models import User
from typing import List

router = APIRouter()
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


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


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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


@router.post("/login", response_model=Token)
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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user information"""

    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    if user_update.phone is not None:
        current_user.phone = user_update.phone

    if user_update.preferences is not None:
        current_user.preferences = user_update.preferences.model_dump()

    db.commit()
    db.refresh(current_user)

    return current_user


@router.put("/me/preferences", response_model=ResponseModel)
async def update_preferences(
    preferences: TravelPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user travel preferences"""

    current_user.preferences = preferences.model_dump()
    db.commit()

    return ResponseModel(
        success=True,
        message="Preferences updated successfully",
        data={"preferences": current_user.preferences},
    )


@router.get("/me/preferences", response_model=TravelPreferences)
async def get_preferences(current_user: User = Depends(get_current_user)):
    """Get user travel preferences"""

    if current_user.preferences:
        return TravelPreferences(**current_user.preferences)
    else:
        return TravelPreferences()


@router.delete("/me", response_model=ResponseModel)
async def delete_current_user(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete current user account"""

    db.delete(current_user)
    db.commit()

    return ResponseModel(
        success=True,
        message="User account deleted successfully",
    )
