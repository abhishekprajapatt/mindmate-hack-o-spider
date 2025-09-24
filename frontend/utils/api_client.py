import requests
import json
from typing import Dict, Any, Optional, List
import streamlit as st
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class MindMateAPIClient:
    """Client for communicating with MindMate backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MindMate-Frontend/1.0'
        })
        self._last_health_check = None
        self._health_status = None
    
    def health_check(self, use_cache: bool = True) -> Dict[str, Any]:
        """Check if the backend is healthy"""
        # Use cached result if recent (within 30 seconds)
        if (use_cache and self._last_health_check and 
            time.time() - self._last_health_check < 30 and
            self._health_status):
            return self._health_status
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            
            self._health_status = {
                "status": "healthy",
                "backend_connected": True,
                "data": response.json(),
                "response_time": response.elapsed.total_seconds()
            }
            self._last_health_check = time.time()
            return self._health_status
            
        except requests.exceptions.ConnectionError:
            self._health_status = {
                "status": "connection_error",
                "backend_connected": False,
                "error": "Cannot connect to backend server"
            }
        except requests.exceptions.Timeout:
            self._health_status = {
                "status": "timeout", 
                "backend_connected": False,
                "error": "Backend server timeout"
            }
        except Exception as e:
            self._health_status = {
                "status": "error",
                "backend_connected": False,
                "error": str(e)
            }
        
        self._last_health_check = time.time()
        return self._health_status
    
    def send_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Optional[Dict[str, Any]]:
        """Send a message to the chatbot"""
        if not message.strip():
            st.error("Please enter a message before sending.")
            return None
        
        start_time = time.time()
        
        try:
            payload = {
                "message": message.strip(),
                "user_id": user_id
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Add response time to result
            result["response_time"] = time.time() - start_time
            
            return result
            
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Please ensure the server is running on http://localhost:8000")
            return None
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. The server might be overloaded. Please try again.")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                st.error("⚠️ Invalid message format. Please check your input.")
            elif e.response.status_code == 500:
                st.error("🔧 Server error occurred. Please try again later.")
            else:
                st.error(f"❌ HTTP error: {e.response.status_code}")
            return None
        except json.JSONDecodeError:
            st.error("⚠️ Invalid response from server. Please try again.")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            logger.error(f"API call failed: {str(e)}")
            return None
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history"""
        try:
            response = self.session.get(
                f"{self.base_url}/conversations/{conversation_id}",
                timeout=10
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {str(e)}")
            return None
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history"""
        try:
            response = self.session.delete(
                f"{self.base_url}/conversations/{conversation_id}",
                timeout=10
            )
            
            if response.status_code == 404:
                # Conversation doesn't exist, consider it cleared
                return True
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear conversation {conversation_id}: {str(e)}")
            st.error("Failed to clear conversation on server")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and available endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get API info: {str(e)}")
            return {"error": str(e)}
    
    def validate_connection(self) -> bool:
        """Validate connection to backend"""
        health = self.health_check(use_cache=False)
        return health.get("backend_connected", False)
    
    def get_conversation_stats(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation statistics (if endpoint exists)"""
        try:
            response = self.session.get(
                f"{self.base_url}/conversations/{conversation_id}/stats",
                timeout=5
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get conversation stats: {str(e)}")
            return None
    
    def batch_send_messages(
        self, 
        messages: List[str], 
        conversation_id: Optional[str] = None
    ) -> List[Optional[Dict[str, Any]]]:
        """Send multiple messages in sequence"""
        results = []
        for message in messages:
            result = self.send_message(
                message=message,
                conversation_id=conversation_id
            )
            results.append(result)
            
            # Small delay between messages to avoid overwhelming the server
            if result:
                time.sleep(0.5)
        
        return results

# Global API client instance
@st.cache_resource
def get_api_client(base_url: str = "http://localhost:8000") -> MindMateAPIClient:
    """Get or create API client instance"""
    return MindMateAPIClient(base_url)

