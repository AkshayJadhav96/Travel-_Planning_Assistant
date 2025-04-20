"""Hotel search tool module."""

import os
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv
from langchain.tools import tool
from loguru import logger

from unified_logging.logging_setup import setup_logging

from .pydantic_models import HotelOption, HotelSearchRequest, HotelSearchResponse

# HTTP status code constant
HTTP_OK = 200

# Initialize logging
setup_logging()
logger.info("Hotel search tool initializing")

# Load environment variables
MISSING_CREDENTIALS_ERROR = "Missing API credentials in environment variables"

def _check_api_credentials() -> None:
    """Check if hotel API credentials are available in environment variables."""
    hotel_api_key = os.getenv("HOTELS_API_KEY")
    hotel_api_secret = os.getenv("HOTELS_API_SECRET")
    if not hotel_api_key or not hotel_api_secret:
        raise ValueError(MISSING_CREDENTIALS_ERROR)

try:
    load_dotenv()
    _check_api_credentials()
    logger.success("Successfully loaded hotel API credentials")
except ValueError as e:
    logger.error(f"Failed to load environment variables: {e}")
    raise

# Load configuration
try:
    config_path = Path(__file__).parent / "config.yaml"
    with config_path.open() as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Hotels"]["BASE_URL"]
    logger.success("Successfully loaded hotel configuration")
except ValueError as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

@tool
def search_hotels(
    city_code: str = "NYC",
    radius: int = 1,
    radius_unit: str = "KM",
    amenities: str = "wifi,pool",
    ratings: str = "3,4",
) -> HotelSearchResponse:
    """Search for hotels using the Amadeus API and return results.

    Use when the user asks for hotel options in a city.

    Args:
        city_code: IATA city code (default = "NYC")
        radius: Search radius from city center (default = 1)
        radius_unit: "KM" or "MI" (default = "KM")
        amenities: Comma-separated list of amenities (default = "wifi,pool")
        ratings: Comma-separated list of rating (default="3,4")

    Returns:
        HotelSearchResponse with list of hotels or error message
    Input format: `search_hotels(city: str, radius: Optional[int],
    radius_unit: Optional[str], amenities: Optional[str], ratings: Optional[str])`

    """
    logger.info(
        f"Starting hotel search in {city_code} "
        f"(radius: {radius}{radius_unit}, amenities: {amenities}, ratings: {ratings})",
    )

    try:
        # Create request object
        request_data = HotelSearchRequest(
            city_code=city_code,
            radius=radius,
            radius_unit=radius_unit,
            amenities=amenities,
            ratings=ratings,
        )
        logger.debug(f"Created request object: {request_data}")

        # Get OAuth token
        logger.info("Requesting API access token")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("HOTELS_API_KEY"),
            "client_secret": os.getenv("HOTELS_API_SECRET"),
        }

        response = requests.post(BASE_URL, headers=headers, data=data, timeout=300)
        if response.status_code != HTTP_OK:
            error_msg = (
                f"Token request failed: {response.status_code} - {response.text}"
            )
            logger.error(error_msg)
            return HotelSearchResponse(error=error_msg)

        access_token = response.json().get("access_token")
        logger.success("Successfully obtained access token")

        # Search for hotels
        search_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "cityCode": request_data.city_code,
            "radius": request_data.radius,
            "radiusUnit": request_data.radius_unit,
            "amenities": request_data.amenities,
            "ratings": request_data.ratings,
        }
        logger.debug(f"Preparing hotel search with params: {params}")

        logger.info("Making hotel search request")
        response = requests.get(search_url, headers=headers, params=params, timeout=300)
        if response.status_code != HTTP_OK:
            error_msg = (
                f"Hotel search failed: {response.status_code} - {response.text}"
            )
            logger.error(error_msg)
            return HotelSearchResponse(error=error_msg)

        data = response.json().get("data", [])
        logger.info(f"Found {len(data)} hotel options")

        # Process hotel options
        hotels = [
            HotelOption(
                name=hotel["name"],
                hotel_id=hotel.get("hotelId", "Not specified"),
                address=hotel["address"].get("countryCode", "Not specified"),
                rating=str(hotel.get("rating", "Not rated")),
                amenities=hotel.get("amenities", []),
            )
            for hotel in data
        ]

        if not hotels:
            logger.warning(f"No hotels found in {city_code} matching criteria")
            return HotelSearchResponse(message=f"No hotels found in {city_code}")

        logger.success(f"Found {len(hotels)} hotels in {city_code}")
        logger.debug(f"Sample hotel: {hotels[0]}")
        return HotelSearchResponse(hotels=hotels)

    except ValueError as e:
        error_msg = f"Unexpected error in hotel search: {e!s}"
        logger.critical(error_msg)
        return HotelSearchResponse(error=error_msg)
