from fastapi import APIRouter, HTTPException, Query
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.models import WeatherResponse
from weather_client import WeatherClient

router = APIRouter()

# Initialize weather client
weather_client = WeatherClient()


@router.get("/city/{city_name}", response_model=WeatherResponse)
async def get_weather_by_city(city_name: str):
    """
    Get current weather and 5-day forecast for a city

    Example: /api/weather/city/London
    Example: /api/weather/city/New York

    Returns:
    - Current weather conditions
    - Temperature, humidity, wind speed
    - 5-day forecast
    - Location coordinates
    """
    try:
        result = await weather_client.get_current_weather(city_name)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching weather data: {str(e)}",
        )


@router.get("/coordinates", response_model=WeatherResponse)
async def get_weather_by_coordinates(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
):
    """
    Get weather by geographic coordinates

    Example: /api/weather/coordinates?latitude=51.5074&longitude=-0.1278

    Returns:
    - Current weather conditions
    - Temperature, humidity, wind speed
    - 5-day forecast
    """
    try:
        result = await weather_client.get_weather_by_coords(latitude, longitude)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching weather data: {str(e)}",
        )


@router.get("/air-quality")
async def get_air_quality(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
):
    """
    Get air quality index for a location

    Example: /api/weather/air-quality?latitude=51.5074&longitude=-0.1278

    Returns:
    - Air Quality Index (AQI)
    - Quality level (Good, Fair, Moderate, Poor, Very Poor)
    - Component concentrations (CO, NO2, O3, PM2.5, PM10, etc.)
    """
    try:
        result = await weather_client.get_air_quality(latitude, longitude)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching air quality data: {str(e)}",
        )


@router.get("/query")
async def query_weather(q: str = Query(..., description="City name or location")):
    """
    Simple weather query endpoint (used by chat agent)

    Example: /api/weather/query?q=Paris

    Returns simplified weather information
    """
    try:
        result = await weather_client.get_current_weather(q)

        return {
            "location": result.location,
            "current": {
                "temperature": f"{result.current.temperature}°C",
                "feels_like": f"{result.current.feels_like}°C",
                "condition": result.current.description,
                "humidity": f"{result.current.humidity}%",
                "wind_speed": f"{result.current.wind_speed} m/s",
            },
            "forecast": [
                {
                    "date": f.date.strftime("%Y-%m-%d"),
                    "temp_range": f"{f.temperature_min}°C - {f.temperature_max}°C",
                    "condition": f.description,
                    "rain_probability": f"{f.precipitation_probability}%",
                }
                for f in result.forecast[:5]
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching weather: {str(e)}",
        )
