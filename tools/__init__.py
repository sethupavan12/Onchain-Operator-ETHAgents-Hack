from .token_tool import deploy_multi_token, DeployMultiTokenInput, DEPLOY_MULTITOKEN_PROMPT
from .browser_tool import when_no_api_search_like_human
from .dalle_nft_tool import create_dalle_nft_tool, DalleNftInput, DALLE_NFT_PROMPT
from .ipfs_upload_tool import create_pinata_upload_tool, UploadImageToPinataInput, UPLOAD_IMAGE_TO_PINATA_PROMPT 
from .create_erc721_metadata_tool import create_erc721_metadata, UploadERC721MetadataInput, UPLOAD_ERC721_METADATA_PROMPT
from .crypto_compare_tools import (
    fetch_news_tool, FetchNewsInput, FETCH_NEWS_PROMPT,
    fetch_price, FetchPriceInput, FETCH_PRICE_PROMPT,
    fetch_trading_signals, FetchTradingSignalsInput, FETCH_TRADING_SIGNALS_PROMPT,
    fetch_top_market_cap, FetchTopMarketCapInput, FETCH_TOP_MARKET_CAP_PROMPT,
    fetch_top_exchanges, FetchTopExchangesInput, FETCH_TOP_EXCHANGES_PROMPT,
    fetch_top_volume, FetchTopVolumeInput, FETCH_TOP_VOLUME_PROMPT,
)
from .moralis_tools import (
    # Core wallet functions
    fetch_wallet_history, WalletHistoryInput, WALLET_HISTORY_PROMPT,
    fetch_wallet_balance, WalletBalanceInput, WALLET_BALANCE_PROMPT,
    
    # NFT related functions
    fetch_nft_transfers, NFTTransfersInput, NFT_TRANSFERS_PROMPT,
    fetch_wallet_nft_trades, WalletNFTTradesInput, WALLET_NFT_TRADES_PROMPT,
    
    # Token related functions
    fetch_token_transfers, TokenTransfersInput, TOKEN_TRANSFERS_PROMPT,
    fetch_wallet_tokens, WalletTokensInput, WALLET_TOKENS_PROMPT,
    fetch_token_price, TokenPriceInput, TOKEN_PRICE_PROMPT,
    fetch_batch_token_prices, BatchTokenPriceInput, BATCH_TOKEN_PRICES_PROMPT,
    
    # DeFi related functions
    fetch_defi_positions, DeFiPositionsInput, DEFI_POSITIONS_PROMPT,
    
    # Trading data functions
    fetch_pair_ohlcv, PairOHLCVInput, PAIR_OHLCV_PROMPT,
)
from .the_graph_uniswap_base_tools import (
    fetch_large_swaps, GraphLargeSwapsInput, GRAPH_LARGE_SWAPS_PROMPT,
    fetch_new_high_tvl_pools, GraphNewHighTVLPoolsInput, GRAPH_NEW_HIGH_TVL_POOLS_PROMPT,
    fetch_high_fee_pools, GraphHighFeePoolsInput, GRAPH_HIGH_FEE_POOLS_PROMPT,
    fetch_undervalued_tokens, GraphUndervaluedTokensInput, GRAPH_UNDERVALUED_TOKENS_PROMPT,
    fetch_whale_accumulation, GraphWhaleAccumulationInput, GRAPH_WHALE_ACCUMULATION_PROMPT,
    fetch_swap_trends, GraphSwapTrendsInput, GRAPH_SWAP_TRENDS_PROMPT,
    fetch_gas_fees, GraphGasFeesInput, GRAPH_GAS_FEES_PROMPT,
    fetch_arbitrage_opportunities, GraphArbitrageInput, GRAPH_ARBITRAGE_PROMPT,
)
from .web2_access_tool import web_search_tool, WebSearchInput, WEB_SEARCH_PROMPT
from .dalle_nft_tool import (
    create_dalle_nft_tool,
    DalleNftInput,
    DALLE_NFT_PROMPT,
)

__all__ = [
    # Token tools
    'deploy_multi_token',
    'DeployMultiTokenInput',
    'DEPLOY_MULTITOKEN_PROMPT',
    
    # Browser tools
    'when_no_api_search_like_human',
    
    # DALLE tools
    'create_dalle_nft_tool', 'DalleNftInput', 'DALLE_NFT_PROMPT',
    
    # IPFS upload tools
    "create_pinata_upload_tool", "UploadImageToPinataInput", "UPLOAD_IMAGE_TO_PINATA_PROMPT" 
    
    # Web Search tools
    'web_search_tool',
    'WebSearchInput',
    'WEB_SEARCH_PROMPT',
    
    # Crypto Compare tools
    "fetch_news_tool", "FetchNewsInput", "FETCH_NEWS_PROMPT",
    "fetch_price", "FetchPriceInput", "FETCH_PRICE_PROMPT",
    "fetch_trading_signals", "FetchTradingSignalsInput", "FETCH_TRADING_SIGNALS_PROMPT",
    "fetch_top_market_cap", "FetchTopMarketCapInput", "FETCH_TOP_MARKET_CAP_PROMPT",
    "fetch_top_exchanges", "FetchTopExchangesInput", "FETCH_TOP_EXCHANGES_PROMPT",
    "fetch_top_volume", "FetchTopVolumeInput", "FETCH_TOP_VOLUME_PROMPT",

    # Moralis Core Wallet Tools
    "fetch_wallet_history", "WalletHistoryInput", "WALLET_HISTORY_PROMPT",
    "fetch_wallet_balance", "WalletBalanceInput", "WALLET_BALANCE_PROMPT",
    
    # Moralis NFT Tools
    "fetch_nft_transfers", "NFTTransfersInput", "NFT_TRANSFERS_PROMPT",
    "fetch_wallet_nft_trades", "WalletNFTTradesInput", "WALLET_NFT_TRADES_PROMPT",
    
    # Moralis Token Tools
    "fetch_token_transfers", "TokenTransfersInput", "TOKEN_TRANSFERS_PROMPT",
    "fetch_wallet_tokens", "WalletTokensInput", "WALLET_TOKENS_PROMPT",
    "fetch_token_price", "TokenPriceInput", "TOKEN_PRICE_PROMPT",
    "fetch_batch_token_prices", "BatchTokenPriceInput", "BATCH_TOKEN_PRICES_PROMPT",
    
    # Moralis DeFi Tools
    "fetch_defi_positions", "DeFiPositionsInput", "DEFI_POSITIONS_PROMPT",
    
    # Moralis Trading Data Tools
    "fetch_pair_ohlcv", "PairOHLCVInput", "PAIR_OHLCV_PROMPT",
    
    # Graph Protocol Tools
    "fetch_large_swaps", "GraphLargeSwapsInput", "GRAPH_LARGE_SWAPS_PROMPT",
    "fetch_new_high_tvl_pools", "GraphNewHighTVLPoolsInput", "GRAPH_NEW_HIGH_TVL_POOLS_PROMPT",
    "fetch_high_fee_pools", "GraphHighFeePoolsInput", "GRAPH_HIGH_FEE_POOLS_PROMPT",
    "fetch_undervalued_tokens", "GraphUndervaluedTokensInput", "GRAPH_UNDERVALUED_TOKENS_PROMPT",
    "fetch_whale_accumulation", "GraphWhaleAccumulationInput", "GRAPH_WHALE_ACCUMULATION_PROMPT",
    "fetch_swap_trends", "GraphSwapTrendsInput", "GRAPH_SWAP_TRENDS_PROMPT",
    "fetch_gas_fees", "GraphGasFeesInput", "GRAPH_GAS_FEES_PROMPT",
    "fetch_arbitrage_opportunities", "GraphArbitrageInput", "GRAPH_ARBITRAGE_PROMPT",
    "create_erc721_metadata", "UploadERC721MetadataInput", "UPLOAD_ERC721_METADATA_PROMPT" 
]
