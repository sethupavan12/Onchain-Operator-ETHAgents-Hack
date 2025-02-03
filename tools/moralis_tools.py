from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import requests
import os
from datetime import datetime

class Chain(str, Enum):
    # Ethereum and variants
    eth = "eth"
    eth_hex = "0x1"
    
    # Polygon and variants
    polygon = "polygon"
    polygon_hex = "0x89"
    
    # BSC
    bsc = "bsc"
    bsc_hex = "0x38"
    
    # Avalanche
    avalanche = "avalanche"
    avalanche_hex = "0xa86a"
    
    # Fantom
    fantom = "fantom"
    fantom_hex = "0xfa"
    
    # Palm
    palm = "palm"
    palm_hex = "0x2a15c308d"
    
    # Cronos
    cronos = "cronos"
    cronos_hex = "0x19"
    
    # Arbitrum
    arbitrum = "arbitrum"
    arbitrum_hex = "0xa4b1"
    
    # Chiliz
    chiliz = "chiliz"
    chiliz_hex = "0x15b38"
    
    # Gnosis
    gnosis = "gnosis"
    gnosis_hex = "0x64"
    
    # Base
    base = "base"
    base_hex = "0x2105"
    
    # Optimism
    optimism = "optimism"
    optimism_hex = "0xa"
    
    # Linea
    linea = "linea"
    linea_hex = "0xe708"
    
    # Moonbeam
    moonbeam = "moonbeam"
    moonbeam_hex = "0x504"
    
    # Moonriver
    moonriver = "moonriver"
    moonriver_hex = "0x505"
    
    # Flow
    flow = "flow"
    flow_hex = "0x2eb"
    
    # Ronin
    ronin = "ronin"
    ronin_hex = "0x7e4"
    
    # Lisk
    lisk = "lisk"
    lisk_hex = "0x46f"
    
    # Pulse
    pulse = "pulse"
    pulse_hex = "0x171"

class OrderDirection(str, Enum):
    DESC = "DESC"
    ASC = "ASC"

# Base configuration
class MoralisConfig:
    BASE_URL = "https://deep-index.moralis.io/api/v2.2"
    API_KEY = os.getenv("MORALIS_API_KEY")
    
    @classmethod
    def get_headers(cls):
        return {
            "accept": "application/json",
            "X-API-Key": cls.API_KEY
        }

# Input Schemas
class WalletHistoryInput(BaseModel):
    address: str = Field(..., description="Wallet address to fetch history for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")
    order: OrderDirection = Field(default=OrderDirection.DESC, description="Sort order")

class WalletBalanceInput(BaseModel):
    address: str = Field(..., description="Wallet address to fetch balance for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")

class NFTTransfersInput(BaseModel):
    address: str = Field(..., description="Address to fetch NFT transfers for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")
    format: str = Field(default="decimal", description="Format of token IDs")

class TokenTransfersInput(BaseModel):
    address: str = Field(..., description="Address to fetch token transfers for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")
    order: OrderDirection = Field(default=OrderDirection.DESC, description="Sort order")

class WalletNFTTradesInput(BaseModel):
    address: str = Field(..., description="Wallet address to fetch NFT trades for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")

class WalletTokensInput(BaseModel):
    address: str = Field(..., description="Wallet address to fetch tokens for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")

class DeFiPositionsInput(BaseModel):
    address: str = Field(..., description="Wallet address to fetch DeFi positions for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")

class TokenPriceInput(BaseModel):
    token_address: str = Field(..., description="Token address to fetch price for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")
    include_percent_change: bool = Field(default=True, description="Include price change percentage")

class BatchTokenPriceInput(BaseModel):
    tokens: List[dict] = Field(..., description="List of token addresses and optional parameters")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")

class PairOHLCVInput(BaseModel):
    pair_address: str = Field(..., description="Pair address to fetch OHLCV data for")
    chain: Chain = Field(default=Chain.eth, description="Blockchain to query")
    timeframe: str = Field(default="1h", description="Timeframe for OHLCV data")
    currency: str = Field(default="usd", description="Currency for price data")
    from_date: str = Field(..., description="Start date for OHLCV data")
    to_date: str = Field(..., description="End date for OHLCV data")

# API Implementation
def make_request(endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET", json_data: Optional[Dict] = None) -> Dict:
    """Make a request to the Moralis API."""
    url = f"{MoralisConfig.BASE_URL}/{endpoint}"
    kwargs = {
        "headers": MoralisConfig.get_headers(),
        "params": params
    }
    if json_data:
        kwargs["json"] = json_data

    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json()

# Function implementations
def fetch_wallet_history(address: str, chain: str = "eth", order: str = "DESC") -> Dict:
    """Fetch wallet transaction history."""
    endpoint = f"wallets/{address}/history"
    params = {"chain": chain, "order": order}
    return make_request(endpoint, params)

def fetch_wallet_balance(address: str, chain: str = "eth") -> Dict:
    """Fetch wallet balance."""
    endpoint = f"{address}/balance"
    params = {"chain": chain}
    return make_request(endpoint, params)

def fetch_nft_transfers(address: str, chain: str = "eth", format: str = "decimal") -> Dict:
    """Fetch NFT transfers for an address."""
    endpoint = f"{address}/nft/transfers"
    params = {"chain": chain, "format": format}
    return make_request(endpoint, params)

def fetch_token_transfers(address: str, chain: str = "eth", order: str = "DESC") -> Dict:
    """Fetch token transfers for an address."""
    endpoint = f"{address}/erc20/transfers"
    params = {"chain": chain, "order": order}
    return make_request(endpoint, params)

def fetch_wallet_nft_trades(address: str, chain: str = "eth") -> Dict:
    """Fetch NFT trades for a wallet."""
    endpoint = f"wallets/{address}/nfts/trades"
    params = {"chain": chain}
    return make_request(endpoint, params)

def fetch_wallet_tokens(address: str, chain: str = "eth") -> Dict:
    """Fetch tokens owned by a wallet."""
    endpoint = f"wallets/{address}/tokens"
    params = {"chain": chain}
    return make_request(endpoint, params)

def fetch_defi_positions(address: str, chain: str = "eth") -> Dict:
    """Fetch DeFi positions for a wallet."""
    endpoint = f"wallets/{address}/defi/positions"
    params = {"chain": chain}
    return make_request(endpoint, params)

def fetch_token_price(token_address: str, chain: str = "eth", include_percent_change: bool = True) -> Dict:
    """Fetch price for a specific token."""
    endpoint = f"erc20/{token_address}/price"
    params = {
        "chain": chain,
        "include": "percent_change" if include_percent_change else None
    }
    return make_request(endpoint, params)

def fetch_batch_token_prices(tokens: List[dict], chain: str = "eth") -> Dict:
    """Fetch prices for multiple tokens."""
    endpoint = "erc20/prices"
    params = {"chain": chain}
    return make_request(endpoint, params=params, method="POST", json_data={"tokens": tokens})

def fetch_pair_ohlcv(
    pair_address: str,
    chain: str = "eth",
    timeframe: str = "1h",
    currency: str = "usd",
    from_date: str = None,
    to_date: str = None
) -> Dict:
    """Fetch OHLCV data for a trading pair."""
    endpoint = f"pairs/{pair_address}/ohlcv"
    params = {
        "chain": chain,
        "timeframe": timeframe,
        "currency": currency,
        "fromDate": from_date,
        "toDate": to_date
    }
    return make_request(endpoint, params)

# Additional Moralis API endpoints
def fetch_wallet_net_worth(address: str, exclude_spam: bool = True, exclude_unverified_contracts: bool = True) -> Dict:
    """Fetch wallet net worth."""
    endpoint = f"wallets/{address}/net-worth"
    params = {
        "exclude_spam": str(exclude_spam).lower(),
        "exclude_unverified_contracts": str(exclude_unverified_contracts).lower()
    }
    return make_request(endpoint, params)

def fetch_wallet_stats(address: str, chain: str = "eth") -> Dict:
    """Fetch wallet statistics."""
    endpoint = f"wallets/{address}/stats"
    params = {"chain": chain}
    return make_request(endpoint, params)

def resolve_ens_domain(domain: str) -> Dict:
    """Resolve ENS domain to address."""
    endpoint = f"resolve/ens/{domain}"
    return make_request(endpoint)

def resolve_address_to_domain(address: str) -> Dict:
    """Resolve address to ENS domain."""
    endpoint = f"resolve/{address}/reverse"
    return make_request(endpoint)


"""Moralis API Tool Prompts"""

WALLET_HISTORY_PROMPT = """
Use this tool to fetch transaction history for a given wallet address.

Parameters:
- address (required): The wallet address to fetch history for (e.g., "0x123...")
- chain (optional): The blockchain to query. Defaults to "eth". Options include: eth, polygon, bsc, etc.
- order (optional): Sort order for transactions. Use "DESC" (default) or "ASC"

Example usage: Fetch the latest transactions for a wallet on Ethereum
Input: {"address": "0x1234...", "chain": "eth", "order": "DESC"}
"""

WALLET_BALANCE_PROMPT = """
Use this tool to fetch the current balance of a wallet address.

Parameters:
- address (required): The wallet address to check (e.g., "0x123...")
- chain (optional): The blockchain to query. Defaults to "eth"

Example usage: Check ETH balance of a wallet
Input: {"address": "0x1234...", "chain": "eth"}
"""

NFT_TRANSFERS_PROMPT = """
Use this tool to fetch NFT transfer history for a given address.

Parameters:
- address (required): The address to check for NFT transfers
- chain (optional): The blockchain to query. Defaults to "eth"
- format (optional): Format for token IDs. Use "decimal" (default) or "hex"

Example usage: Get NFT transfers for an address on Polygon
Input: {"address": "0x1234...", "chain": "polygon", "format": "decimal"}
"""

TOKEN_TRANSFERS_PROMPT = """
Use this tool to fetch ERC20 token transfers for an address.

Parameters:
- address (required): The address to check for token transfers
- chain (optional): The blockchain to query. Defaults to "eth"
- order (optional): Sort order for transfers. Use "DESC" (default) or "ASC"

Example usage: Get token transfers on BSC
Input: {"address": "0x1234...", "chain": "bsc", "order": "DESC"}
"""

WALLET_NFT_TRADES_PROMPT = """
Use this tool to fetch NFT trading history for a wallet.

Parameters:
- address (required): The wallet address to check NFT trades for
- chain (optional): The blockchain to query. Defaults to "eth"

Example usage: Get NFT trading activity on Ethereum
Input: {"address": "0x1234...", "chain": "eth"}
"""

WALLET_TOKENS_PROMPT = """
Use this tool to fetch all tokens owned by a wallet.

Parameters:
- address (required): The wallet address to check token holdings for
- chain (optional): The blockchain to query. Defaults to "eth"

Example usage: List all tokens owned by a wallet on Polygon
Input: {"address": "0x1234...", "chain": "polygon"}
"""

DEFI_POSITIONS_PROMPT = """
Use this tool to fetch DeFi positions for a wallet address.

Parameters:
- address (required): The wallet address to check DeFi positions for
- chain (optional): The blockchain to query. Defaults to "eth"

Example usage: Get DeFi positions on Ethereum
Input: {"address": "0x1234...", "chain": "eth"}
"""

TOKEN_PRICE_PROMPT = """
Use this tool to fetch the current price of a specific token.

Parameters:
- token_address (required): The contract address of the token
- chain (optional): The blockchain to query. Defaults to "eth"
- include_percent_change (optional): Include 24h price change. Defaults to true

Example usage: Get USDT price on Ethereum
Input: {"token_address": "0xdac17f958d2ee523a2206206994597c13d831ec7", "chain": "eth"}
"""

BATCH_TOKEN_PRICES_PROMPT = """
Use this tool to fetch prices for multiple tokens in a single request.

Parameters:
- tokens (required): List of token addresses and optional parameters
- chain (optional): The blockchain to query. Defaults to "eth"

Example usage: Get prices for USDT and USDC
Input: {
    "tokens": [
        {"token_address": "0xdac17f958d2ee523a2206206994597c13d831ec7"},
        {"token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"}
    ],
    "chain": "eth"
}
"""

PAIR_OHLCV_PROMPT = """
Use this tool to fetch OHLCV (Open, High, Low, Close, Volume) data for a trading pair.

Parameters:
- pair_address (required): The address of the trading pair
- chain (optional): The blockchain to query. Defaults to "eth"
- timeframe (optional): Time interval for candles. Defaults to "1h"
- currency (optional): Price currency. Defaults to "usd"
- from_date (required): Start date for data (YYYY-MM-DD)
- to_date (required): End date for data (YYYY-MM-DD)

Example usage: Get hourly OHLCV data for a Uniswap pair
Input: {
    "pair_address": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
    "chain": "eth",
    "timeframe": "1h",
    "from_date": "2024-01-01",
    "to_date": "2024-01-02"
}
"""

WALLET_NET_WORTH_PROMPT = """
Use this tool to calculate the total net worth of a wallet across all holdings.

Parameters:
- address (required): The wallet address to calculate net worth for
- exclude_spam (optional): Exclude spam tokens. Defaults to true
- exclude_unverified_contracts (optional): Exclude unverified contracts. Defaults to true

Example usage: Calculate wallet net worth excluding spam tokens
Input: {
    "address": "0x1234...",
    "exclude_spam": true,
    "exclude_unverified_contracts": true
}
"""

WALLET_STATS_PROMPT = """
Use this tool to fetch statistical information about a wallet's activity.

Parameters:
- address (required): The wallet address to get stats for
- chain (optional): The blockchain to query. Defaults to "eth"

Example usage: Get wallet statistics on Ethereum
Input: {"address": "0x1234...", "chain": "eth"}
"""
