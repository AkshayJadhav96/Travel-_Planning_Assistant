# from pydantic import BaseModel, Field
# from typing import List, Optional, Literal

# class FlightSearchRequest(BaseModel):
#     source: str = Field(..., min_length=3, max_length=3, description="IATA code of the departure airport")
#     destination: str = Field(..., min_length=3, max_length=3, description="IATA code of the destination airport")
#     date: str = Field(..., pattern="\\d{4}-\\d{2}-\\d{2}", description="Travel date in 'YYYY-MM-DD' format")
#     adults: int = Field(1, gt=0, description="Number of adult passengers")
#     currency: str = Field("USD", min_length=3, max_length=3, description="Currency code for price display")

# class FlightOption(BaseModel):
#     airline: str
#     departure_time: str
#     arrival_time: str
#     price: str

# class FlightSearchResponse(BaseModel):
#     flights: List[FlightOption] = []
#     message: Optional[str] = None
#     error: Optional[str] = None

# class HotelSearchRequest(BaseModel):
#     city_code: str = Field(..., min_length=3, max_length=3, description="IATA city code")
#     radius: int = Field(10, ge=1, description="Search radius around city center (default: 10 km)")
#     radius_unit: Literal["KM", "MI"] = Field("KM", description="Unit of radius (KM or MI)")
#     amenities: Optional[str] = Field(None, description="Comma-separated list of amenities")
#     ratings: Optional[str] = Field(None, description="Comma-separated list of minimum ratings")

# class HotelOption(BaseModel):
#     name: str
#     hotel_id: Optional[str]
#     address: Optional[str]
#     rating: Optional[str]
#     amenities: List[str]

# class HotelSearchResponse(BaseModel):
#     hotels: Optional[List[HotelOption]] = None
#     message: Optional[str] = None
#     error: Optional[str] = None

import requests
from typing import List,Optional,Dict, Literal
from pydantic import BaseModel, Field
from pydantic import BaseModel, HttpUrl, Field

# Pydantic Models
class Condition(BaseModel):
    text: str

class Day(BaseModel):
    mintemp_c: float = Field(..., alias="mintemp_c")
    maxtemp_c: float = Field(..., alias="maxtemp_c")
    maxwind_kph: float = Field(..., alias="maxwind_kph")
    avghumidity: float = Field(..., alias="avghumidity")
    daily_chance_of_rain: int = Field(..., alias="daily_chance_of_rain")
    daily_chance_of_snow: int = Field(..., alias="daily_chance_of_snow")
    condition: Condition

class ForecastDay(BaseModel):
    date: str
    day: Day

class WeatherForecast(BaseModel):
    forecastday: List[ForecastDay]

class FlightSearchRequest(BaseModel):
    source: str = Field(..., min_length=3, max_length=3, description="IATA code of the departure airport")
    destination: str = Field(..., min_length=3, max_length=3, description="IATA code of the destination airport")
    date: str = Field(..., pattern="\\d{4}-\\d{2}-\\d{2}", description="Travel date in 'YYYY-MM-DD' format")
    adults: int = Field(1, gt=0, description="Number of adult passengers")
    currency: str = Field("USD", min_length=3, max_length=3, description="Currency code for price display")

class FlightOption(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: str

class FlightSearchResponse(BaseModel):
    flights: List[FlightOption] = []
    message: Optional[str] = None
    error: Optional[str] = None

class CurrencyData(BaseModel):
    rates: Dict[str, float]


class ConvertedAmount(BaseModel):
    final_amount : float

class HotelSearchRequest(BaseModel):
    city_code: str = Field(..., description="IATA city code")
    radius: int = Field(10, ge=1, description="Search radius around city center (default: 10 km)")
    radius_unit: Literal["km","mi","KM", "MI"] = Field("KM", description="Unit of radius (KM or MI)")
    amenities: str = Field(None, description="Comma-separated list of amenities")
    ratings: str = Field(None, description="Comma-separated list of minimum ratings")

class HotelOption(BaseModel):
    name: str
    hotel_id: Optional[str]
    address: Optional[str]
    rating: Optional[str]
    amenities: List[str]

class HotelSearchResponse(BaseModel):
    hotels: Optional[List[HotelOption]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    
class NewsArticle(BaseModel):
    Title: str = Field(..., min_length=1)
    URL: HttpUrl
    