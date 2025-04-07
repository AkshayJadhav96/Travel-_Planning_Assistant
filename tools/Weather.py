"""Weather forecast tool module."""

import os
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv
from langchain.tools import tool
from loguru import logger
from pydantic import ValidationError

from unified_logging.logging_setup import setup_logging

from .pydantic_models import WeatherForecast

# Initialize logging
setup_logging()
logger.info("Weather forecast tool initializing")

# Load environment variables
MISSING_API_KEY_ERROR = "Missing WEATHER_API_KEY in environment variables"

def _check_api_key() -> None:
    """Check if the weather API key is available in environment variables."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError(MISSING_API_KEY_ERROR)

try:
    load_dotenv()
    _check_api_key()
    logger.success("Successfully loaded weather API credentials")
except ValueError as e:
    logger.error(f"Failed to load environment variables: {e}")
    raise

# Load configuration
try:
    config_path = Path(__file__).parent / "config.yaml"
    with config_path.open() as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Weather"]["BASE_URL"]
    logger.success("Successfully loaded weather configuration")
except ValueError as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

@tool
def get_weather(city: str, days: int = 1) -> list[str] | str:
    """Fetch the weather forecast for a given city and future dates.

    Args:
        city (str): The name of the city.
        days (int): Number of future days for the forecast (1-14 days).

    Returns:
        Union[List[dict], str]: The weather forecast summary as a list
         of dictionaries or an error message.

    """
    logger.info(f"Starting weather forecast for {city} (days: {days})")

    # Use forecast endpoint for future weather
    try:
        endpoint = f"{BASE_URL}/forecast.json"
        params = {"key": os.getenv("WEATHER_API_KEY"), "q": city, "days": days}
        logger.debug(f"Constructed API URL: {endpoint}")
        logger.debug("Request params: {**params, 'key': '***'}")  # Hide API key

        # Make API request
        logger.info("Making request to weather API")
        response = requests.get(endpoint, params=params, timeout=10)
        logger.debug(f"Received status code: {response.status_code}")

        data = response.json()

        # Handle API errors
        if "error" in data:
            error_msg = f"API error: {data['error']['message']}"
            logger.error(error_msg)
            return error_msg

        logger.info("Successfully received weather data")

        # Validate API response with Pydantic model
        try:
            forecast_data = WeatherForecast(forecastday=data["forecast"]["forecastday"])
            logger.debug("Successfully validated weather data")
        except ValidationError as e:
            error_msg = f"Data validation error: {e}"
            logger.error(error_msg)
            return error_msg

        # Create a list of dictionaries with validated data
        forecast_summary = f"📍 Weather forecast for {city}:\n\n"
        for day in forecast_data.forecastday:
            forecast_summary += (
                f"📅 Date: {day.date}\n"
                f"🌤 Weather: {day.day.condition.text}\n"
                f"🌡️ Temperature: {day.day.mintemp_c}°C - {day.day.maxtemp_c}°C\n"
                f"💨 Wind Speed: {day.day.maxwind_kph} Kph\n"
                f"💧 Humidity: {day.day.avghumidity}%\n"
                f"🌧️ Rain Probability: {day.day.daily_chance_of_rain}%\n"
                f"❄️ Snow Probability: {day.day.daily_chance_of_snow}%\n\n"
            )

        logger.success(f"Successfully generated {days}-day forecast for {city}")
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {e!s}"
        logger.error(error_msg)
        return error_msg
    except ValueError as e:
        error_msg = f"Unexpected error: {e!s}"
        logger.critical(error_msg)
        return error_msg
    else:
        return forecast_summary
