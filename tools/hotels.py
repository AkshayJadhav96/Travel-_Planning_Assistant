import requests
from .pydantic_models import HotelOption, HotelSearchRequest, HotelSearchResponse
from langchain.tools import tool
from dotenv import load_dotenv
import os
import yaml
from pathlib import Path

from loguru import logger
from unified_logging.logging_setup import setup_logging

# Initialize logging
setup_logging()
logger.info("Hotel search tool initializing")

# Load environment variables
try:
    load_dotenv()
    HOTEL_API_KEY = os.getenv("HOTELS_API_KEY")
    HOTEL_API_SECRET = os.getenv("HOTELS_API_SECRET")
    if not HOTEL_API_KEY or not HOTEL_API_SECRET:
        raise ValueError("Missing API credentials in environment variables")
    logger.success("Successfully loaded hotel API credentials")
except Exception as e:
    logger.error(f"Failed to load environment variables: {e}")
    raise

# Load configuration
try:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Hotels"]["BASE_URL"]
    logger.success("Successfully loaded hotel configuration")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

@tool
def search_hotels(
    city_code: str = "NYC",
    radius: int = 1,
    radius_unit: str = "KM",
    amenities: str = "",
    ratings: str = ""
) -> HotelSearchResponse:
    """
    Search for hotels using the Amadeus API and return results.
    Args:
        city_code: IATA city code (e.g. "NYC")
        radius: Search radius from city center
        radius_unit: "KM" or "MI"
        amenities: Comma-separated list of amenities
        ratings: Comma-separated list of rating filters
    Returns:
        HotelSearchResponse with list of hotels or error message
    """
    logger.info(
        f"Starting hotel search in {city_code} "
        f"(radius: {radius}{radius_unit}, amenities: {amenities}, ratings: {ratings})"
    )

    try:
        # Create request object
        request_data = HotelSearchRequest(
            city_code=city_code,
            radius=radius,
            radius_unit=radius_unit,
            amenities=amenities,
            ratings=ratings
        )
        logger.debug(f"Created request object: {request_data}")

        # Get OAuth token
        logger.info("Requesting API access token")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": HOTEL_API_KEY,
            "client_secret": HOTEL_API_SECRET
        }
        
        response = requests.post(BASE_URL, headers=headers, data=data)
        if response.status_code != 200:
            error_msg = f"Token request failed: {response.status_code} - {response.text}"
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
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code != 200:
            error_msg = f"Hotel search failed: {response.status_code} - {response.text}"
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
                amenities=hotel.get("amenities", [])
            )
            for hotel in data
        ]

        if not hotels:
            logger.warning(f"No hotels found in {city_code} matching criteria")
            return HotelSearchResponse(message=f"No hotels found in {city_code}")

        logger.success(f"Found {len(hotels)} hotels in {city_code}")
        logger.debug(f"Sample hotel: {hotels[0]}")
        return HotelSearchResponse(hotels=hotels)

    except Exception as e:
        error_msg = f"Unexpected error in hotel search: {str(e)}"
        logger.critical(error_msg)
        return HotelSearchResponse(error=error_msg)
