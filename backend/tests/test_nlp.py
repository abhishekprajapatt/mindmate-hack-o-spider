import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import SentimentAnalyzer

class TestSentimentAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    @pytest.mark.asyncio
    async def test_basic_sentiment_positive(self, analyzer):
        """Test basic sentiment analysis with positive text"""
        result = await analyzer.analyze("I am feeling great today!")
        
        assert result["label"] in ["positive", "neutral"]
        assert result["score"] >= -1.0 and result["score"] <= 1.0
        assert result["confidence"] >= 0.0 and result["confidence"] <= 1.0
        assert "provider" in result
    
    @pytest.mark.asyncio
    async def test_basic_sentiment_negative(self, analyzer):
        """Test basic sentiment analysis with negative text"""
        result = await analyzer.analyze("I am feeling terrible and sad.")
        
        assert result["label"] in ["negative", "neutral"]
        assert result["score"] >= -1.0 and result["score"] <= 1.0
        assert result["confidence"] >= 0.0 and result["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_empty_text(self, analyzer):
        """Test handling of empty text"""
        result = await analyzer.analyze("")
        
        assert result is not None
        assert "label" in result
        assert "score" in result
    
    @pytest.mark.asyncio
    async def test_very_long_text(self, analyzer):
        """Test handling of very long text"""
        long_text = "I am feeling anxious. " * 100
        result = await analyzer.analyze(long_text)
        
        assert result is not None
        assert result["label"] in ["positive", "negative", "neutral"]
    
    def test_score_to_label_conversion(self, analyzer):
        """Test score to label conversion"""
        assert analyzer._score_to_label(0.5) == "positive"
        assert analyzer._score_to_label(-0.5) == "negative"
        assert analyzer._score_to_label(0.05) == "neutral"
        assert analyzer._score_to_label(-0.05) == "neutral"
    
    @pytest.mark.asyncio
    async def test_fallback_sentiment(self, analyzer):
        """Test basic fallback sentiment analysis"""
        # Test with known positive words
        result = analyzer._basic_sentiment("I love this wonderful day!")
        assert result["label"] == "positive"
        assert result["score"] > 0
        
        # Test with known negative words
        result = analyzer._basic_sentiment("I hate this terrible awful day")
        assert result["label"] == "negative"
        assert result["score"] < 0
        
        # Test neutral
        result = analyzer._basic_sentiment("The weather is today.")
        assert result["label"] == "neutral"
        assert result["score"] == 0.0

    @pytest.mark.asyncio 
    async def test_crisis_related_sentiment(self, analyzer):
        """Test sentiment analysis on crisis-related text"""
        crisis_text = "I feel hopeless and want to end my pain"
        result = await analyzer.analyze(crisis_text)
        
        # Should detect negative sentiment
        assert result["score"] < 0
        assert result["label"] == "negative"