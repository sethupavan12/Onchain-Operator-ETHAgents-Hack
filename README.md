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
2. Fill ENV
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
MORALIS_API_KEY=""
```

## API Documentation

The agent exposes a REST API that allows real-time interaction with streaming responses. The API is built using FastAPI and provides detailed information about the agent's actions and thought process.

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Chat with Agent
```http
POST /chat
```

**Request Body:**
```json
{
    "message": string,    // The message to send to the agent
    "stream": boolean     // Whether to stream the response (default: false)
}
```

**Response Format:**

For non-streaming requests (`stream: false`):
```json
{
    "response": string    // The agent's complete response
}
```

For streaming requests (`stream: true`), you'll receive a series of Server-Sent Events (SSE) with the following types:

1. Thinking State:
```json
{
    "type": "thinking",
    "content": "Processing your request...",
    "step": "start"
}
```

2. Tool Usage:
```json
{
    "type": "tool_usage",
    "content": string,        // Description of the tool being used
    "tool_type": string      // Type of tool: "external_api", "internal", or "unknown"
}
```

3. Response:
```json
{
    "type": "message",
    "content": string,        // The agent's response
    "step": "response"
}
```

4. Error (if any):
```json
{
    "type": "error",
    "content": string,        // Error message
    "step": "error"
}
```

#### 2. Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "agent_initialized": boolean,
    "config_loaded": boolean
}
```

### Example Usage

#### Non-streaming Request
```javascript
// Using fetch
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: "What are the current top cryptocurrency exchanges?",
        stream: false
    })
});
const data = await response.json();
console.log(data.response);
```

#### Streaming Request
```javascript
// Using EventSource
const sse = new EventSource('/chat');
const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: "What are the current top cryptocurrency exchanges?",
        stream: true
    })
});

// Handle the streaming response
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const messages = chunk.split('\n').filter(Boolean);
    
    for (const message of messages) {
        const data = JSON.parse(message);
        switch (data.type) {
            case 'thinking':
                console.log('Agent is thinking:', data.content);
                break;
            case 'tool_usage':
                console.log('Using tool:', data.content);
                break;
            case 'message':
                console.log('Agent response:', data.content);
                break;
            case 'error':
                console.error('Error:', data.content);
                break;
        }
    }
}
```

### Running the API Server

1. Install dependencies:
```bash
poetry install
```

2. Start the server:
```bash
poetry run uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## Browser Use
With pip:

pip install browser-use
install playwright:

playwright install

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
- RESTful API with streaming support

## Source
This template is based on the CDP Agentkit examples. For more information, visit:
https://github.com/coinbase/cdp-agentkit
