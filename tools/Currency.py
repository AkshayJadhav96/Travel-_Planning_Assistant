import requests
from tools.pydantic_models import ConvertedAmount,CurrencyData
from pydantic import ValidationError
from langchain.tools import tool
import os,yaml
from pathlib import Path
import sys


from loguru import logger
from unified_logging.logging_setup import setup_logging

setup_logging()
logger.info("Currency conversion tool starting up")

try:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Currency"]["BASE_URL"]
    logger.success("Successfully loaded configuration")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise


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

    logger.info(f"Starting currency conversion: {amount} {from_currency.upper()} to {to_currency.upper()}")

    from_currency = from_currency.lower()  # Convert to lowercase for API
    to_currency = to_currency.lower()

    # Construct the API endpoint
    url = f"{BASE_URL}{from_currency}.json"
    logger.debug(f"Constructed API URL: {url}")

    try:
        # Fetch data from the API
        logger.info("Making API request for currency data")
        response = requests.get(url)
        data = response.json()
        logger.success("Successfully received currency data from API")

        # Validate the API response with Pydantic
        if to_currency in data[from_currency]:
            rates = {to_currency: data[from_currency][to_currency]}
            logger.debug(f"Extracted exchange rate: {rates}")
        else:
            error_msg = f"Currency '{to_currency.upper()}' not available"
            logger.warning(error_msg)
            return {"error": error_msg}

        try:
            # Validate exchange rate data
            currency_data = CurrencyData(rates=rates)
        except ValidationError as e:
            error_msg = f"Data validation error: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        # Calculate and validate the final converted amount
        converted_amount = round(amount * currency_data.rates[to_currency], 2)
        logger.info(f"Converted amount: {amount} {from_currency.upper()} = {converted_amount} {to_currency.upper()}")
        
        result = ConvertedAmount(final_amount=converted_amount)
        logger.success("Conversion completed successfully")
        return result


    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {e}"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.critical(error_msg)
        return {"error": error_msg}
    
# if __name__ == "__main__":
#     print(convert_currency(1, "bdt", "inr"))  # Direct function call