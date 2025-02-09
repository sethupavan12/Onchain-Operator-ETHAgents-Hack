from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Iterator, Tuple, Dict, List
import asyncio
from contextlib import asynccontextmanager
import json
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import os

# Import agent-related functions
from chatbot import initialize_agent
from conversation_manager import ConversationManager

# Global variables for agent and config
agent_instance = None
agent_config = None
conversation_manager = None
conversation_histories: Dict[str, List[dict]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the agent and conversation manager on startup
    global agent_instance, agent_config, conversation_manager
    print("Initializing agent...")
    agent_instance, agent_config = initialize_agent()
    conversation_manager = ConversationManager()
    yield
    # Cleanup on shutdown
    agent_instance = None
    agent_config = None
    conversation_manager = None

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Agent API",
    description="API to interact with the AI agent",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    session_id: Optional[str] = None

def get_run_config():
    """Get configuration for a new run with required checkpointer keys"""
    return {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "checkpoint_id": str(uuid.uuid4()),
            "checkpoint_ns": "chat_session"
        }
    }

def get_tool_description(chunk):
    """Extract a user-friendly description of what tool is being used"""
    if "tools" in chunk:
        try:
            # Get the raw tool message
            tool_message = chunk["tools"]["messages"][0].content
            
            # Try to parse it as JSON first
            try:
                tool_data = json.loads(tool_message)
                # If it's a tool response, extract relevant info
                if isinstance(tool_data, dict) and "Response" in tool_data:
                    return {
                        "type": "tool_usage",
                        "content": "Processing response from external data source...",
                        "tool_type": "external_api"
                    }
            except json.JSONDecodeError:
                pass
            
            # If it's not JSON, it might be a direct tool invocation message
            # Extract the tool name and args if available
            if "I will use the" in tool_message:
                parts = tool_message.split("I will use the")
                if len(parts) > 1:
                    tool_desc = parts[1].strip().split(" tool")[0]
                    return {
                        "type": "tool_usage",
                        "content": f"Using {tool_desc} to process your request...",
                        "tool_type": "internal"
                    }
            
            # If we can't parse it in a specific way, return the raw message
            return {
                "type": "tool_usage",
                "content": tool_message,
                "tool_type": "unknown"
            }
        except Exception as e:
            return {
                "type": "tool_usage",
                "content": "Using an agent tool to process your request...",
                "tool_type": "unknown"
            }
    return None

async def stream_response(message: str, session_id: str) -> Iterator[str]:
    """Stream the agent's response"""
    try:
        run_config = get_run_config()
        current_response = []
        
        # Add user message to history
        user_message = HumanMessage(content=message)
        conversation_manager.add_message(session_id, user_message)
        
        # Get full conversation history
        history = conversation_manager.get_history(session_id)

        # Send session ID first
        yield json.dumps({
            "type": "session",
            "content": "Session started",
            "session_id": session_id
        }) + "\n"
        
        for chunk in agent_instance.stream(
            {"messages": history},
            run_config
        ):
            if "agent" in chunk and chunk["agent"]["messages"][0].content:
                content = chunk["agent"]["messages"][0].content
                current_response.append(content)
                yield json.dumps({
                    "type": "message",
                    "content": content,
                    "session_id": session_id
                }) + "\n"
            elif "tools" in chunk:
                tool_desc = get_tool_description(chunk)
                if tool_desc:
                    yield json.dumps({
                        "type": "tool",
                        "content": tool_desc["content"],
                        "session_id": session_id
                    }) + "\n"
        
        # Add agent's response to history
        if current_response:
            ai_message = AIMessage(content=" ".join(current_response))
            conversation_manager.add_message(session_id, ai_message)
        
        # Send completion message
        yield json.dumps({
            "type": "complete",
            "content": "Task completed",
            "session_id": session_id
        }) + "\n"
        
    except Exception as e:
        yield json.dumps({
            "type": "error",
            "content": str(e),
            "session_id": session_id
        }) + "\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with the agent
    
    If stream=True, returns a streaming response
    If stream=False, returns a regular JSON response
    """
    if agent_instance is None or conversation_manager is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Create or get session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        if request.stream:
            return StreamingResponse(
                stream_response(request.message, session_id),
                media_type='text/event-stream'
            )
        else:
            # Add user message to history
            user_message = HumanMessage(content=request.message)
            conversation_manager.add_message(session_id, user_message)
            
            response = []
            run_config = get_run_config()
            for chunk in agent_instance.stream(
                {"messages": conversation_manager.get_history(session_id)},
                run_config
            ):
                if "agent" in chunk and chunk["agent"]["messages"][0].content:
                    response.append(chunk["agent"]["messages"][0].content)
            
            # Add agent's response to history
            if response:
                ai_message = AIMessage(content=" ".join(response))
                conversation_manager.add_message(session_id, ai_message)
            
            return {"response": " ".join(response)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallet/public_address")
async def get_wallet_public_address():
    """
    Read the wallets_data.txt file and return the default_address_id.
    """
    file_path = "./wallet_data.txt"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Wallet file not found")
    
    try:
        # Read the file content (assuming it contains a single JSON object)
        with open(file_path, "r") as f:
            content = f.read().strip()
        
        wallet_data = json.loads(content)
        default_address = wallet_data.get("default_address_id")
        
        if not default_address:
            raise HTTPException(
                status_code=404,
                detail="default_address_id not found in wallet data"
            )
        
        return {"public_address": default_address}
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Error parsing wallet data file. Please ensure it is valid JSON."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check if the API and agent are healthy"""
    return {
        "status": "healthy",
        "agent_initialized": agent_instance is not None,
        "config_loaded": agent_config is not None
    }
