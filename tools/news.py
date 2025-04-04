import requests
from langchain.tools import tool
from typing import List
from .pydantic_models import NewsArticle
from dotenv import load_dotenv
import os

from loguru import logger
from unified_logging.logging_setup import setup_logging

# Initialize logging
setup_logging()
logger.info("News Search tool initializing")

load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

@tool
def get_news(location: str) -> List[NewsArticle]:
    """Get the news about a location and its surrounding by inputting the location"""
    logger.info(f"Received request to fetch news for location: '{location}'")

    if not isinstance(location, str) or not location.strip():
        logger.error("Invalid location provided. Must be a non-empty string.")
        raise ValueError("Location must be a non-empty string")

    url = f"https://newsapi.org/v2/everything?q={location}&from=today&sortBy=publishedAt&apiKey={API_KEY}"
    logger.debug(f"Sending request to News API: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("News API request successful")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data from News API: {e}")
        raise

    data = response.json()
    
    if "articles" not in data or not isinstance(data["articles"], list):
        logger.error("Invalid API response: Missing or incorrect 'articles' field")
        raise ValueError("Invalid API response: Missing or incorrect 'articles' field")

    news_articles = []
    logger.info(f"Processing up to 5 articles from response")
    for idx, article in enumerate(data["articles"][:5]):
        try:
            news_article = NewsArticle(
                Title=article["title"],
                URL=article["url"]
            )
            news_articles.append(news_article)
            # logger.debug(f"Article {idx + 1} added: {news_article.Title}")
        except Exception as e:
            logger.warning(f"Skipping an article due to validation error: {e}")

    logger.info(f"Returning {len(news_articles)} articles for location: '{location}'")
    return news_articles
