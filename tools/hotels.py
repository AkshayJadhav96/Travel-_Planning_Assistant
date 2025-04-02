# import requests
# from .pydantic_models import HotelSearchRequest, HotelSearchResponse, HotelOption

# # Replace with your actual Amadeus API credentials
# API_KEY = "9jjmOUCJuaJV4fhWJntJugcbYSvmt5lU"
# API_SECRET = "iX5PadqYsoVa40M7"

# def search_hotels(request_data: HotelSearchRequest) -> HotelSearchResponse:
#     """
#     Search for hotels using the Amadeus API and return results.
#     """
#     # Get OAuth token
#     url = "https://test.api.amadeus.com/v1/security/oauth2/token"
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     data = {
#         "grant_type": "client_credentials",
#         "client_id": API_KEY,
#         "client_secret": API_SECRET
#     }
    
#     response = requests.post(url, headers=headers, data=data)
#     if response.status_code != 200:
#         return HotelSearchResponse(error=f"Failed to get access token: {response.json()}")

#     access_token = response.json().get("access_token")

#     # Search for hotels
#     url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     params = {
#         "cityCode": request_data.city_code,
#         "radius": request_data.radius,
#         "radiusUnit": request_data.radius_unit,
#         "amenities": request_data.amenities or "",
#         "ratings": request_data.ratings or "",
#     }
    
#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code != 200:
#         return HotelSearchResponse(error=f"API request failed: {response.json()}")

#     data = response.json().get("data", [])
#     hotels = [
#         HotelOption(
#             name=hotel["name"],
#             hotel_id=hotel.get("hotelId", "Not specified"),
#             address=hotel["address"].get("countryCode", "Not specified"),
#             rating=str(hotel.get("rating", "Not rated")),  # ✅ Fix: Cast rating to string
#             amenities=hotel.get("amenities", [])
#         )
#         for hotel in data
#     ]
    
#     return HotelSearchResponse(hotels=hotels) if hotels else HotelSearchResponse(message="No hotels found")

# # Example usage:
# request_data = HotelSearchRequest(city_code="NYC", radius=1, amenities="wifi,pool,spa,swimming_pool", ratings="2,3,4")
# # result = search_hotels(request_data)
# # print(result)


import requests

from .pydantic_models import HotelOption,HotelSearchRequest,HotelSearchResponse
from langchain.tools import tool

API_KEY_fl = "fNrC2Kg6bk0uRclgKL26udSxQsyzdKb9"
API_SECRET_fl = "NA71wALaHjIwi48o"


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
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY_fl,
        "client_secret": API_SECRET_fl
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
