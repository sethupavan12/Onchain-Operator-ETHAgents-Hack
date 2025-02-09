import json
import os
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

class ConversationManager:
    def __init__(self, storage_file: str = "conversation_histories.json"):
        self.storage_file = storage_file
        self.histories: Dict[str, List[dict]] = self._load_histories()
    
    def _load_histories(self) -> Dict[str, List[dict]]:
        """Load conversation histories from file"""
        if not os.path.exists(self.storage_file):
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                # Load raw histories
                raw_histories = json.load(f)
                
                # Convert raw messages back to LangChain messages
                histories = {}
                for session_id, messages in raw_histories.items():
                    histories[session_id] = []
                    for msg in messages:
                        if msg['type'] == 'human':
                            histories[session_id].append(HumanMessage(content=msg['content']))
                        elif msg['type'] == 'ai':
                            histories[session_id].append(AIMessage(content=msg['content']))
                return histories
        except Exception as e:
            print(f"Error loading histories: {e}")
            return {}
    
    def _save_histories(self):
        """Save conversation histories to file"""
        try:
            # Convert LangChain messages to serializable format
            serializable_histories = {}
            for session_id, messages in self.histories.items():
                serializable_histories[session_id] = []
                for msg in messages:
                    msg_type = 'human' if isinstance(msg, HumanMessage) else 'ai'
                    serializable_histories[session_id].append({
                        'type': msg_type,
                        'content': msg.content
                    })
            
            with open(self.storage_file, 'w') as f:
                json.dump(serializable_histories, f, indent=2)
        except Exception as e:
            print(f"Error saving histories: {e}")
    
    def get_history(self, session_id: str, limit: int = 10) -> List[BaseMessage]:
        """Get conversation history for a session
        
        Args:
            session_id: The session ID
            limit: Number of most recent messages to return, defaults to 10
        """
        history = self.histories.get(session_id, [])
        return history[-limit:]
    
    def add_message(self, session_id: str, message: BaseMessage):
        """Add a message to a session's history"""
        if session_id not in self.histories:
            self.histories[session_id] = []
        self.histories[session_id].append(message)
        self._save_histories()
    
    def create_session(self, session_id: str):
        """Create a new session"""
        if session_id not in self.histories:
            self.histories[session_id] = []
            self._save_histories()
    
    def delete_session(self, session_id: str):
        """Delete a session's history"""
        if session_id in self.histories:
            del self.histories[session_id]
            self._save_histories()
