from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_db
from backend.shared.models import HotelSearchRequest, HotelSearchResponse
from backend.database.models import SearchHistory
from amadeus_client import AmadeusHotelClient

router = APIRouter()

# Initialize Amadeus hotel client
amadeus = AmadeusHotelClient()


@router.post("/search", response_model=HotelSearchResponse)
async def search_hotels(
    search_request: HotelSearchRequest, db: Session = Depends(get_db)
):
    """
    Search for hotels using Amadeus API

    Required parameters:
    - city_code: City IATA code (e.g., "NYC", "LON", "PAR")
    - check_in: Check-in date (YYYY-MM-DD)
    - check_out: Check-out date (YYYY-MM-DD)
    - guests: Number of guests
    - rooms: Number of rooms

    Optional parameters:
    - min_rating: Minimum hotel rating (1-5 stars)
    - max_price: Maximum price per night
    - amenities: List of required amenities
    - max_results: Maximum number of results (default 20)

    Note: Location is CRITICAL - use the /cities/search endpoint to find city codes
    """
    try:
        # Validate dates
        if search_request.check_out <= search_request.check_in:
            raise HTTPException(
                status_code=400,
                detail="Check-out date must be after check-in date",
            )

        # Search hotels using Amadeus
        result = await amadeus.search_hotels_by_city(search_request)

        # Save search to history (optional - if user_id is available)
        # search_history = SearchHistory(
        #     user_id=user_id,  # from auth
        #     search_type="hotel",
        #     search_params=search_request.model_dump(),
        #     results_count=result.total_results,
        # )
        # db.add(search_history)
        # db.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching hotels: {str(e)}",
        )


@router.get("/cities/search")
async def search_cities(keyword: str):
    """
    Search for cities by keyword to get city codes

    Example: /api/hotels/cities/search?keyword=Paris
    Returns list of cities matching the keyword with their IATA codes
    """
    try:
        results = await amadeus.search_city_by_name(keyword)

        return {
            "cities": [
                {
                    "iata_code": city.get("iataCode"),
                    "name": city.get("name"),
                    "city": city.get("address", {}).get("cityName"),
                    "country": city.get("address", {}).get("countryName"),
                    "coordinates": {
                        "latitude": city.get("geoCode", {}).get("latitude"),
                        "longitude": city.get("geoCode", {}).get("longitude"),
                    },
                }
                for city in results
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching cities: {str(e)}",
        )


@router.get("/{hotel_id}")
async def get_hotel_details(hotel_id: str):
    """
    Get detailed information about a specific hotel

    Example: /api/hotels/HOTEL123
    """
    try:
        result = await amadeus.get_hotel_details(hotel_id)

        if not result.get("data"):
            raise HTTPException(
                status_code=404,
                detail=f"Hotel {hotel_id} not found",
            )

        hotel_data = result["data"][0] if isinstance(result["data"], list) else result["data"]
        hotel = hotel_data.get("hotel", {})

        return {
            "hotel_id": hotel.get("hotelId"),
            "name": hotel.get("name"),
            "rating": hotel.get("rating"),
            "address": hotel.get("address", {}),
            "contact": hotel.get("contact", {}),
            "amenities": hotel.get("amenities", []),
            "description": hotel.get("description", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching hotel details: {str(e)}",
        )
