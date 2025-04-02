import requests
from .pydantic_models import FlightSearchRequest,FlightSearchResponse,FlightOption
from langchain.tools import tool
from dotenv import load_dotenv
import os,yaml
from pathlib import Path

load_dotenv()
FLIGHTS_API_KEY = os.getenv("FLIGHTS_API_KEY")
FLIGHTS_API_SECRET = os.getenv("FLIGHTS_API_SECRET")

config_path = Path(__file__).parent / "config.yaml"
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

BASE_URL = config["Flights"]["BASE_URL"]

@tool
def search_flights(source: str, destination: str, date: str, adults: int,currency: str) -> FlightSearchResponse:
    """
    Search for flights using Amadeus API and return results.
    Now accepts individual parameters instead of a Pydantic object.
    """
    adults = adults or 1
    currency = currency or "USD"
    # Create the request object from parameters
    request_data = FlightSearchRequest(
        source=source,
        destination=destination,
        date=date,
        adults=adults,
        currency=currency
    )
    
    # Rest of your existing implementation...
    url = BASE_URL
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": FLIGHTS_API_KEY,
        "client_secret": FLIGHTS_API_SECRET
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        return FlightSearchResponse(error=f"Failed to get access token: {response.json()}")
    
    access_token = response.json().get("access_token")
    
    # Search for flights
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": request_data.source,
        "destinationLocationCode": request_data.destination,
        "departureDate": request_data.date,
        "adults": request_data.adults,
        "currencyCode": request_data.currency,
        "max": 5  # Limit to 5 flights
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return FlightSearchResponse(error=f"API request failed: {response.json()}")
    
    data = response.json().get("data", [])
    flights = [
        FlightOption(
            airline=flight["itineraries"][0]["segments"][0]["carrierCode"],
            departure_time=flight["itineraries"][0]["segments"][0]["departure"]["at"],
            arrival_time=flight["itineraries"][0]["segments"][-1]["arrival"]["at"],
            price=f"{flight['price']['total']} {request_data.currency}"
        )
        for flight in data
    ]
    
    return FlightSearchResponse(flights=flights) if flights else FlightSearchResponse(message="No flights found")


# Example usage:
request_data = FlightSearchRequest(source="JFK", destination="LHR", date="2025-04-10", adults=2, currency="USD")
# result = search_flights(request_data)
# print(result)