import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings
from backend.shared.models import FlightSearchRequest, FlightOffer, FlightSegment, FlightSearchResponse

settings = get_settings()


class AmadeusClient:
    """Client for Amadeus Flight API"""

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

    async def search_flights(
        self, search_params: FlightSearchRequest
    ) -> FlightSearchResponse:
        """
        Search for flights using Amadeus API

        Args:
            search_params: Flight search parameters

        Returns:
            FlightSearchResponse with flight offers
        """
        token = await self.get_access_token()

        params = {
            "originLocationCode": search_params.origin.upper(),
            "destinationLocationCode": search_params.destination.upper(),
            "departureDate": search_params.departure_date.isoformat(),
            "adults": search_params.passengers,
            "nonStop": str(search_params.non_stop).lower(),
            "max": search_params.max_results,
        }

        if search_params.return_date:
            params["returnDate"] = search_params.return_date.isoformat()

        if search_params.flight_class.value != "economy":
            params["travelClass"] = search_params.flight_class.value.upper()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/shopping/flight-offers",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_flight_response(data)
            else:
                raise Exception(f"Amadeus API error: {response.text}")

    def _parse_flight_response(self, data: Dict[str, Any]) -> FlightSearchResponse:
        """Parse Amadeus API response into our model"""

        offers = []

        for offer_data in data.get("data", []):
            try:
                # Parse outbound segments
                outbound_segments = []
                for segment in offer_data["itineraries"][0]["segments"]:
                    outbound_segments.append(
                        FlightSegment(
                            departure_airport=segment["departure"]["iataCode"],
                            arrival_airport=segment["arrival"]["iataCode"],
                            departure_time=datetime.fromisoformat(
                                segment["departure"]["at"].replace("Z", "+00:00")
                            ),
                            arrival_time=datetime.fromisoformat(
                                segment["arrival"]["at"].replace("Z", "+00:00")
                            ),
                            airline=segment["carrierCode"],
                            flight_number=segment["number"],
                            duration=segment["duration"],
                            aircraft=segment.get("aircraft", {}).get("code"),
                        )
                    )

                # Parse return segments if exists
                return_segments = None
                if len(offer_data["itineraries"]) > 1:
                    return_segments = []
                    for segment in offer_data["itineraries"][1]["segments"]:
                        return_segments.append(
                            FlightSegment(
                                departure_airport=segment["departure"]["iataCode"],
                                arrival_airport=segment["arrival"]["iataCode"],
                                departure_time=datetime.fromisoformat(
                                    segment["departure"]["at"].replace("Z", "+00:00")
                                ),
                                arrival_time=datetime.fromisoformat(
                                    segment["arrival"]["at"].replace("Z", "+00:00")
                                ),
                                airline=segment["carrierCode"],
                                flight_number=segment["number"],
                                duration=segment["duration"],
                                aircraft=segment.get("aircraft", {}).get("code"),
                            )
                        )

                # Create flight offer
                price_data = offer_data["price"]
                offer = FlightOffer(
                    id=offer_data["id"],
                    price=float(price_data["total"]),
                    currency=price_data["currency"],
                    outbound_segments=outbound_segments,
                    return_segments=return_segments,
                    total_duration=offer_data["itineraries"][0]["duration"],
                    stops=len(outbound_segments) - 1,
                )

                offers.append(offer)

            except Exception as e:
                print(f"Error parsing offer: {e}")
                continue

        return FlightSearchResponse(
            results=offers,
            search_id=data.get("meta", {}).get("requestId", "unknown"),
            total_results=len(offers),
        )

    async def get_airport_info(self, iata_code: str) -> Dict[str, Any]:
        """Get airport information by IATA code"""
        token = await self.get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/reference-data/locations",
                params={
                    "subType": "AIRPORT",
                    "keyword": iata_code.upper(),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    return data["data"][0]
            return {}

    async def search_airports(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for airports by keyword"""
        token = await self.get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/reference-data/locations",
                params={
                    "subType": "AIRPORT,CITY",
                    "keyword": keyword,
                    "page[limit]": 10,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
