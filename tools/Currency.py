import requests
from .pydantic_models import ConvertedAmount,CurrencyData
from pydantic import ValidationError
from langchain.tools import tool
import os,yaml
from pathlib import Path

config_path = Path(__file__).parent / "config.yaml"
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

BASE_URL = config["Currency"]["BASE_URL"]


@tool
def convert_currency(amount: float = 1, from_currency: str = "usd", to_currency: str = "inr") -> ConvertedAmount:
    """
    Converts a given amount from one currency to another.
    Args:
        amount (float): The amount to convert.
        from_currency (str): The source currency code (e.g., 'usd').
        to_currency (str): The target currency code (e.g., 'inr').
    Returns:
        dict: The converted amount with currency information.
    """

    from_currency = from_currency.lower()  # Convert to lowercase for API
    to_currency = to_currency.lower()

    # Construct the API endpoint
    url = f"{BASE_URL}{from_currency}.json"

    try:
        # Fetch data from the API
        response = requests.get(url)
        data = response.json()

        # Validate the API response with Pydantic
        if to_currency in data[from_currency]:
            rates = {to_currency: data[from_currency][to_currency]}
        else:
            return {"error": f"Currency '{to_currency.upper()}' not available."}

        try:
            # Validate exchange rate data
            currency_data = CurrencyData(rates=rates)
        except ValidationError as e:
            return {"error": f"Data validation error: {e}"}

        # Calculate and validate the final converted amount
        converted_amount = round(amount * currency_data.rates[to_currency], 2)
        result = ConvertedAmount(final_amount=converted_amount)

        # Return the result as a dictionary
        return result

    except Exception as e:
        return {"error": f"Error fetching currency conversion data: {e}"}
    
# print(convert_currency(1, "bdt", "inr"))