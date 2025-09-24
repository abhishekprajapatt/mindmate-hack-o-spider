import os
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.google_client = None
        self.hf_pipeline = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize sentiment analysis services"""
        # Try Google Cloud first
        if os.getenv("GOOGLE_CLOUD_API_KEY"):
            try:
                from google.cloud import language_v1
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CLOUD_API_KEY")
                self.google_client = language_v1.LanguageServiceClient()
                logger.info("Google Cloud Natural Language API initialized")
            except Exception as e:
                logger.warning(f"Google Cloud NLP initialization failed: {e}")
        
        # Fallback to HuggingFace
        if not self.google_client:
            try:
                from transformers import pipeline
                self.hf_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True
                )
                logger.info("HuggingFace sentiment pipeline initialized")
            except Exception as e:
                logger.error(f"HuggingFace pipeline initialization failed: {e}")
                self.hf_pipeline = None
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the given text"""
        try:
            if self.google_client:
                return await self._analyze_with_google(text)
            elif self.hf_pipeline:
                return await self._analyze_with_huggingface(text)
            else:
                # Basic fallback
                return self._basic_sentiment(text)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._basic_sentiment(text)
    
    async def _analyze_with_google(self, text: str) -> Dict[str, Any]:
        """Analyze using Google Cloud Natural Language API"""
        try:
            from google.cloud import language_v1
            
            def _sync_analyze():
                document = language_v1.Document(
                    content=text,
                    type_=language_v1.Document.Type.PLAIN_TEXT
                )
                response = self.google_client.analyze_sentiment(
                    request={"document": document}
                )
                return response
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, _sync_analyze)
            
            sentiment = response.document_sentiment
            
            return {
                "provider": "google",
                "score": sentiment.score,  # -1.0 to 1.0
                "magnitude": sentiment.magnitude,  # 0.0 to inf
                "label": self._score_to_label(sentiment.score),
                "confidence": min(sentiment.magnitude, 1.0)
            }
        except Exception as e:
            logger.error(f"Google sentiment analysis failed: {e}")
            return await self._analyze_with_huggingface(text)
    
    async def _analyze_with_huggingface(self, text: str) -> Dict[str, Any]:
        """Analyze using HuggingFace transformers"""
        try:
            def _sync_analyze():
                results = self.hf_pipeline(text)
                return results[0]  # Get all scores
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, _sync_analyze)
            
            # Convert to consistent format
            positive_score = next((r["score"] for r in results if r["label"] == "POSITIVE"), 0.5)
            negative_score = next((r["score"] for r in results if r["label"] == "NEGATIVE"), 0.5)
            
            # Convert to -1 to 1 scale
            score = positive_score - negative_score
            confidence = max(positive_score, negative_score)
            
            return {
                "provider": "huggingface",
                "score": score,
                "magnitude": confidence,
                "label": self._score_to_label(score),
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"HuggingFace sentiment analysis failed: {e}")
            return self._basic_sentiment(text)
    
    def _basic_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic rule-based sentiment fallback"""
        positive_words = [
            "good", "great", "happy", "joy", "love", "wonderful", "amazing", 
            "excellent", "fantastic", "perfect", "awesome", "brilliant"
        ]
        negative_words = [
            "bad", "terrible", "sad", "angry", "hate", "awful", "horrible", 
            "depressed", "anxious", "worried", "scared", "lonely", "hopeless",
            "suicide", "kill", "die", "hurt", "pain"
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if negative_count > positive_count:
            score = -0.7
            label = "negative"
        elif positive_count > negative_count:
            score = 0.7
            label = "positive"
        else:
            score = 0.0
            label = "neutral"
        
        return {
            "provider": "basic",
            "score": score,
            "magnitude": abs(score),
            "label": label,
            "confidence": 0.6
        }
    
    def _score_to_label(self, score: float) -> str:
        """Convert numeric score to label"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"