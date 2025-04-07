"""Pydantic models for Travel and Finance Assistant tools."""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


# Pydantic Models
class Condition(BaseModel):
    """Weather condition details."""

    text: str


class Day(BaseModel):
    """Daily weather forecast data."""

    mintemp_c: float = Field(..., alias="mintemp_c")
    maxtemp_c: float = Field(..., alias="maxtemp_c")
    maxwind_kph: float = Field(..., alias="maxwind_kph")
    avghumidity: float = Field(..., alias="avghumidity")
    daily_chance_of_rain: int = Field(..., alias="daily_chance_of_rain")
    daily_chance_of_snow: int = Field(..., alias="daily_chance_of_snow")
    condition: Condition


class ForecastDay(BaseModel):
    """Single day forecast in weather data."""

    date: str
    day: Day


class WeatherForecast(BaseModel):
    """Complete weather forecast structure."""

    forecastday: list[ForecastDay]


class FlightSearchRequest(BaseModel):
    """Request data for flight search."""

    source: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="IATA code of the departure airport",
    )
    destination: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="IATA code of the destination airport",
    )
    date: str = Field(
        ...,
        pattern=r"\d{4}-\d{2}-\d{2}",
        description="Travel date in 'YYYY-MM-DD' format",
    )
    adults: int = Field(1, gt=0, description="Number of adult passengers")
    currency: str = Field(
        "USD",
        min_length=3,
        max_length=3,
        description="Currency code for price display",
    )


class FlightOption(BaseModel):
    """Details of a single flight option."""

    airline: str
    departure_time: str
    arrival_time: str
    price: str


class FlightSearchResponse(BaseModel):
    """Response data for flight search."""

    flights: list[FlightOption] = []
    message: str | None = None
    error: str | None = None


class CurrencyData(BaseModel):
    """Currency exchange rate data."""

    rates: dict[str, float]


class ConvertedAmount(BaseModel):
    """Converted currency amount."""

    final_amount: float


class HotelSearchRequest(BaseModel):
    """Request data for hotel search."""

    city_code: str = Field(..., description="IATA city code")
    radius: int = Field(
        10,
        ge=1,
        description="Search radius around city center (default: 10 km)",
    )
    radius_unit: Literal["km", "mi", "KM", "MI"] = Field(
        "KM",
        description="Unit of radius (KM or MI)",
    )
    amenities: str = Field(None, description="Comma-separated list of amenities")
    ratings: str = Field(None, description="Comma-separated list of minimum ratings")


class HotelOption(BaseModel):
    """Details of a single hotel option."""

    name: str
    hotel_id: str | None
    address: str | None
    rating: str | None
    amenities: list[str]


class HotelSearchResponse(BaseModel):
    """Response data for hotel search."""

    hotels: list[HotelOption] | None = None
    message: str | None = None
    error: str | None = None


class NewsArticle(BaseModel):
    """News article details."""

    Title: str = Field(..., min_length=1)
    URL: HttpUrl
