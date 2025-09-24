import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_client import LLMClient

class TestLLMClient:
    @pytest.fixture
    def llm_client(self):
        return LLMClient()
    
    def test_initialization(self, llm_client):
        """Test LLM client initialization"""
        assert llm_client is not None
        # At least one client should be available or fallback should work
    
    @pytest.mark.asyncio
    async def test_fallback_response(self, llm_client):
        """Test fallback responses when LLMs are unavailable"""
        sentiment_data = {"label": "negative", "score": -0.7, "confidence": 0.8}
        response = llm_client._fallback_response(sentiment_data)
        
        assert len(response) > 0
        assert isinstance(response, str)
        assert len(response.split()) > 10  # Should be substantial
    
    def test_context_building(self, llm_client):
        """Test context building for LLM prompts"""
        conversation_history = [
            {"role": "user", "content": "I'm feeling sad"},
            {"role": "assistant", "content": "I understand you're feeling sad"}
        ]
        sentiment = {"label": "negative", "score": -0.5, "confidence": 0.7}
        
        context = llm_client._build_context(
            current_message="I need help",
            conversation_history=conversation_history,
            sentiment=sentiment
        )
        
        assert "I need help" in context
        assert "negative" in context
        assert "conversation:" in context.lower()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {}, clear=True)
    async def test_no_api_keys(self):
        """Test behavior when no API keys are provided"""
        llm_client = LLMClient()
        
        sentiment = {"label": "neutral", "score": 0.0, "confidence": 0.5}
        response = await llm_client.generate_response(
            current_message="Hello",
            conversation_history=[],
            sentiment=sentiment
        )
        
        # Should return fallback response
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_fallback_responses_variety(self, llm_client):
        """Test that fallback responses vary by sentiment"""
        sentiments = [
            {"label": "positive", "score": 0.7},
            {"label": "negative", "score": -0.7},
            {"label": "neutral", "score": 0.0}
        ]
        
        responses = []
        for sentiment in sentiments:
            response = llm_client._fallback_response(sentiment)
            responses.append(response)
        
        # Responses should be different for different sentiments
        assert len(set(responses)) == 3, "Fallback responses should vary by sentiment"
        
        # All responses should contain supportive language
        for response in responses:
            assert any(word in response.lower() for word in ['help', 'support', 'here', 'listen'])

class TestSystemPrompt:
    def test_system_prompt_requirements(self):
        """Test that system prompt meets requirements"""
        from llm_client import SYSTEM_PROMPT
        
        # Should contain key safety requirements
        assert "empathetic" in SYSTEM_PROMPT.lower()
        assert "non-judgmental" in SYSTEM_PROMPT.lower()
        assert "medical" in SYSTEM_PROMPT.lower()
        assert "diagnostic" in SYSTEM_PROMPT.lower()
        assert "validate" in SYSTEM_PROMPT.lower()
        assert "breathing" in SYSTEM_PROMPT.lower()
        assert "emergency" in SYSTEM_PROMPT.lower()
        assert "911" in SYSTEM_PROMPT or "crisis" in SYSTEM_PROMPT.lower()
        
        # Should have word limit
        assert "120" in SYSTEM_PROMPT or "word" in SYSTEM_PROMPT.lower()