import requests
from typing import Union,List
from pydantic import ValidationError
from .pydantic_models import WeatherForecast
from langchain.tools import tool
from dotenv import load_dotenv
import os,yaml
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

config_path = Path(__file__).parent / "config.yaml"
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

BASE_URL = config["Weather"]["BASE_URL"]

@tool
def get_weather(city: str, days: int = 1) -> Union[List[str], str]:
    """
    Fetches the weather forecast for a given city and future dates.
    Args:
        city (str): The name of the city.
        days (int): Number of future days for the forecast (1-14 days).
    Returns:
        Union[List[dict], str]: The weather forecast summary as a list of dictionaries or an error message.
    """

    # Use forecast endpoint for future weather
    endpoint = f"{BASE_URL}/forecast.json"
    params = {"key": API_KEY, "q": city, "days": days}

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()

        # Handle API errors
        if "error" in data:
            return f"Error: {data['error']['message']}"

        # Validate API response with Pydantic model
        try:
            forecast_data = WeatherForecast(forecastday=data["forecast"]["forecastday"])
        except ValidationError as e:
            return f"Error validating data: {e}"

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
        
        return forecast_summary

    except Exception as e:
        return f"Error fetching weather data: {e}"

# Test: Get a 3-day forecast for Mumbai
# print(get_weather("Mumbai", days=3))
