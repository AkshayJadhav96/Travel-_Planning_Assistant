"""Flight search tool module."""

import os
from datetime import datetime
from pathlib import Path

import pytz
import requests
import yaml
from dotenv import load_dotenv
from langchain.tools import tool
from loguru import logger

from unified_logging.logging_setup import setup_logging

from .pydantic_models import FlightOption, FlightSearchRequest, FlightSearchResponse

# HTTP status code constant
HTTP_OK = 200

# Initialize logging
setup_logging()
logger.info("Flight search tool initializing")

# Load environment variables
MISSING_CREDENTIALS_ERROR = "Missing API credentials in environment variables"

def _check_api_credentials() -> None:
    """Check if flight API credentials are available in environment variables."""
    flights_api_key = os.getenv("FLIGHTS_API_KEY")
    flights_api_secret = os.getenv("FLIGHTS_API_SECRET")
    if not flights_api_key or not flights_api_secret:
        raise ValueError(MISSING_CREDENTIALS_ERROR)

try:
    load_dotenv()
    _check_api_credentials()
    logger.success("Successfully loaded API credentials")
except ValueError as e:
    logger.error(f"Failed to load environment variables: {e}")
    raise

# Load configuration
try:
    config_path = Path(__file__).parent / "config.yaml"
    with config_path.open() as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Flights"]["BASE_URL"]
    logger.success("Successfully loaded configuration")
except ValueError as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

@tool
def search_flights(source: str,
                   destination: str,
                   date: str =  str(datetime.now(pytz.UTC).date()),
                   adults: int = 1,
                   currency: str = "USD",
                   ) -> FlightSearchResponse:
    """Search for flights between airports using Amadeus API and return results.

    Use when the user asks for flights between two cities/airports on a specific date.
    - Required: source IATA code, destination IATA code,
    date (YYYY-MM-DD) (default = use today's date tool to set input value of date).
    - Optional: number of adults (int default = 1),
    preferred currency (str default = "USD").

    Input format: `search_flights(source: str, destination: str,
    date: str, adults: Optional[int], currency: Optional[str])`

    """
    logger.info(
        f"Starting flight search: {source}→{destination} on {date} for {adults} "
        f"adult(s) in {currency}",
    )

    try:
        # Create request object
        request_data = FlightSearchRequest(
            source=source,
            destination=destination,
            date=date,
            adults=adults,
            currency=currency,
        )
        logger.debug(f"Created request object: {request_data}")

        # Get access token
        logger.info("Requesting API access token")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("FLIGHTS_API_KEY"),
            "client_secret": os.getenv("FLIGHTS_API_SECRET"),
        }

        response = requests.post(BASE_URL, headers=headers, data=data, timeout=10)
        if response.status_code != HTTP_OK:
            error_msg = f"Token request failed:{response.status_code} - {response.text}"
            logger.error(error_msg)
            return FlightSearchResponse(error=error_msg)

        access_token = response.json().get("access_token")
        logger.success("Successfully obtained access token")

        # Search for flights
        search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "originLocationCode": request_data.source,
            "destinationLocationCode": request_data.destination,
            "departureDate": request_data.date,
            "adults": request_data.adults,
            "currencyCode": request_data.currency,
            "max": 5,
        }
        logger.debug(f"Preparing flight search with params: {params}")

        logger.info("Making flight search request")
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        if response.status_code != HTTP_OK:
            error_msg = f"Flight search failed:{response.status_code} - {response.text}"
            logger.error(error_msg)
            return FlightSearchResponse(error=error_msg)

        data = response.json().get("data", [])
        logger.info(f"Found {len(data)} flight options")

        # Process flight options
        flights = [
            FlightOption(
                airline=flight["itineraries"][0]["segments"][0]["carrierCode"],
                departure_time=flight["itineraries"][0]["segments"][0]["departure"]["at"],
                arrival_time=flight["itineraries"][0]["segments"][-1]["arrival"]["at"],
                price=f"{flight['price']['total']} {request_data.currency}",
            )
            for flight in data
        ]

        if not flights:
            logger.warning("No flights found matching criteria")
            return FlightSearchResponse(message="No flights found")

        logger.success(f"Successfully found {len(flights)} flight options")
        return FlightSearchResponse(flights=flights)

    except ValueError as e:
        error_msg = f"Unexpected error in flight search: {e!s}"
        logger.critical(error_msg)
        return FlightSearchResponse(error=error_msg)

# Example usage:
request_data = FlightSearchRequest(
    source="JFK", destination="LHR", date="2025-04-10", adults=2, currency="USD",
)
