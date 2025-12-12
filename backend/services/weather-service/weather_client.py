import httpx
from typing import Dict, Any, List
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings
from backend.shared.models import (
    WeatherResponse,
    CurrentWeather,
    WeatherForecast,
    Coordinates,
)

settings = get_settings()


class WeatherClient:
    """Client for OpenWeatherMap API"""

    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_base_url

    async def get_current_weather(self, city: str) -> WeatherResponse:
        """
        Get current weather for a city

        Args:
            city: City name (e.g., "London", "New York")

        Returns:
            WeatherResponse with current weather and forecast
        """
        async with httpx.AsyncClient() as client:
            # Get current weather
            current_response = await client.get(
                f"{self.base_url}/weather",
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",  # Celsius
                },
                timeout=30.0,
            )

            if current_response.status_code != 200:
                raise Exception(f"Weather API error: {current_response.text}")

            current_data = current_response.json()

            # Get forecast
            forecast_response = await client.get(
                f"{self.base_url}/forecast",
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": 40,  # 5 days, 8 times per day
                },
                timeout=30.0,
            )

            forecast_data = (
                forecast_response.json() if forecast_response.status_code == 200 else {}
            )

            return self._parse_weather_response(current_data, forecast_data)

    async def get_weather_by_coords(
        self, latitude: float, longitude: float
    ) -> WeatherResponse:
        """
        Get weather by coordinates

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            WeatherResponse with current weather and forecast
        """
        async with httpx.AsyncClient() as client:
            # Get current weather
            current_response = await client.get(
                f"{self.base_url}/weather",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=30.0,
            )

            if current_response.status_code != 200:
                raise Exception(f"Weather API error: {current_response.text}")

            current_data = current_response.json()

            # Get forecast
            forecast_response = await client.get(
                f"{self.base_url}/forecast",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": 40,
                },
                timeout=30.0,
            )

            forecast_data = (
                forecast_response.json() if forecast_response.status_code == 200 else {}
            )

            return self._parse_weather_response(current_data, forecast_data)

    def _parse_weather_response(
        self, current_data: Dict[str, Any], forecast_data: Dict[str, Any]
    ) -> WeatherResponse:
        """Parse OpenWeatherMap API response"""

        # Parse current weather
        current = CurrentWeather(
            temperature=current_data["main"]["temp"],
            feels_like=current_data["main"]["feels_like"],
            humidity=current_data["main"]["humidity"],
            pressure=current_data["main"]["pressure"],
            condition=current_data["weather"][0]["main"],
            description=current_data["weather"][0]["description"],
            wind_speed=current_data["wind"]["speed"],
            clouds=current_data["clouds"]["all"],
            visibility=current_data.get("visibility"),
        )

        # Parse coordinates
        coords = Coordinates(
            latitude=current_data["coord"]["lat"],
            longitude=current_data["coord"]["lon"],
        )

        # Parse forecast (group by day and get one forecast per day)
        forecasts = []
        seen_dates = set()

        for item in forecast_data.get("list", []):
            date = datetime.fromtimestamp(item["dt"])
            date_str = date.date().isoformat()

            # Only take one forecast per day (around noon)
            if date_str not in seen_dates and date.hour >= 11 and date.hour <= 13:
                seen_dates.add(date_str)

                forecast = WeatherForecast(
                    date=date,
                    temperature_min=item["main"]["temp_min"],
                    temperature_max=item["main"]["temp_max"],
                    condition=item["weather"][0]["main"],
                    description=item["weather"][0]["description"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item["wind"]["speed"],
                    precipitation_probability=item.get("pop", 0) * 100,  # Convert to percentage
                )

                forecasts.append(forecast)

        return WeatherResponse(
            location=current_data["name"],
            coordinates=coords,
            current=current,
            forecast=forecasts,
            timezone=current_data.get("timezone", "UTC"),
        )

    async def get_air_quality(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get air quality index for a location

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Air quality data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://api.openweathermap.org/data/2.5/air_pollution",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                aqi_data = data["list"][0] if data.get("list") else {}

                # AQI levels: 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
                aqi_levels = {
                    1: "Good",
                    2: "Fair",
                    3: "Moderate",
                    4: "Poor",
                    5: "Very Poor",
                }

                aqi = aqi_data.get("main", {}).get("aqi", 0)

                return {
                    "aqi": aqi,
                    "quality": aqi_levels.get(aqi, "Unknown"),
                    "components": aqi_data.get("components", {}),
                }

            return {"error": "Could not fetch air quality data"}
