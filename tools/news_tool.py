import os
import time
import json
import requests
from pydantic import BaseModel, Field

NEWS_API_BASE_URL = "https://min-api.cryptocompare.com/data/v2/news/"
NEWS_API_KEY = os.getenv("CRYPTO_COMPARE_API_KEY")

def fetch_news(token: str, timestamp: int = None):
    """Fetches news for a specific token and timestamp."""
    # Use current time if no timestamp provided
    if timestamp is None:
        timestamp = int(time.time())

    print(f"Fetching news for timestamp: {timestamp}")
    url = f"{NEWS_API_BASE_URL}?lang=EN&lTs={timestamp}&categories={token}&sign=true"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {NEWS_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"

    return response.json()

class FetchNewsInput(BaseModel):
    """Input schema for fetching news."""
    token: str = Field(..., description="Token symbol (e.g., BTC, ETH, SOL)")
    timestamp: int = Field(
        None,
        description=
        "Unix timestamp to search for news (optional, defaults to current time)"
    )

def fetch_news_tool(token: str, timestamp: int = None):
    """Fetch news articles for a token at a specific timestamp."""
    news_data = fetch_news(token, timestamp)
    return json.dumps(news_data, indent=2)