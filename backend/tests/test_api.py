import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json

# Import the main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

class TestHealthEndpoints:
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "MindMate" in data["message"]
        assert data["status"] == "healthy"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestChatEndpoint:
    @patch('main.sentiment_analyzer')
    @patch('main.crisis_detector')
    @patch('main.llm_client')
    def test_normal_conversation(self, mock_llm, mock_crisis, mock_sentiment):
        """Test normal conversation flow"""
        # Mock sentiment analysis
        mock_sentiment.analyze = AsyncMock(return_value={
            "provider": "mock",
            "score": 0.3,
            "magnitude": 0.5,
            "label": "positive",
            "confidence": 0.8
        })
        
        # Mock crisis detection
        mock_crisis.detect_crisis.return_value = False
        
        # Mock LLM response
        mock_llm.generate_response = AsyncMock(return_value="I understand you're feeling positive today. That's wonderful! What's been going well for you?")
        
        response = client.post("/chat", json={
            "message": "I'm feeling good today",
            "conversation_id": "test123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["crisis_detected"] == False
        assert "positive" in data["sentiment"]["label"]
        assert len(data["response"]) > 0
        assert data["conversation_id"] == "test123"
    
    @patch('main.sentiment_analyzer')
    @patch('main.crisis_detector')
    def test_crisis_detection(self, mock_crisis, mock_sentiment):
        """Test crisis detection and response"""
        # Mock sentiment analysis
        mock_sentiment.analyze = AsyncMock(return_value={
            "provider": "mock",
            "score": -0.9,
            "magnitude": 0.9,
            "label": "negative",
            "confidence": 0.9
        })
        
        # Mock crisis detection - return True
        mock_crisis.detect_crisis.return_value = True
        
        response = client.post("/chat", json={
            "message": "I want to end my life",
            "conversation_id": "crisis_test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["crisis_detected"] == True
        assert "988" in data["response"]  # Should include crisis hotline
        assert data["resources"] is not None
        assert len(data["resources"]) > 0
    
    def test_missing_message(self):
        """Test request with missing message"""
        response = client.post("/chat", json={
            "conversation_id": "test123"
        })
        assert response.status_code == 422  # Validation error
    
    def test_empty_message(self):
        """Test request with empty message"""
        response = client.post("/chat", json={
            "message": "",
            "conversation_id": "test123"
        })
        # Should still process but might handle gracefully
        assert response.status_code in [200, 422]
    
    @patch('main.sentiment_analyzer')
    @patch('main.crisis_detector')
    @patch('main.llm_client')
    def test_long_conversation_history(self, mock_llm, mock_crisis, mock_sentiment):
        """Test conversation with long history"""
        # Mock responses
        mock_sentiment.analyze = AsyncMock(return_value={
            "provider": "mock", "score": 0.0, "label": "neutral", "confidence": 0.5
        })
        mock_crisis.detect_crisis.return_value = False
        mock_llm.generate_response = AsyncMock(return_value="I'm here to listen.")
        
        # Send multiple messages to build history
        conversation_id = "long_test"
        for i in range(10):
            response = client.post("/chat", json={
                "message": f"This is message {i}",
                "conversation_id": conversation_id
            })
            assert response.status_code == 200
        
        # Verify last response
        data = response.json()
        assert data["conversation_id"] == conversation_id

class TestConversationManagement:
    def test_get_nonexistent_conversation(self):
        """Test getting a conversation that doesn't exist"""
        response = client.get("/conversations/nonexistent")
        assert response.status_code == 404
    
    def test_conversation_lifecycle(self):
        """Test full conversation lifecycle"""
        conversation_id = "lifecycle_test"
        
        # Send a message to create conversation
        with patch('main.sentiment_analyzer'), \
             patch('main.crisis_detector'), \
             patch('main.llm_client'):
            
            # Mock the dependencies
            import main
            main.sentiment_analyzer.analyze = AsyncMock(return_value={
                "provider": "mock", "score": 0.0, "label": "neutral", "confidence": 0.5
            })
            main.crisis_detector.detect_crisis.return_value = False
            main.llm_client.generate_response = AsyncMock(return_value="Test response")
            
            response = client.post("/chat", json={
                "message": "Hello",
                "conversation_id": conversation_id
            })
            assert response.status_code == 200
        
        # Get conversation
        response = client.get(f"/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert len(data["history"]) >= 2  # User message + bot response
        
        # Clear conversation
        response = client.delete(f"/conversations/{conversation_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        response = client.get(f"/conversations/{conversation_id}")
        assert response.status_code == 404

class TestErrorHandling:
    @patch('main.sentiment_analyzer')
    def test_sentiment_analysis_failure(self, mock_sentiment):
        """Test handling of sentiment analysis failures"""
        # Make sentiment analysis raise an exception
        mock_sentiment.analyze = AsyncMock(side_effect=Exception("Sentiment API failed"))
        
        with patch('main.crisis_detector'), patch('main.llm_client'):
            response = client.post("/chat", json={
                "message": "Test message",
                "conversation_id": "error_test"
            })
            # Should still return 500 or handle gracefully
            assert response.status_code in [200, 500]
    
    @patch('main.llm_client')
    def test_llm_failure(self, mock_llm):
        """Test handling of LLM failures"""
        # Make LLM generation raise an exception
        mock_llm.generate_response = AsyncMock(side_effect=Exception("LLM API failed"))
        
        with patch('main.sentiment_analyzer'), patch('main.crisis_detector'):
            import main
            main.sentiment_analyzer.analyze = AsyncMock(return_value={
                "provider": "mock", "score": 0.0, "label": "neutral", "confidence": 0.5
            })
            main.crisis_detector.detect_crisis.return_value = False
            
            response = client.post("/chat", json={
                "message": "Test message",
                "conversation_id": "llm_error_test"
            })
            assert response.status_code in [200, 500]

# Test utilities for safety module
class TestSafetyModule:
    def test_crisis_detection_import(self):
        """Test that safety module imports correctly"""
        from safety import CrisisDetector, get_crisis_response
        
        detector = CrisisDetector()
        assert detector is not None
        
        crisis_response = get_crisis_response()
        assert "988" in crisis_response
        assert "911" in crisis_response

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])