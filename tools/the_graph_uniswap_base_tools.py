from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import requests
import time
import math

from dotenv import load_dotenv
load_dotenv()

###############################################
# Helper Functions to Execute GraphQL Queries
###############################################

def execute_graph_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes a GraphQL query against the primary Uniswap V3 subgraph endpoint.
    
    The API key is read from the environment variable THE_GRAPH_API_KEY.
    """
    api_key = os.getenv("THE_GRAPH_API_KEY")
    if not api_key:
        raise Exception("Environment variable THE_GRAPH_API_KEY is not set.")
    
    # Primary DEX endpoint (Uniswap V3, for example)
    endpoint = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/43Hwfi3dJSoGpyas9VwNoDAv55yjgGrPpNSmbQZArzMG"
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(endpoint, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def execute_graph_query_custom(query: str, endpoint: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes a GraphQL query against a custom endpoint.
    
    Use this helper to query the secondary DEX subgraph.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(endpoint, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def compute_price(sqrt_price_str: str) -> Optional[float]:
    """
    Computes the implied price from a Uniswap V3 sqrtPriceX96 value.
    
    Assumes that the sqrtPrice is in Q64.96 format.
    Formula: price = (sqrtPrice / 2^96)^2
    """
    try:
        sqrt_price = float(sqrt_price_str)
        price = (sqrt_price / (2**96)) ** 2
        return price
    except Exception as e:
        print(f"Error computing price from sqrtPrice: {e}")
        return None


###############################################
# Base Input Class
###############################################

class GraphQueryBase(BaseModel):
    timestamp: int = Field(
        default_factory=lambda: int(time.time()),
        description="The Unix timestamp to be used in the query (defaults to the current time)"
    )
    variables: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional dictionary of variables to include in the query."
    )


###############################################
# 1. Detect Large Holders (Whales) Exiting
###############################################

class GraphLargeSwapsInput(GraphQueryBase):
    first: int = Field(100, description="Number of swaps to fetch")
    threshold: float = Field(100000.0, description="Minimum swap volume (USD) to consider as a large swap")
    
    def to_query(self) -> str:
        query = (
            f'query LargeSwaps {{\n'
            f'  swaps(\n'
            f'    first: {self.first}\n'
            f'    orderBy: amountUSD\n'
            f'    orderDirection: desc\n'
            f'    where: {{ amountUSD_gt: "{self.threshold}"  timestamp_gt: "{math.floor(time.time() - 86400)}"}}\n'
            f'  ) {{\n'
            f'    id\n'
            f'    amountUSD\n'
            f'    sender\n'
            f'    recipient\n'
            f'    pool {{\n'
            f'      id\n'
            f'      token0 {{ symbol }}\n'
            f'      token1 {{ symbol }}\n'
            f'    }}\n'
            f'    timestamp\n'
            f'  }}\n'
            f'}}'
        )
        print(query)
        return query

def fetch_large_swaps(**kwargs) -> Dict[str, Any]:
    input_data = GraphLargeSwapsInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 2. Opportunity Identification: New High TVL Pools
###############################################

class GraphNewHighTVLPoolsInput(GraphQueryBase):
    first: int = Field(5, description="Number of pool day datas to fetch")
    threshold: float = Field(1000000.0, description="Minimum TVL (USD) threshold for pools")
    
    def to_query(self) -> str:
        return (
            f'query NewHighTVLPools {{\n'
            f'  poolDayDatas(\n'
            f'    first: {self.first}\n'
            f'    orderBy: tvlUSD\n'
            f'    orderDirection: desc\n'
            f'    where: {{ tvlUSD_gt: "{self.threshold}" }}\n'
            f'  ) {{\n'
            f'    id\n'
            f'    pool {{ id token0 {{ symbol }} token1 {{ symbol }} }}\n'
            f'    tvlUSD\n'
            f'    volumeUSD\n'
            f'    date\n'
            f'  }}\n'
            f'}}'
        )

def fetch_new_high_tvl_pools(**kwargs) -> Dict[str, Any]:
    input_data = GraphNewHighTVLPoolsInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 3. Opportunity Identification: High Fee Pools
###############################################

class GraphHighFeePoolsInput(GraphQueryBase):
    first: int = Field(10, description="Number of pools to fetch")
    threshold: float = Field(5000.0, description="Minimum fee tier threshold")
    
    def to_query(self) -> str:
        query = (
            f'query HighFeePools {{\n'
            f'  pools(\n'
            f'    first: {self.first}\n'
            f'    orderBy: feeTier\n'
            f'    orderDirection: desc\n'
            f'    where: {{ feeTier_gt: {self.threshold} }}\n'
            f'  ) {{\n'
            f'    id\n'
            f'    token0 {{ symbol }}\n'
            f'    token1 {{ symbol }}\n'
            f'    totalValueLockedUSD\n'
            f'    volumeUSD\n'
            f'  }}\n'
            f'}}'
        )
        print(query)
        return query

def fetch_high_fee_pools(**kwargs) -> Dict[str, Any]:
    input_data = GraphHighFeePoolsInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 4. Identify Undervalued Tokens
###############################################

class GraphUndervaluedTokensInput(GraphQueryBase):
    first: int = Field(10, description="Number of tokens to fetch")
    threshold: float = Field(100000.0, description="Minimum total liquidity threshold")
    
    def to_query(self) -> str:
        return (
            f'query UndervaluedTokens {{\n'
            f'  tokens(\n'
            f'    first: {self.first}\n'
            f'    orderBy: derivedETH\n'
            f'    orderDirection: desc\n'
            f'    where: {{ derivedETH_gt: "{self.threshold}"  }}\n'
            f'  ) {{\n'
            f'    id\n'
            f'    symbol\n'
            f'    volumeUSD\n'
            f'    derivedETH\n'
            f'  }}\n'
            f'}}'
        )

def fetch_undervalued_tokens(**kwargs) -> Dict[str, Any]:
    input_data = GraphUndervaluedTokensInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 5. Detect Early Whale Accumulation
###############################################

class GraphWhaleAccumulationInput(GraphQueryBase):
    first: int = Field(10, description="Number of swaps to fetch")
    threshold: float = Field(250000.0, description="Minimum swap volume (USD) to consider for whale accumulation")
    
    def to_query(self) -> str:
        return (
            f'query WhaleAccumulation {{\n'
            f'  swaps(\n'
            f'    first: {self.first}\n'
            f'    orderBy: amountUSD\n'
            f'    orderDirection: desc\n'
            f'    where: {{ amountUSD_gt: "{self.threshold}" timestamp_gt: "{math.floor(time.time() - 186400)}"}}\n'
            f'  ) {{\n'
            f'    id\n'
            f'    amountUSD\n'
            f'    sender\n'
            f'    recipient\n'
            f'    timestamp\n'
            f'  }}\n'
            f'}}'
        )

def fetch_whale_accumulation(**kwargs) -> Dict[str, Any]:
    input_data = GraphWhaleAccumulationInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 6. Check Historical Swap Trends
###############################################

class GraphSwapTrendsInput(GraphQueryBase):
    first: int = Field(7, description="Number of token day data records to fetch")
    
    def to_query(self) -> str:
        return (
            f'query SwapTrends {{\n'
            f'  tokenDayDatas(\n'
            f'    first: {self.first}\n'
            f'    orderBy: date\n'
            f'    orderDirection: desc\n'
            f'  ) {{\n'
            f'    id\n'
            f'    token {{ symbol }}\n'
            f'    priceUSD\n'
            f'    volumeUSD\n'
            f'  }}\n'
            f'}}'
        )

def fetch_swap_trends(**kwargs) -> Dict[str, Any]:
    input_data = GraphSwapTrendsInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 7. Historical Gas Fee Insights
###############################################

class GraphGasFeesInput(GraphQueryBase):
    first: int = Field(10, description="Number of transactions to fetch")
    
    def to_query(self) -> str:
        return (
            f'query GasFees {{\n'
            f'  transactions(\n'
            f'    first: {self.first}\n'
            f'    orderBy: gasUsed\n'
            f'    orderDirection: desc\n'
            f'  ) {{\n'
            f'    id\n'
            f'    gasUsed\n'
            f'    gasPrice\n'
            f'    timestamp\n'
            f'  }}\n'
            f'}}'
        )

def fetch_gas_fees(**kwargs) -> Dict[str, Any]:
    input_data = GraphGasFeesInput(**kwargs)
    query = input_data.to_query()
    return execute_graph_query(query, input_data.variables)


###############################################
# 8. Arbitrage Opportunities
###############################################

class GraphArbitrageInput(GraphQueryBase):
    token0: str = Field(..., description="The symbol of the first token (e.g., 'ETH')")
    token1: str = Field(..., description="The symbol of the second token (e.g., 'DAI')")
    amount: Optional[float] = Field(1.0, description="The amount of token0 to simulate for arbitrage calculations")
    
    def to_query_uniswap(self) -> str:
        return (
            f'query ArbitragePoolData {{\n'
            f'  pools(where: {{ token0_: {{ symbol: "{self.token0}" }}, token1_: {{ symbol: "{self.token1}" }} }}) {{\n'
            f'    id\n'
            f'    token0 {{ symbol }}\n'
            f'    token1 {{ symbol }}\n'
            f'    sqrtPrice\n'
            f'    feeTier\n'
            f'    totalValueLockedUSD\n'
            f'    volumeUSD\n'
            f'  }}\n'
            f'}}'
        )

    def to_query_bunni(self) -> str:
        return (
            f'query ArbitragePoolData {{\n'
            f'  pools(where: {{ bunniToken: {{ symbol: "{self.token0}" }}, bunniToken: {{ symbol: "{self.token1}" }} }}) {{\n'
            f'    id\n'
            f'    currency0 {{ symbol }}\n'
            f'    currency1 {{ symbol }}\n'
            f'    sqrtPriceX96\n'
            f'    fee\n'
            f'    liquidity\n'
            f'    volumeUSD\n'
            f'  }}\n'
            f'}}'
        )

def fetch_arbitrage_opportunities(**kwargs) -> Dict[str, Any]:
    input_data = GraphArbitrageInput(**kwargs)
    query_uniswap = input_data.to_query_uniswap()
    query_bunni = input_data.to_query_bunni()

    api_key = os.getenv("THE_GRAPH_API_KEY")
    if not api_key:
        raise Exception("Environment variable THE_GRAPH_API_KEY is not set.")
    
    # Define the two endpoints:
    uniswap_endpoint = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/43Hwfi3dJSoGpyas9VwNoDAv55yjgGrPpNSmbQZArzMG"
    bunni_endpoint = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/3oawHiCt7L9wJTEY9DynwAEmoThy8bvRhuMZdaaAooqW"
    
    result_uniswap = execute_graph_query_custom(query_uniswap, uniswap_endpoint, input_data.variables)
    result_bunni = execute_graph_query_custom(query_bunni, bunni_endpoint, input_data.variables)
    print(result_uniswap)
    print(result_bunni)
    
    if not result_dex1 or "data" not in result_dex1:
        raise Exception(f"Error: No valid data returned from DEX 1. Response: {result_dex1}")
    if not result_dex2 or "data" not in result_dex2:
        raise Exception(f"Error: No valid data returned from DEX 2. Response: {result_dex2}")

    pools1 = result_dex1.get("data", {}).get("pools", [])
    pools2 = result_dex2.get("data", {}).get("pools", [])
    
    if not pools1 or not pools2:
        return {"error": "Pool data not found on one or both DEXs for the specified token pair."}
    
    # For simplicity, take the first pool result from each DEX.
    pool1 = pools1[0]
    pool2 = pools2[0]
    
    price1 = compute_price(pool1.get("sqrtPrice", "0"))
    price2 = compute_price(pool2.get("sqrtPrice", "0"))
    
    arbitrage_info = {}
    if price1 is not None and price2 is not None:
        price_diff = abs(price1 - price2)
        arbitrage_margin = (price_diff / min(price1, price2)) * 100 if min(price1, price2) > 0 else 0
        arbitrage_info = {
            "price_difference": price_diff,
            "arbitrage_margin_percent": arbitrage_margin,
            "price_on_dex1": price1,
            "price_on_dex2": price2,
        }
    
    return {
        "dex1_pool": pool1,
        "dex2_pool": pool2,
        "arbitrage": arbitrage_info,
    }

###############################################
# Prompts for LLM Agent Integration
###############################################

GRAPH_LARGE_SWAPS_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to detect large swap transactions that may indicate whale exits.
Threshold: It focuses on transactions with a sell volume of $100,000+ USD (configurable).
Use Case: Detect whales exiting a token or liquidity pool.
Presentation: The tool should present the top swap transactions including swap volume, sender, recipient, pool token symbols, and timestamp.
Example usage:
Input: {"first": 100, "threshold": 100000.0}
"""

GRAPH_NEW_HIGH_TVL_POOLS_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to identify emerging liquidity pools with rapidly growing Total Value Locked (TVL).
Threshold: It filters for pools with TVL above 1,000,000 USD and significant growth (e.g., TVL growth > 50% in 24h).
Use Case: Find newly booming liquidity pools.
Presentation: The tool should display the pool details including pool ID, token pair symbols, TVL, volume, and the corresponding date.
Example usage:
Input: {"first": 5, "threshold": 1000000.0}
"""

GRAPH_HIGH_FEE_POOLS_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to alert you to high-yield liquidity pool opportunities.
Threshold: It selects pools with fee tiers above 5000 (indicative of fee APY > 50% per year).
Use Case: Alert users about high-yield LP opportunities.
Presentation: The tool should present pool details including pool ID, token pair symbols, total value locked (USD), and trading volume.
Example usage:
Input: {"first": 10, "threshold": 5000.0}
"""

GRAPH_UNDERVALUED_TOKENS_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to identify potentially undervalued tokens.
Threshold: It filters tokens with total liquidity above 100,000 USD; tokens may be undervalued if the TVL-to-Market Cap ratio is low (e.g., < 0.5).
Use Case: Identify tokens that might be undervalued.
Presentation: The tool should display the token symbol, current price (USD), and total liquidity for further analysis.
Example usage:
Input: {"first": 10, "threshold": 100000.0}
"""

GRAPH_WHALE_ACCUMULATION_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to detect early whale accumulation.
Threshold: It flags transactions where a single wallet buys tokens with a value exceeding $250,000 USD in 24 hours.
Use Case: Detect whales accumulating tokens early.
Presentation: The tool should list transactions including sender, recipient, transaction value, and timestamp.
Example usage:
Input: {"first": 10, "threshold": 250000.0}
"""

GRAPH_SWAP_TRENDS_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to analyze historical swap trends over the last 7 days.
Threshold: It examines volume trends to help understand market sentiment shifts.
Use Case: Understand market sentiment shifts by analyzing daily swap data.
Presentation: The tool should present token day data with token symbols, daily price (USD), trading volume, and total liquidity.
Example usage:
Input: {"first": 7}
"""

GRAPH_GAS_FEES_PROMPT = """
This tool interacts with Uniswap V3 contracts on the Base network to provide historical gas fee insights.
Threshold: It focuses on transactions with the highest gas usage over the last 24 hours.
Use Case: Understand network cost dynamics and market sentiment shifts.
Presentation: The tool should display details such as gas used, gas price, and timestamp for the top transactions.
Example usage:
Input: {"first": 10}
"""

GRAPH_ARBITRAGE_PROMPT = """
This tool compares price data between two decentralized exchanges (DEXs) by querying their subgraphs (Uniswap) & (Airswap).
It fetches pool data for a given token pair from two DEX subgraphs and computes the implied price from the sqrtPrice.
Use Case: Identify arbitrage opportunities by comparing the prices between DEXs.
Presentation: The tool returns pool data from both DEXs along with the computed prices and the arbitrage margin (price difference percentage).
Example usage:
Input: {"token0": "ETH", "token1": "DAI", "amount": 1.0}
"""

