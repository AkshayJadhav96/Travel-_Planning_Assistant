# import requests

# api_key="ff47b0668fd74e2599be21fff9382774"

# def get_news(location):
#     url = f"https://newsapi.org/v2/everything?q={location}&from=today&sortBy=publishedAt&apiKey={api_key}"
#     response = requests.get(url)
#     data = response.json()
#     # print(data)
#     return data["articles"]# Return top 5 news articles

# location = "Solapur"
# news = get_news(location)
# for article in news:
#     print(f"Title: {article['title']}\nURL: {article['url']}\n")
# # print(news)


import requests
from langchain.tools import tool
from typing import List
from .pydantic_models import NewsArticle

api_key_new="ff47b0668fd74e2599be21fff9382774"

@tool
def get_news(location: str) -> List[NewsArticle]:
    """Get the news about a location and its surrounding by inputting the location"""
    if not isinstance(location, str) or not location.strip():
        raise ValueError("Location must be a non-empty string")

    url = f"https://newsapi.org/v2/everything?q={location}&from=today&sortBy=publishedAt&apiKey={api_key_new}"
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