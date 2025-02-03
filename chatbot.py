import os
import sys
import time
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.tools import CdpTool
from dotenv import load_dotenv
from twitter_langchain import TwitterApiWrapper, TwitterToolkit
load_dotenv()

# Import tools
from tools import (
    # create an ERC-20 token
    deploy_multi_token, DeployMultiTokenInput, DEPLOY_MULTITOKEN_PROMPT,

    # crypto compare
    fetch_news_tool, FetchNewsInput, FETCH_NEWS_PROMPT,
    fetch_price, FetchPriceInput, FETCH_PRICE_PROMPT,
    fetch_trading_signals, FetchTradingSignalsInput, FETCH_TRADING_SIGNALS_PROMPT,
    fetch_top_market_cap, FetchTopMarketCapInput, FETCH_TOP_MARKET_CAP_PROMPT,
    fetch_top_exchanges, FetchTopExchangesInput, FETCH_TOP_EXCHANGES_PROMPT,
    fetch_top_volume, FetchTopVolumeInput, FETCH_TOP_VOLUME_PROMPT,

    # Moralis
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

    # Browser search
    # when_no_api_search_like_human,
)

# Configure a file to persist the agent's CDP MPC Wallet Data.
wallet_data_file = "wallet_data.txt"

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

    # Persist the agent's CDP MPC Wallet Data.
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)

    # Initialize CDP Agentkit Toolkit and get tools.
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()
    twitter_api_wrapper = TwitterApiWrapper()
    twitter_toolkit = TwitterToolkit.from_twitter_api_wrapper(twitter_api_wrapper)
    tools.extend(twitter_toolkit.get_tools())

    # Create Token 
    deployMultiTokenTool = CdpTool(
        name="deploy_multi_token",
        description=DEPLOY_MULTITOKEN_PROMPT,
        cdp_agentkit_wrapper=agentkit,
        args_schema=DeployMultiTokenInput,
        func=deploy_multi_token,
    )

    # Crypto Compare
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

    # Moralis API Tools
    moralisTools = [
        CdpTool(
            name="wallet_history",
            description="Fetch transaction history for a wallet address",
            cdp_agentkit_wrapper=agentkit,
            args_schema=WalletHistoryInput,
            func=fetch_wallet_history,
        ),
        CdpTool(
            name="wallet_balance",
            description="Fetch balance for a wallet address",
            cdp_agentkit_wrapper=agentkit,
            args_schema=WalletBalanceInput,
            func=fetch_wallet_balance,
        ),
        CdpTool(
            name="nft_transfers",
            description="Fetch NFT transfers for an address",
            cdp_agentkit_wrapper=agentkit,
            args_schema=NFTTransfersInput,
            func=fetch_nft_transfers,
        ),
        CdpTool(
            name="token_transfers",
            description="Fetch token transfers for an address",
            cdp_agentkit_wrapper=agentkit,
            args_schema=TokenTransfersInput,
            func=fetch_token_transfers,
        ),
        CdpTool(
            name="wallet_nft_trades",
            description="Fetch NFT trades for a wallet",
            cdp_agentkit_wrapper=agentkit,
            args_schema=WalletNFTTradesInput,
            func=fetch_wallet_nft_trades,
        ),
        CdpTool(
            name="wallet_tokens",
            description="Fetch tokens owned by a wallet",
            cdp_agentkit_wrapper=agentkit,
            args_schema=WalletTokensInput,
            func=fetch_wallet_tokens,
        ),
        CdpTool(
            name="defi_positions",
            description="Fetch DeFi positions for a wallet",
            cdp_agentkit_wrapper=agentkit,
            args_schema=DeFiPositionsInput,
            func=fetch_defi_positions,
        ),
        CdpTool(
            name="token_price",
            description="Fetch price for a specific token",
            cdp_agentkit_wrapper=agentkit,
            args_schema=TokenPriceInput,
            func=fetch_token_price,
        ),
        CdpTool(
            name="batch_token_prices",
            description="Fetch prices for multiple tokens",
            cdp_agentkit_wrapper=agentkit,
            args_schema=BatchTokenPriceInput,
            func=fetch_batch_token_prices,
        ),
        CdpTool(
            name="pair_ohlcv",
            description="Fetch OHLCV data for a trading pair",
            cdp_agentkit_wrapper=agentkit,
            args_schema=PairOHLCVInput,
            func=fetch_pair_ohlcv,
        )
    ]

    # Add additional tools.
    tools.append(deployMultiTokenTool)

    tools.extend([
    fetchNewsTool,
    fetchPriceTool,
    fetchTradingSignalsTool,
    fetchTopMarketCapTool,
    fetchTopExchangesTool,
    fetchTopVolumeTool
    ])

    tools.extend(moralisTools)

    # tools.append(when_no_api_search_like_human)

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
