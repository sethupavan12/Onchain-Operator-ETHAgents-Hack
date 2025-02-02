# Cryptopia Multi-Agent Source Code

A Replit template for running an AI agent with onchain capabilities and X posting using the [Coinbase Developer Platform (CDP) Agentkit](https://github.com/coinbase/cdp-agentkit/).

Supports CDP Agentkit actions + our own actions, allowing it to perform blockchain operations like:
- Deploying tokens (ERC-20 & NFTs)
- Managing wallets
- Executing transactions
- Interacting with smart contracts
- Posting on X
- Finding news about a specific token
- Browsing like a human about a specific thing if there's no API

## Prerequisites

1. **API Keys**
   - OpenAI API key from the [OpenAI Portal](https://platform.openai.com/api-keys)
   - CDP API credentials from [CDP Portal](https://portal.cdp.coinbase.com/access/api)
   - X Social API (Account Key and secret, Access Key and Secret)
   - Crypto compare API key CRYPTO_COMPARE_API_KEY

Fill this
```
OPENAI_API_KEY=""
CDP_API_KEY_PRIVATE_KEY=""
CDP_API_KEY_NAME=""
TWITTER_API_KEY=""
TWITTER_API_SECRET=""
TWITTER_ACCESS_TOKEN=""
TWITTER_ACCESS_TOKEN_SECRET=""
NETWORK_ID="base-sepolia"
TWITTER_BEARER_TOKEN="fake"
CRYPTO_COMPARE_API_KEY=""
```
## Quick Start

1. **Configure Secrets and CDP API Keys**
   Navigate to Tools > Secrets and add the secrets above.

2. **Run the Bot**
- Click the Run button
- Choose between chat mode or autonomous mode
- Start interacting onchain!

## Securing your Wallets

Every agent comes with an associated wallet. Wallet data is read from wallet_data.txt, and if that file does not exist, we will create a new wallet and persist it in a new file. Please note that this contains sensitive data and should not be used in production environments. Refer to the [CDP docs](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets#securing-a-wallet) for information on how to secure your wallets.

## Features
- Interactive chat mode for guided interactions
- Autonomous mode for self-directed blockchain operations
- Full CDP Agentkit integration
- Persistent wallet management

## Source
This template is based on the CDP Agentkit examples. For more information, visit:
https://github.com/coinbase/cdp-agentkit
