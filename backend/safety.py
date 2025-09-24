import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CrisisDetector:
    def __init__(self):
        # Crisis keywords and phrases
        self.crisis_patterns = [
            # Suicide ideation
            r'\b(?:kill\s+myself|suicide|end\s+my\s+life|take\s+my\s+life|want\s+to\s+die)\b',
            r'\b(?:suicidal|end\s+it\s+all|not\s+worth\s+living|better\s+off\s+dead)\b',
            
            # Self-harm
            r'\b(?:cut\s+myself|hurt\s+myself|self\s*harm|cutting|burning\s+myself)\b',
            r'\b(?:razor|blade|pills\s+to\s+die|overdose)\b',
            
            # Immediate danger
            r'\b(?:going\s+to\s+kill|planning\s+to\s+die|tonight\s+.*\s+die|ready\s+to\s+die)\b',
            r'\b(?:gun|rope|bridge|jump\s+off|pills\s+.*\s+die)\b',
            
            # Harm to others
            r'\b(?:kill\s+(?:someone|them|him|her)|hurt\s+(?:someone|people|others))\b',
            r'\b(?:planning\s+to\s+hurt|going\s+to\s+hurt|want\s+to\s+hurt\s+(?:someone|others))\b'
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.crisis_patterns]
        
        # Additional high-risk phrases
        self.high_risk_phrases = [
            "can't go on", "nothing to live for", "everyone would be better off without me",
            "final goodbye", "last time", "saying goodbye", "won't be here tomorrow"
        ]
    
    def detect_crisis(self, message: str) -> bool:
        """Detect if the message contains crisis indicators"""
        try:
            # Check compiled regex patterns
            for pattern in self.compiled_patterns:
                if pattern.search(message):
                    logger.warning(f"Crisis pattern detected in message")
                    return True
            
            # Check high-risk phrases
            message_lower = message.lower()
            for phrase in self.high_risk_phrases:
                if phrase in message_lower:
                    logger.warning(f"High-risk phrase detected: {phrase}")
                    return True
            
            # Additional contextual analysis
            if self._contextual_crisis_check(message_lower):
                logger.warning("Contextual crisis indicators detected")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Crisis detection failed: {e}")
            return False  # Fail safe - don't trigger false positives
    
    def _contextual_crisis_check(self, message: str) -> bool:
        """Additional contextual checks for crisis detection"""
        # Combinations that might indicate crisis
        crisis_combinations = [
            ["pain", "can't", "anymore"],
            ["tired", "fighting", "give up"],
            ["no one", "cares", "alone"],
            ["pointless", "life", "meaningless"]
        ]
        
        for combination in crisis_combinations:
            if all(word in message for word in combination):
                return True
        
        return False

def get_crisis_response() -> str:
    """Return the standardized crisis response"""
    return """I'm very concerned about what you've shared with me. Your safety is the most important thing right now.

Please reach out for immediate help:

🚨 **If you're in immediate danger, call emergency services (911) right away.**

📞 **Crisis Support:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- National Domestic Violence Hotline: 1-800-799-7233

👥 **Please contact a trusted person in your life right now** - a friend, family member, counselor, or healthcare provider.

You don't have to go through this alone. Professional counselors are trained to help and want to support you through this difficult time.

I care about your wellbeing, but I'm not equipped to provide the immediate professional help you need right now. Please reach out to one of these resources."""

def get_safety_disclaimer() -> str:
    """Return the safety disclaimer for the application"""
    return """**Important Safety Information:**

🤖 **This is an AI chatbot** designed to provide emotional support and wellness resources. It is NOT a replacement for professional mental health care, medical advice, or emergency services.

⚠️ **Limitations:**
- Cannot provide medical diagnoses or treatment recommendations
- Cannot prescribe medications or provide clinical therapy
- Cannot handle immediate crisis situations requiring urgent intervention

🆘 **In Case of Emergency:**
If you're experiencing thoughts of self-harm, suicide, or immediate danger, please contact:
- Emergency Services: 911
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741

💙 **Privacy:** Your conversations are handled with care. We log anonymized data for safety and improvement purposes only.

📞 **Professional Help:** We strongly encourage speaking with a licensed mental health professional for ongoing support and treatment."""

def validate_message_safety(message: str) -> Dict[str, Any]:
    """Comprehensive message safety validation"""
    detector = CrisisDetector()
    
    result = {
        "safe": True,
        "crisis_detected": False,
        "risk_level": "low",
        "concerns": []
    }
    
    # Crisis detection
    if detector.detect_crisis(message):
        result["safe"] = False
        result["crisis_detected"] = True
        result["risk_level"] = "high"
        result["concerns"].append("Crisis indicators detected")
    
    # Check message length (prevent spam/abuse)
    if len(message) > 2000:
        result["concerns"].append("Message too long")
    
    # Check for inappropriate content (basic)
    inappropriate_patterns = [
        r'\b(?:spam|advertisement|buy\s+now|click\s+here)\b',
        r'\b(?:hate|racist|discrimination)\b'
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            result["concerns"].append("Potentially inappropriate content")
            break
    
    return result