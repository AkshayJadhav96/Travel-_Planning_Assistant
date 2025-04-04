import requests
from .pydantic_models import FlightSearchRequest, FlightSearchResponse, FlightOption
from langchain.tools import tool
from dotenv import load_dotenv
import os
import yaml
from pathlib import Path

from loguru import logger
from unified_logging.logging_setup import setup_logging

# Initialize logging
setup_logging()
logger.info("Flight search tool initializing")

# Load environment variables
try:
    load_dotenv()
    FLIGHTS_API_KEY = os.getenv("FLIGHTS_API_KEY")
    FLIGHTS_API_SECRET = os.getenv("FLIGHTS_API_SECRET")
    # print("##########################")
    # print(FLIGHTS_API_KEY,FLIGHTS_API_SECRET)
    # print("##########################")
    if not FLIGHTS_API_KEY or not FLIGHTS_API_SECRET:
        raise ValueError("Missing API credentials in environment variables")
    logger.success("Successfully loaded API credentials")
except Exception as e:
    logger.error(f"Failed to load environment variables: {e}")
    raise

# Load configuration
try:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Flights"]["BASE_URL"]
    logger.success("Successfully loaded configuration")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

@tool
def search_flights(source: str, destination: str, date: str, adults: int, currency: str) -> FlightSearchResponse:
    """
    Search for flights using Amadeus API and return results.
    Now accepts individual parameters instead of a Pydantic object.
    """
    logger.info(f"Starting flight search: {source}→{destination} on {date} for {adults} adult(s) in {currency}")
    
    try:
        # Create request object
        request_data = FlightSearchRequest(
            source=source,
            destination=destination,
            date=date,
            adults=adults or 1,
            currency=currency or "USD"
        )
        logger.debug(f"Created request object: {request_data}")

        # Get access token
        logger.info("Requesting API access token")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": FLIGHTS_API_KEY,
            "client_secret": FLIGHTS_API_SECRET
        }
        
        response = requests.post(BASE_URL, headers=headers, data=data)
        if response.status_code != 200:
            error_msg = f"Token request failed: {response.status_code} - {response.text}"
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
            "max": 5
        }
        logger.debug(f"Preparing flight search with params: {params}")

        logger.info("Making flight search request")
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code != 200:
            error_msg = f"Flight search failed: {response.status_code} - {response.text}"
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
                price=f"{flight['price']['total']} {request_data.currency}"
            )
            for flight in data
        ]

        if not flights:
            logger.warning("No flights found matching criteria")
            return FlightSearchResponse(message="No flights found")
        
        logger.success(f"Successfully found {len(flights)} flight options")
        return FlightSearchResponse(flights=flights)

    except Exception as e:
        error_msg = f"Unexpected error in flight search: {str(e)}"
        logger.critical(error_msg)
        return FlightSearchResponse(error=error_msg)

# Example usage:
request_data = FlightSearchRequest(source="JFK", destination="LHR", date="2025-04-10", adults=2, currency="USD")
# result = search_flights(request_data)
# print(result)