from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.shared.config.database import Base


class User(Base):
    """User model for authentication and preferences"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    searches = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation/chat history model"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Individual chat message model"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class SearchHistory(Base):
    """Search history for flights, hotels, etc."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_type = Column(String(50), nullable=False)  # flight, hotel, weather
    search_params = Column(JSON, nullable=False)
    results_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="searches")


class Booking(Base):
    """Booking records for flights and hotels"""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_type = Column(String(50), nullable=False)  # flight, hotel
    booking_reference = Column(String(255), unique=True, nullable=False)
    details = Column(JSON, nullable=False)
    total_price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookings")


class Location(Base):
    """Cached location data"""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    iata_code = Column(String(3), unique=True, index=True, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
