import requests
from langchain.tools import tool
from typing import List
from .pydantic_models import NewsArticle
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

@tool
def get_news(location: str) -> List[NewsArticle]:
    """Get the news about a location and its surrounding by inputting the location"""
    if not isinstance(location, str) or not location.strip():
        raise ValueError("Location must be a non-empty string")

    url = f"https://newsapi.org/v2/everything?q={location}&from=today&sortBy=publishedAt&apiKey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "articles" not in data or not isinstance(data["articles"], list):
        raise ValueError("Invalid API response: Missing or incorrect 'articles' field")

    news_articles = []
    for article in data["articles"][:5]:  # Return only top 5 articles
        try:
            news_article = NewsArticle(
                Title=article["title"],
                URL=article["url"]  # Ensure correct key (fixed from 'URl' to 'url')
            )
            news_articles.append(news_article)
        except Exception as e:
            print(f"Skipping an article due to validation error: {e}")

    return news_articles
