import requests

from .pydantic_models import HotelOption,HotelSearchRequest,HotelSearchResponse
from langchain.tools import tool

from dotenv import load_dotenv
import os,yaml
from pathlib import Path

load_dotenv()
HOTEL_API_KEY = os.getenv("HOTELS_API_KEY")
HOTEL_API_SECRET = os.getenv("HOTELS_API_SECRET")

config_path = Path(__file__).parent / "config.yaml"
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

BASE_URL = config["Hotels"]["BASE_URL"]


@tool
def search_hotels(city_code: str = "NYC",radius: int = 1,radius_unit: str = "KM", ammenities: str = "",ratings: str = "") -> HotelSearchResponse:
    """
    Search for hotels using the Amadeus API and return results.
    """
    request_data = HotelSearchRequest(
        city_code=city_code,
        radius=radius,
        radius_unit=radius_unit,
        ammenities=ammenities,
        ratings=ratings
    )
    
    # Get OAuth token
    url = BASE_URL
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": HOTEL_API_KEY,
        "client_secret": HOTEL_API_SECRET
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        return HotelSearchResponse(error=f"Failed to get access token: {response.json()}")

    access_token = response.json().get("access_token")

    # Search for hotels
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "cityCode": request_data.city_code,
        "radius": request_data.radius,
        "radiusUnit": request_data.radius_unit,
        "amenities": request_data.amenities,
        "ratings": request_data.ratings,
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return HotelSearchResponse(error=f"API request failed: {response.json()}")

    data = response.json().get("data", [])
    hotels = [
        HotelOption(
            name=hotel["name"],
            hotel_id=hotel.get("hotelId", "Not specified"),
            address=hotel["address"].get("countryCode", "Not specified"),
            rating=str(hotel.get("rating", "Not rated")),  # ✅ Fix: Cast rating to string
            amenities=hotel.get("amenities", [])
        )
        for hotel in data
    ]
    
    return HotelSearchResponse(hotels=hotels) if hotels else HotelSearchResponse(message="No hotels found")
