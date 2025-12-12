from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import sys
import os
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_db
from backend.shared.models import FlightSearchRequest, FlightSearchResponse, ResponseModel
from backend.database.models import SearchHistory
from amadeus_client import AmadeusClient

router = APIRouter()

# Initialize Amadeus client
amadeus = AmadeusClient()


@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(
    search_request: FlightSearchRequest, db: Session = Depends(get_db)
):
    """
    Search for flights using Amadeus API

    Required parameters:
    - origin: Airport IATA code (e.g., "JFK", "LAX")
    - destination: Airport IATA code
    - departure_date: Departure date (YYYY-MM-DD)
    - passengers: Number of passengers

    Optional parameters:
    - return_date: Return date for round trip
    - flight_class: economy, premium_economy, business, first
    - non_stop: true for direct flights only
    - max_results: Maximum number of results (default 10)
    """
    try:
        # Search flights using Amadeus
        result = await amadeus.search_flights(search_request)

        # Save search to history (optional - if user_id is available)
        # This would require user authentication context
        # search_history = SearchHistory(
        #     user_id=user_id,  # from auth
        #     search_type="flight",
        #     search_params=search_request.model_dump(),
        #     results_count=result.total_results,
        # )
        # db.add(search_history)
        # db.commit()

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching flights: {str(e)}",
        )


@router.get("/airports/search")
async def search_airports(keyword: str):
    """
    Search for airports by keyword

    Example: /api/flights/airports/search?keyword=New York
    Returns list of airports matching the keyword
    """
    try:
        results = await amadeus.search_airports(keyword)

        return {
            "airports": [
                {
                    "iata_code": airport.get("iataCode"),
                    "name": airport.get("name"),
                    "city": airport.get("address", {}).get("cityName"),
                    "country": airport.get("address", {}).get("countryName"),
                }
                for airport in results
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching airports: {str(e)}",
        )


@router.get("/airports/{iata_code}")
async def get_airport_info(iata_code: str):
    """
    Get detailed information about an airport

    Example: /api/flights/airports/JFK
    """
    try:
        result = await amadeus.get_airport_info(iata_code)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Airport {iata_code} not found",
            )

        return {
            "iata_code": result.get("iataCode"),
            "name": result.get("name"),
            "city": result.get("address", {}).get("cityName"),
            "country": result.get("address", {}).get("countryName"),
            "timezone": result.get("timeZoneOffset"),
            "coordinates": {
                "latitude": result.get("geoCode", {}).get("latitude"),
                "longitude": result.get("geoCode", {}).get("longitude"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching airport info: {str(e)}",
        )


@router.get("/offers/{offer_id}")
async def get_flight_offer(offer_id: str):
    """
    Get detailed information about a specific flight offer

    This would typically be used after a search to get more details
    before booking
    """
    return ResponseModel(
        success=False,
        message="Flight offer details endpoint - Implementation pending",
        data={"offer_id": offer_id},
    )
