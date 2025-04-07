"""Amount converted from one currency to other."""

from pathlib import Path

import requests
import yaml
from langchain.tools import tool
from loguru import logger
from pydantic import ValidationError

from tools.pydantic_models import ConvertedAmount, CurrencyData
from unified_logging.logging_setup import setup_logging

setup_logging()
logger.info("Currency conversion tool starting up")

try:
    config_path = Path(__file__).parent / "config.yaml"
    with config_path.open() as file:
        config = yaml.safe_load(file)
    BASE_URL = config["Currency"]["BASE_URL"]
    logger.success("Successfully loaded configuration")
except ValueError as e:
    logger.error(f"Failed to load configuration: {e}")
    raise


@tool
def convert_currency(
    amount: float = 1, from_currency: str = "usd", to_currency: str = "inr",
) -> ConvertedAmount:
    """Convert a given amount from one currency to another.

    Args:
        amount (float): The amount to convert default is 1.
        from_currency (str): The source currency code (3 letter ISO, e.g., 'usd').
        to_currency (str): The target currency code (3 letter ISO, e.g., 'inr').

    Returns:
        dict: The converted amount with currency information.

    """
    logger.info(
        f"Starting currency conversion: {amount} {from_currency.upper()} to "
        f"{to_currency.upper()}",
    )

    from_currency = from_currency.lower()  # Convert to lowercase for API
    to_currency = to_currency.lower()

    # Construct the API endpoint
    url = f"{BASE_URL}{from_currency}.json"
    logger.debug(f"Constructed API URL: {url}")

    try:
        # Fetch data from the API
        logger.info("Making API request for currency data")
        response = requests.get(url, timeout=10)
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
        logger.info(
            f"Converted amount: {amount} {from_currency.upper()} = "
            f"{converted_amount} {to_currency.upper()}",
        )

        result = ConvertedAmount(final_amount=converted_amount)
        logger.success("Conversion completed successfully")
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {e}"
        logger.error(error_msg)
        return {"error": error_msg}
    except ValueError as e:
        error_msg = f"Unexpected error: {e}"
        logger.critical(error_msg)
        return {"error": error_msg}
    else:
        return result


# Renamed to avoid invalid module name issue
