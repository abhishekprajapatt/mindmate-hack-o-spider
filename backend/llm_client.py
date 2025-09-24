import os
import asyncio
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an empathetic and non-judgmental mental-wellness assistant. Your goal is to provide emotional support and practical coping suggestions, NOT medical, diagnostic, or therapeutic advice. Always:

1. Validate the user's feelings.
2. Use short, calm sentences.
3. Offer 1–2 practical coping steps (breathing, grounding).
4. If user expresses self-harm, suicidal intent, or immediate danger, do NOT attempt to counsel. Instead:
   - Express concern and seriousness,
   - Provide clear, immediate instructions: contact local emergency services or a crisis hotline, and encourage contacting a trusted person,
   - Provide placeholders for local emergency numbers and recommend professional help.
5. Always end by asking a gentle follow-up question (e.g., 'Would you like some breathing exercises now?').
6. Never provide medical diagnoses, prescribe medication, or claim to be a medical professional.

Keep responses under 120 words and always be warm, understanding, and supportive."""

class LLMClient:
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients"""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                self.openai_client = openai.AsyncOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # Google Gemini
        if os.getenv("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
        
        # Anthropic Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                self.anthropic_client = anthropic.AsyncAnthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Anthropic initialization failed: {e}")
        
        if not any([self.openai_client, self.gemini_client, self.anthropic_client]):
            logger.error("No LLM clients initialized. Please provide at least one API key.")
    
    async def generate_response(
        self, 
        current_message: str, 
        conversation_history: List[Dict], 
        sentiment: Dict[str, Any]
    ) -> str:
        """Generate an empathetic response using available LLM"""
        try:
            # Build context
            context = self._build_context(current_message, conversation_history, sentiment)
            
            # Try clients in order of preference
            if self.openai_client:
                return await self._generate_with_openai(context)
            elif self.anthropic_client:
                return await self._generate_with_anthropic(context)
            elif self.gemini_client:
                return await self._generate_with_gemini(context)
            else:
                return self._fallback_response(sentiment)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_response(sentiment)
    
    def _build_context(
        self, 
        current_message: str, 
        conversation_history: List[Dict], 
        sentiment: Dict[str, Any]
    ) -> str:
        """Build context for the LLM"""
        context_parts = []
        
        # Add conversation history
        if conversation_history:
            context_parts.append("Recent conversation:")
            for msg in conversation_history[-4:]:  # Last 4 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                context_parts.append(f"{role}: {msg['content']}")
        
        # Add current message and sentiment
        context_parts.append(f"\nCurrent user message: {current_message}")
        context_parts.append(f"Detected sentiment: {sentiment.get('label', 'neutral')} (confidence: {sentiment.get('confidence', 0.5):.2f})")
        
        # Add specific guidance based on sentiment
        if sentiment.get('score', 0) < -0.3:
            context_parts.append("\nNote: User seems to be experiencing negative emotions. Provide extra validation and gentle coping suggestions.")
        
        context_parts.append("\nProvide a supportive, empathetic response following the system guidelines:")
        
        return "\n".join(context_parts)
    
    async def _generate_with_openai(self, context: str) -> str:
        """Generate response using OpenAI"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    async def _generate_with_anthropic(self, context: str) -> str:
        """Generate response using Anthropic Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": f"{SYSTEM_PROMPT}\n\n{context}"}
                ],
                temperature=0.7
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise
    
    async def _generate_with_gemini(self, context: str) -> str:
        """Generate response using Google Gemini"""
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{context}"
            
            def _sync_generate():
                response = self.gemini_client.generate_content(full_prompt)
                return response.text
            
            # Run in thread pool
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(None, _sync_generate)
            return response_text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    def _fallback_response(self, sentiment: Dict[str, Any]) -> str:
        """Provide a fallback response when LLMs are unavailable"""
        sentiment_label = sentiment.get('label', 'neutral')
        
        responses = {
            'negative': "I hear that you're going through a difficult time right now. Your feelings are completely valid. Sometimes when we're struggling, it can help to take slow, deep breaths - in for 4 counts, hold for 4, out for 4. Would you like to talk about what's making you feel this way?",
            
            'positive': "I'm glad to hear you're feeling positive! It's wonderful that you're taking time to check in with yourself. Maintaining good mental health habits, like the ones that brought you here, is really important. What's been going well for you lately?",
            
            'neutral': "Thank you for sharing with me. I'm here to listen and support you. Sometimes it helps to just talk through what's on your mind. Taking a moment to breathe deeply can also be grounding. What would be most helpful for you right now?"
        }
        
        return responses.get(sentiment_label, responses['neutral'])