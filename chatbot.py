from typing import List
import os
import sys
import time
import json
import requests
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.tools import CdpTool
from pydantic import BaseModel, Field
from cdp import Wallet
from dotenv import load_dotenv
# from browser_use import Agent
load_dotenv()
from langchain_core.tools import tool
import asyncio
from twitter_langchain import (TwitterApiWrapper, TwitterToolkit)


# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"






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
    url = f"{NEWS_CRYPTO_COMPARE_BASE_URL}/data/v2/news/?lang=EN&lTs={timestamp}&categories={token}&sign=true"
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

# @tool
# def when_no_api_search_like_human(message: str):
#     """
#     Finds information from the internet using a browser.
#     
#     Great for when you want to find something but there is no API.
#     """
#     async def async_tool_logic():
#         llm = ChatOpenAI(model="gpt-4o-mini")
#         browse_agent = Agent(
#             task=message,
#             llm=llm,
#         )
#         result = await browse_agent.run()
#         return result
#
#     # Run the async logic in a synchronous context
#     return asyncio.run(async_tool_logic())

DEPLOY_MULTITOKEN_PROMPT = """
This tool deploys a new multi-token contract with a specified base URI for token metadata.
The base URI should be a template URL containing {id} which will be replaced with the token ID.
For example: 'https://example.com/metadata/{id}.json'
"""


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



class DeployMultiTokenInput(BaseModel):
    """Input argument schema for deploy multi-token contract action."""
    base_uri: str = Field(
        ...,
        description=
        "The base URI template for token metadata. Must contain {id} placeholder.",
        example="https://example.com/metadata/{id}.json")


def deploy_multi_token(wallet: Wallet, base_uri: str) -> str:
    """Deploy a new multi-token contract with the specified base URI.

    Args:
        wallet (Wallet): The wallet to deploy the contract from.
        base_uri (str): The base URI template for token metadata. Must contain {id} placeholder.

    Returns:
        str: A message confirming deployment with the contract address.
    """
    # Validate that the base_uri contains the {id} placeholder
    if "{id}" not in base_uri:
        raise ValueError("base_uri must contain {id} placeholder")

    # Deploy the contract
    deployed_contract = wallet.deploy_multi_token(base_uri)
    result = deployed_contract.wait()

    return f"Successfully deployed multi-token contract at address: {result.contract_address}"


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    # Initialize LLM.
    llm = ChatOpenAI(model="gpt-4o-mini")

    wallet_data = None

    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    # Configure CDP Agentkit Langchain Extension.
    values = {}
    if wallet_data is not None:
        # If there is a persisted agentic wallet, load it and pass to the CDP Agentkit Wrapper.
        values = {"cdp_wallet_data": wallet_data}

    agentkit = CdpAgentkitWrapper(**values)

    # persist the agent's CDP MPC Wallet Data.
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get tools.
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()
    twitter_api_wrapper = TwitterApiWrapper()
    twitter_toolkit = TwitterToolkit.from_twitter_api_wrapper(
        twitter_api_wrapper)
    tools.extend(twitter_toolkit.get_tools())
    deployMultiTokenTool = CdpTool(
        name="deploy_multi_token",
        description=DEPLOY_MULTITOKEN_PROMPT,
        cdp_agentkit_wrapper=
        agentkit,  # this should be whatever the instantiation of CdpAgentkitWrapper is
        args_schema=DeployMultiTokenInput,
        func=deploy_multi_token,
    )

    fetchNewsTool = CdpTool(
        name="fetch_news",
        description=FETCH_NEWS_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=FetchNewsInput,
        func=fetch_news_tool,
    )

    fetchPriceTool = CdpTool(
        name="fetch_price",
        description=FETCH_PRICE_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=FetchPriceInput,
        func=fetch_price,
    )

    fetchTradingSignalsTool = CdpTool(
        name="fetch_trading_signals",
        description=FETCH_TRADING_SIGNALS_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=FetchTradingSignalsInput,
        func=fetch_trading_signals,
    )

    fetchTopMarketCapTool = CdpTool(
        name="fetch_top_market_cap",
        description=FETCH_TOP_MARKET_CAP_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=FetchTopMarketCapInput,
        func=fetch_top_market_cap,
    )

    fetchTopExchangesTool = CdpTool(
        name="fetch_top_exchanges",
        description=FETCH_TOP_EXCHANGES_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=FetchTopExchangesInput,
        func=fetch_top_exchanges,
    )

    fetchTopVolumeTool = CdpTool(
        name="fetch_top_volume",
        description=FETCH_TOP_VOLUME_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=FetchTopVolumeInput,
        func=fetch_top_volume,
    )
    # Add to tools list
    tools.append(deployMultiTokenTool)
    # tools.append(when_no_api_search_like_human)
    # tools.append(fetchNewsTool)
    tools.extend([
    fetchNewsTool,
    fetchPriceTool,
    fetchTradingSignalsTool,
    fetchTopMarketCapTool,
    fetchTopExchangesTool,
    fetchTopVolumeTool
])

    # Store buffered conversation history in memory.
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    prompt = "You are a helpful agent that can interact onchain using the Coinbase Developer Platform Agentkit. You are empowered to interact onchain using your tools."
    "If you ever need funds, you can request them from the faucet if you are on network ID `base-sepolia`. "
    "If not, you can provide your wallet details and request funds from the user. "
    "If someone asks you to do something you can't do with your currently available tools, say you don't have a tool to do that AND you must ask the user "
    "'I can hack my way into AGI and answer your question. Do you consent? (Yes/No)'"
    "and you must use the tool - when_no_api_search_like_human which takes the action you want to achieve and it has another agent who searches the internet for you"
    "you just need to pass in the string query you want to 'achieve' and it can be a multi-step process the agent can handle it. "
    "bear in mind this takes bit of time so be careful using this and use it when users asks you to do something you can't do with your currently available tools"
    "Be concise and helpful with your responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=prompt,
    ), config


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            # Provide instructions autonomously
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities. "
            )

            # Run agent in autonomous mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            # Wait before the next action
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Chat Mode
def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input(
            "\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()

    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
