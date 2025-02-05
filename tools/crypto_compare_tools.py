from typing import List
import os
import time
import json
import requests
from pydantic import BaseModel, Field

CRYPTO_COMPARE_BASE_URL = "https://min-api.cryptocompare.com"
CRYPTO_COMPARE_API_KEY = os.getenv("CRYPTO_COMPARE_API_KEY")

class FetchNewsInput(BaseModel):
    """Input schema for fetching news."""
    token: str = Field(..., description="Token symbol to fetch news for (e.g., BTC, ETH, SOL)")
    timestamp: int = Field(
        None,
        description=
        "Unix timestamp to search for news (optional, defaults to current time)"
    )

class FetchPriceInput(BaseModel):
    """Input schema for fetching crypto prices."""
    from_symbol: str = Field(
        ..., 
        description="Base cryptocurrency symbol to get prices for (e.g., 'BTC', 'ETH')"
    )
    to_symbols: List[str] = Field(
        ..., 
        description="List of target currencies to get prices in (e.g., ['USD', 'EUR', 'JPY']). Can include both fiat and crypto currencies"
    )

class FetchTradingSignalsInput(BaseModel):
    """Input schema for fetching IntoTheBlock trading signals."""
    from_symbol: str = Field(
        ..., 
        description="Cryptocurrency symbol to fetch trading signals for (e.g., 'BTC'). Returns detailed market indicators and analytics"
    )

class FetchTopMarketCapInput(BaseModel):
    """Input schema for fetching top cryptocurrencies by market cap."""
    limit: int = Field(
        10, 
        description="Number of top cryptocurrencies to return, ordered by market capitalization"
    )
    to_symbol: str = Field(
        "USD", 
        description="Quote currency for market cap calculation (e.g., 'USD', 'EUR')"
    )

class FetchTopExchangesInput(BaseModel):
    """Input schema for fetching top exchanges for a trading pair."""
    from_symbol: str = Field(
        ..., 
        description="Base cryptocurrency symbol for the trading pair (e.g., 'BTC')"
    )
    to_symbol: str = Field(
        "USD", 
        description="Quote currency symbol for the trading pair. Defaults to 'USD'"
    )

class FetchTopVolumeInput(BaseModel):
    """Input schema for fetching top cryptocurrencies by trading volume."""
    limit: int = Field(
        10, 
        description="Number of top cryptocurrencies to return, ordered by trading volume"
    )
    to_symbol: str = Field(
        "USD", 
        description="Quote currency for volume calculation. Defaults to 'USD'"
    )


def fetch_price(from_symbol: str, to_symbols: List[str]) -> dict:
    """
    Fetch current price for a cryptocurrency in multiple currencies.
    
    Args:
        from_symbol: Base currency symbol (e.g., 'BTC')
        to_symbols: List of quote currency symbols (e.g., ['USD', 'EUR', 'JPY'])
    """
    url = f"{CRYPTO_COMPARE_BASE_URL}/data/price"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CRYPTO_COMPARE_API_KEY}"
    }
    params = {
        "fsym": from_symbol.upper(),
        "tsyms": ",".join(to_symbols)
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"
    return response.json()

def fetch_trading_signals(from_symbol: str) -> dict:
    """
    Fetch latest trading signals from IntoTheBlock.
    
    Args:
        from_symbol: Cryptocurrency symbol (e.g., 'BTC')
    """
    url = f"{CRYPTO_COMPARE_BASE_URL}/data/tradingsignals/intotheblock/latest"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CRYPTO_COMPARE_API_KEY}"
    }
    params = {
        "fsym": from_symbol.upper()
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"
    return response.json()

def fetch_top_market_cap(limit: int = 10, to_symbol: str = "USD") -> dict:
    """
    Fetch top cryptocurrencies by market cap.
    
    Args:
        limit: Number of results to return
        to_symbol: Quote currency symbol
    """
    url = f"{CRYPTO_COMPARE_BASE_URL}/data/top/mktcapfull"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CRYPTO_COMPARE_API_KEY}"
    }
    params = {
        "limit": limit,
        "tsym": to_symbol.upper()
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"
    return response.json()

def fetch_top_exchanges(from_symbol: str, to_symbol: str = "USD") -> dict:
    """
    Fetch top exchanges for a cryptocurrency pair.
    
    Args:
        from_symbol: Base currency symbol
        to_symbol: Quote currency symbol
    """
    url = f"{CRYPTO_COMPARE_BASE_URL}/data/top/exchanges"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CRYPTO_COMPARE_API_KEY}"
    }
    params = {
        "fsym": from_symbol.upper(),
        "tsym": to_symbol.upper()
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"
    return response.json()

def fetch_top_volume(limit: int = 10, to_symbol: str = "USD") -> dict:
    """
    Fetch top cryptocurrencies by total volume.
    
    Args:
        limit: Number of results to return
        to_symbol: Quote currency symbol
    """
    url = f"{CRYPTO_COMPARE_BASE_URL}/data/top/totalvolfull"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CRYPTO_COMPARE_API_KEY}"
    }
    params = {
        "limit": limit,
        "tsym": to_symbol.upper()
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"
    return response.json()


def fetch_news(token: str, timestamp: int = None):
    """Fetches news for a specific token and timestamp."""
    # Use current time if no timestamp provided
    if timestamp is None:
        timestamp = int(time.time())

    print(f"Fetching news for timestamp: {timestamp}")
    url = f"{CRYPTO_COMPARE_BASE_URL}/data/v2/news/?lang=EN&lTs={timestamp}&categories={token}&sign=true"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {CRYPTO_COMPARE_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"

    return response.json()


def fetch_news_tool(token: str, timestamp: int = None):
    """Fetch news articles for a token at a specific timestamp."""
    news_data = fetch_news(token, timestamp)
    return json.dumps(news_data, indent=2)


FETCH_NEWS_PROMPT = """
This tool fetches the latest cryptocurrency news articles for a specific token.
You can optionally specify a timestamp to get historical news, otherwise it uses the current time.
The news includes important updates, market analysis, and developments related to the specified token.
Returns articles in English with details like title, body, source, and publish time.
"""

FETCH_PRICE_PROMPT = """
This tool fetches real-time cryptocurrency price data with multi-currency support.
Provide a base currency (e.g., 'BTC', 'ETH') and a list of target currencies (e.g., ['USD', 'EUR', 'JPY']).
Returns current exchange rates for all requested currency pairs.
Example: fetch_price('BTC', ['USD', 'EUR']) returns prices like {"USD": 50000, "EUR": 42000}
"""

FETCH_TRADING_SIGNALS_PROMPT = """
This tool retrieves advanced trading signals from IntoTheBlock analytics for a specific cryptocurrency.
Provide a cryptocurrency symbol (e.g., 'BTC') to get detailed market indicators.
Returns key metrics like:
- Network growth and activity
- Large transaction patterns
- Holder composition and behavior
- Market momentum indicators
Useful for understanding current market sentiment and potential price movements.
"""

FETCH_TOP_MARKET_CAP_PROMPT = """
This tool retrieves the top cryptocurrencies ranked by market capitalization.
Customize results with:
- limit: Number of top cryptocurrencies to return (default 10)
- to_symbol: Currency for market cap calculation (default 'USD')
Returns detailed information including:
- Current price
- Market capitalization
- 24h volume
- Circulating supply
Perfect for market overview and tracking leading cryptocurrencies.
"""

FETCH_TOP_EXCHANGES_PROMPT = """
This tool fetches the top cryptocurrency exchanges for a specific trading pair.
Specify base and quote currencies (e.g., 'BTC'/'USD') to get exchange rankings.
Returns key information about each exchange including:
- 24h trading volume
- Market share percentage
- Price variations across exchanges
- Exchange reliability metrics
Useful for finding the best venues for trading specific crypto pairs.
"""

FETCH_TOP_VOLUME_PROMPT = """
This tool retrieves cryptocurrencies ranked by their total trading volume.
Customize the view with:
- limit: Number of results to show (default 10)
- to_symbol: Quote currency for volume calculation (default 'USD')
Returns comprehensive volume data including:
- 24h trading volume
- Volume distribution across exchanges
- Price movement correlation
Ideal for identifying most actively traded cryptocurrencies and market activity hotspots.
"""

