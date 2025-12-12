from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==================== Location Models ====================
class Location(BaseModel):
    """Location/Place model"""

    city: str
    country: str
    iata_code: Optional[str] = None  # Airport code
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class Coordinates(BaseModel):
    """Geographic coordinates"""

    latitude: float
    longitude: float


# ==================== Flight Models ====================
class FlightClass(str, Enum):
    """Flight class enumeration"""

    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class FlightSearchRequest(BaseModel):
    """Flight search request"""

    origin: str = Field(..., description="Origin airport IATA code (e.g., JFK)")
    destination: str = Field(..., description="Destination airport IATA code")
    departure_date: date
    return_date: Optional[date] = None
    passengers: int = Field(1, ge=1, le=9)
    flight_class: FlightClass = FlightClass.ECONOMY
    non_stop: bool = False
    max_results: int = Field(10, ge=1, le=50)

    model_config = ConfigDict(from_attributes=True)


class FlightSegment(BaseModel):
    """Flight segment/leg"""

    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    airline: str
    flight_number: str
    duration: str  # e.g., "2h 30m"
    aircraft: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FlightOffer(BaseModel):
    """Flight offer/result"""

    id: str
    price: float
    currency: str = "USD"
    outbound_segments: List[FlightSegment]
    return_segments: Optional[List[FlightSegment]] = None
    total_duration: str
    stops: int
    booking_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FlightSearchResponse(BaseModel):
    """Flight search response"""

    results: List[FlightOffer]
    search_id: str
    total_results: int

    model_config = ConfigDict(from_attributes=True)


# ==================== Hotel Models ====================
class HotelSearchRequest(BaseModel):
    """Hotel search request"""

    city_code: str = Field(..., description="City IATA code")
    check_in: date
    check_out: date
    guests: int = Field(1, ge=1, le=9)
    rooms: int = Field(1, ge=1, le=9)
    min_rating: Optional[int] = Field(None, ge=1, le=5)
    max_price: Optional[float] = None
    amenities: Optional[List[str]] = None  # wifi, pool, parking, etc.
    max_results: int = Field(20, ge=1, le=50)

    model_config = ConfigDict(from_attributes=True)


class HotelAmenity(BaseModel):
    """Hotel amenity"""

    name: str
    available: bool


class HotelOffer(BaseModel):
    """Hotel offer/result"""

    id: str
    name: str
    rating: Optional[float] = None  # 1-5 stars
    price_per_night: float
    total_price: float
    currency: str = "USD"
    address: str
    city: str
    country: str
    coordinates: Optional[Coordinates] = None
    amenities: List[str] = []
    description: Optional[str] = None
    images: List[str] = []
    booking_url: Optional[str] = None
    distance_from_center: Optional[float] = None  # in km

    model_config = ConfigDict(from_attributes=True)


class HotelSearchResponse(BaseModel):
    """Hotel search response"""

    results: List[HotelOffer]
    search_id: str
    total_results: int

    model_config = ConfigDict(from_attributes=True)


# ==================== Weather Models ====================
class WeatherCondition(str, Enum):
    """Weather condition enumeration"""

    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    MIST = "mist"


class CurrentWeather(BaseModel):
    """Current weather data"""

    temperature: float  # Celsius
    feels_like: float
    humidity: int  # percentage
    pressure: int  # hPa
    condition: str
    description: str
    wind_speed: float  # m/s
    clouds: int  # percentage
    visibility: Optional[int] = None  # meters

    model_config = ConfigDict(from_attributes=True)


class WeatherForecast(BaseModel):
    """Weather forecast for a specific date"""

    date: datetime
    temperature_min: float
    temperature_max: float
    condition: str
    description: str
    humidity: int
    wind_speed: float
    precipitation_probability: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class WeatherResponse(BaseModel):
    """Weather response"""

    location: str
    coordinates: Coordinates
    current: CurrentWeather
    forecast: List[WeatherForecast] = []
    timezone: str

    model_config = ConfigDict(from_attributes=True)


# ==================== Chat/Conversation Models ====================
class MessageRole(str, Enum):
    """Message role enumeration"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message"""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class ConversationContext(BaseModel):
    """Conversation context for LLM"""

    user_id: int
    conversation_id: str
    user_preferences: Optional[dict] = None
    current_location: Optional[Location] = None
    travel_dates: Optional[dict] = None  # start_date, end_date
    budget: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Chat request"""

    user_id: int
    message: str
    conversation_id: Optional[str] = None
    context: Optional[ConversationContext] = None

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    """Chat response"""

    conversation_id: str
    message: str
    suggestions: Optional[List[str]] = None
    action_required: Optional[str] = None  # "search_flights", "search_hotels", etc.
    action_params: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
