"""News search tool module."""

import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from loguru import logger

from unified_logging.logging_setup import setup_logging

from .pydantic_models import NewsArticle

# Initialize logging
setup_logging()
logger.info("News Search tool initializing")

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# Error messages
INVALID_LOCATION_ERROR = "Location must be a non-empty string"
INVALID_RESPONSE_ERROR = "Invalid API response: Missing or incorrect 'articles' field"

@tool
def get_news(location: str) -> list[NewsArticle]:
    """Get the news about a location and its surrounding by inputting the location.

    Use when the user asks for news related to a specific city, country, or region.

    Args:
        location (str): The location to fetch news for.

    Returns:
        list[NewsArticle]: A list of news articles.

    """
    logger.info(f"Received request to fetch news for location: '{location}'")

    if not isinstance(location, str) or not location.strip():
        logger.error("Invalid location provided. Must be a non-empty string.")
        raise ValueError(INVALID_LOCATION_ERROR)

    url = f"https://newsapi.org/v2/everything?q={location}&from=today&sortBy=publishedAt&apiKey={API_KEY}"
    logger.debug(f"Sending request to News API: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.info("News API request successful")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from News API: {e}")
        raise

    data = response.json()

    if "articles" not in data or not isinstance(data["articles"], list):
        logger.error("Invalid API response: Missing or incorrect 'articles' field")
        raise ValueError(INVALID_RESPONSE_ERROR)

    news_articles = []
    logger.info("Processing up to 5 articles from response")
    for _idx, article in enumerate(data["articles"][:5]):
        try:
            news_article = NewsArticle(
                Title=article["title"],
                URL=article["url"],
            )
            news_articles.append(news_article)
        except ValueError as e:
            logger.warning(f"Skipping an article due to validation error: {e}")

    logger.info(f"Returning {len(news_articles)} articles for location: '{location}'")
    return news_articles
