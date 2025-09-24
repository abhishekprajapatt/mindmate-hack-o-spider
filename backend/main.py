from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import logging

from nlp import SentimentAnalyzer
from llm_client import LLMClient
from safety import CrisisDetector, get_crisis_response
from db import ConversationLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MindMate API", description="Mental Health Support Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sentiment_analyzer = SentimentAnalyzer()
llm_client = LLMClient()
crisis_detector = CrisisDetector()
logger_db = ConversationLogger() if os.getenv("ENABLE_LOGGING", "").lower() == "true" else None

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"

class ChatResponse(BaseModel):
    response: str
    sentiment: dict
    crisis_detected: bool
    timestamp: str
    conversation_id: str
    resources: Optional[List[str]] = None

# In-memory conversation storage (for demo purposes)
conversations = {}

@app.on_startup
async def startup_event():
    """Initialize database and services"""
    if logger_db:
        await logger_db.initialize()
    logger.info("MindMate API started successfully")

@app.get("/")
async def root():
    return {"message": "MindMate Mental Health Support API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        timestamp = datetime.now().isoformat()
        conversation_id = request.conversation_id or f"conv_{timestamp}"
        
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        conversation_history = conversations[conversation_id]
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": request.message,
            "timestamp": timestamp
        })
        
        # Keep only last 6 messages (3 exchanges) to manage context
        if len(conversation_history) > 6:
            conversation_history = conversation_history[-6:]
            conversations[conversation_id] = conversation_history
        
        # Analyze sentiment
        sentiment = await sentiment_analyzer.analyze(request.message)
        
        # Check for crisis
        crisis_detected = crisis_detector.detect_crisis(request.message)
        
        if crisis_detected:
            # Return crisis response immediately
            response_text = get_crisis_response()
            resources = [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "Emergency Services: 911",
                "Find local mental health resources at SAMHSA.gov"
            ]
            
            # Log crisis event (anonymized)
            if logger_db:
                await logger_db.log_conversation(
                    conversation_id=conversation_id,
                    sentiment=sentiment,
                    crisis_detected=True,
                    severity="high"
                )
            
            return ChatResponse(
                response=response_text,
                sentiment=sentiment,
                crisis_detected=True,
                timestamp=timestamp,
                conversation_id=conversation_id,
                resources=resources
            )
        
        # Generate empathetic response using LLM
        recent_messages = conversation_history[-3:]  # Last 3 messages
        response_text = await llm_client.generate_response(
            current_message=request.message,
            conversation_history=recent_messages,
            sentiment=sentiment
        )
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant", 
            "content": response_text,
            "timestamp": timestamp
        })
        
        # Log conversation (anonymized)
        if logger_db:
            severity = "low"
            if sentiment.get("score", 0) < -0.5:
                severity = "medium"
            
            await logger_db.log_conversation(
                conversation_id=conversation_id,
                sentiment=sentiment,
                crisis_detected=False,
                severity=severity
            )
        
        resources = [
            "National Alliance on Mental Illness (NAMI): nami.org",
            "Mental Health America: mhanational.org",
            "Psychology Today therapist finder"
        ]
        
        return ChatResponse(
            response=response_text,
            sentiment=sentiment,
            crisis_detected=False,
            timestamp=timestamp,
            conversation_id=conversation_id,
            resources=resources
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history (for demo purposes)"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation_id,
        "history": conversations[conversation_id]
    }

@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("API_HOST", "0.0.0.0"), 
        port=int(os.getenv("API_PORT", "8000"))
    )