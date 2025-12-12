import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings
from backend.shared.models import (
    HotelSearchRequest,
    HotelOffer,
    HotelSearchResponse,
    Coordinates,
)

settings = get_settings()


class AmadeusHotelClient:
    """Client for Amadeus Hotel API"""

    def __init__(self):
        self.api_key = settings.amadeus_api_key
        self.api_secret = settings.amadeus_api_secret
        self.base_url = settings.amadeus_base_url
        self.access_token = None

    async def get_access_token(self) -> str:
        """Get OAuth access token from Amadeus"""
        if self.access_token:
            return self.access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.api_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                return self.access_token
            else:
                raise Exception(f"Failed to get access token: {response.text}")

    async def search_hotels_by_city(
        self, search_params: HotelSearchRequest
    ) -> HotelSearchResponse:
        """
        Search for hotels by city code

        Args:
            search_params: Hotel search parameters

        Returns:
            HotelSearchResponse with hotel offers
        """
        token = await self.get_access_token()

        # Step 1: Get hotel IDs for the city
        hotel_ids = await self._get_hotel_ids_by_city(
            city_code=search_params.city_code, token=token
        )

        if not hotel_ids:
            return HotelSearchResponse(results=[], search_id="empty", total_results=0)

        # Step 2: Get hotel offers for those IDs
        params = {
            "hotelIds": ",".join(hotel_ids[: search_params.max_results]),
            "checkInDate": search_params.check_in.isoformat(),
            "checkOutDate": search_params.check_out.isoformat(),
            "adults": search_params.guests,
            "roomQuantity": search_params.rooms,
        }

        if search_params.max_price:
            params["priceRange"] = f"0-{int(search_params.max_price)}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v3/shopping/hotel-offers",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_hotel_response(data, search_params.min_rating)
            else:
                raise Exception(f"Amadeus API error: {response.text}")

    async def _get_hotel_ids_by_city(self, city_code: str, token: str) -> List[str]:
        """Get hotel IDs for a city"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/reference-data/locations/hotels/by-city",
                params={"cityCode": city_code.upper()},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                return [hotel["hotelId"] for hotel in data.get("data", [])[:100]]
            return []

    def _parse_hotel_response(
        self, data: Dict[str, Any], min_rating: Optional[int]
    ) -> HotelSearchResponse:
        """Parse Amadeus hotel API response into our model"""

        offers = []

        for hotel_data in data.get("data", []):
            try:
                hotel = hotel_data.get("hotel", {})
                offer_data = hotel_data.get("offers", [{}])[0]

                # Get price
                price = offer_data.get("price", {})
                total_price = float(price.get("total", 0))
                currency = price.get("currency", "USD")

                # Calculate nights and price per night
                check_in = datetime.fromisoformat(
                    offer_data.get("checkInDate", "2024-01-01")
                )
                check_out = datetime.fromisoformat(
                    offer_data.get("checkOutDate", "2024-01-02")
                )
                nights = (check_out - check_in).days or 1
                price_per_night = total_price / nights

                # Get rating (if available)
                rating = hotel.get("rating")
                if rating:
                    rating = float(rating)

                # Filter by rating if specified
                if min_rating and rating and rating < min_rating:
                    continue

                # Get coordinates
                coords = None
                if hotel.get("latitude") and hotel.get("longitude"):
                    coords = Coordinates(
                        latitude=float(hotel["latitude"]),
                        longitude=float(hotel["longitude"]),
                    )

                # Create hotel offer
                hotel_offer = HotelOffer(
                    id=hotel.get("hotelId", "unknown"),
                    name=hotel.get("name", "Unknown Hotel"),
                    rating=rating,
                    price_per_night=price_per_night,
                    total_price=total_price,
                    currency=currency,
                    address=hotel.get("address", {}).get("lines", [""])[0],
                    city=hotel.get("address", {}).get("cityName", ""),
                    country=hotel.get("address", {}).get("countryCode", ""),
                    coordinates=coords,
                    amenities=hotel.get("amenities", []),
                    description=offer_data.get("description", {}).get("text"),
                )

                offers.append(hotel_offer)

            except Exception as e:
                print(f"Error parsing hotel offer: {e}")
                continue

        # Sort by rating (highest first) then by price (lowest first)
        offers.sort(key=lambda x: (-x.rating if x.rating else 0, x.total_price))

        return HotelSearchResponse(
            results=offers,
            search_id=data.get("meta", {}).get("requestId", "unknown"),
            total_results=len(offers),
        )

    async def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific hotel"""
        token = await self.get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/shopping/hotel-offers/by-hotel",
                params={"hotelId": hotel_id},
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                return response.json()
            return {}

    async def search_city_by_name(self, city_name: str) -> List[Dict[str, Any]]:
        """Search for city codes by name"""
        token = await self.get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/reference-data/locations",
                params={
                    "subType": "CITY",
                    "keyword": city_name,
                    "page[limit]": 10,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
