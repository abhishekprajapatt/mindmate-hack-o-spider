import streamlit as st
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
import time

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    except Exception:
        return timestamp_str

def format_sentiment_score(score: float) -> Tuple[str, str]:
    """Format sentiment score for display"""
    if score > 0.1:
        return "😊 Positive", "#4CAF50"
    elif score < -0.1:
        return "😔 Negative", "#f44336"
    else:
        return "😐 Neutral", "#757575"

def get_sentiment_emoji(sentiment_label: str) -> str:
    """Get emoji for sentiment"""
    sentiment_emojis = {
        'positive': '😊',
        'negative': '😔',
        'neutral': '😐',
        'very_positive': '😄',
        'very_negative': '😢'
    }
    return sentiment_emojis.get(sentiment_label.lower(), '😐')

def clean_message(message: str) -> str:
    """Clean and sanitize user message"""
    # Remove excessive whitespace
    message = re.sub(r'\s+', ' ', message.strip())
    
    # Remove potentially harmful content (basic)
    message = re.sub(r'<script.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
    message = re.sub(r'<.*?>', '', message)  # Remove HTML tags
    
    return message

def generate_conversation_id() -> str:
    """Generate a unique conversation ID"""
    timestamp = str(int(time.time() * 1000))
    random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"conv_{timestamp}_{random_part}"

def validate_message(message: str) -> Tuple[bool, Optional[str]]:
    """Validate user message"""
    if not message or not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) > 2000:
        return False, "Message is too long (max 2000 characters)"
    
    if len(message.strip()) < 2:
        return False, "Message is too short"
    
    # Check for spam patterns
    spam_patterns = [
        r'(.)\1{10,}',  # Repeated characters
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return False, "Message contains inappropriate content"
    
    return True, None

def format_response_time(response_time: float) -> str:
    """Format response time for display"""
    if response_time < 1:
        return f"{response_time * 1000:.0f}ms"
    else:
        return f"{response_time:.1f}s"

def get_crisis_keywords() -> List[str]:
    """Get list of crisis keywords for client-side awareness"""
    return [
        "suicide", "kill myself", "end my life", "want to die",
        "hurt myself", "cut myself", "self harm", "overdose",
        "not worth living", "better off dead", "end it all"
    ]

def contains_crisis_keywords(message: str) -> bool:
    """Check if message contains crisis keywords (client-side check)"""
    message_lower = message.lower()
    crisis_keywords = get_crisis_keywords()
    
    return any(keyword in message_lower for keyword in crisis_keywords)

def format_message_for_display(message: str) -> str:
    """Format message for better display"""
    # Convert newlines to HTML breaks
    message = message.replace('\n', '<br>')
    
    # Make URLs clickable
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    message = re.sub(url_pattern, r'<a href="\g<0>" target="_blank">\g<0></a>', message)
    
    return message

def get_conversation_summary(conversation_history: List[Dict]) -> Dict[str, Any]:
    """Generate conversation summary statistics"""
    if not conversation_history:
        return {
            "message_count": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "avg_sentiment": 0.0,
            "crisis_detected": False,
            "duration": "0 minutes"
        }
    
    user_messages = [msg for msg in conversation_history if msg.get("is_user", False)]
    assistant_messages = [msg for msg in conversation_history if not msg.get("is_user", False)]
    
    # Calculate average sentiment from assistant messages
    sentiments = []
    crisis_detected = False
    
    for msg in assistant_messages:
        if msg.get("sentiment"):
            sentiments.append(msg["sentiment"].get("score", 0))
        if msg.get("crisis_detected", False):
            crisis_detected = True
    
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    # Calculate duration
    if len(conversation_history) >= 2:
        try:
            first_time = datetime.fromisoformat(conversation_history[0].get("timestamp", ""))
            last_time = datetime.fromisoformat(conversation_history[-1].get("timestamp", ""))
            duration_minutes = (last_time - first_time).seconds // 60
            duration = f"{duration_minutes} minutes" if duration_minutes > 0 else "Less than a minute"
        except:
            duration = "Unknown"
    else:
        duration = "Just started"
    
    return {
        "message_count": len(conversation_history),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "avg_sentiment": avg_sentiment,
        "crisis_detected": crisis_detected,
        "duration": duration
    }

def get_wellbeing_tip() -> str:
    """Get a random wellbeing tip"""
    tips = [
        "🧘 Take 5 deep breaths: In for 4, hold for 4, out for 6",
        "🚶 Go for a short walk, even just around the block",
        "💧 Drink a glass of water and notice how it tastes",
        "📱 Reach out to one person you care about",
        "✍️ Write down three things you're grateful for",
        "🌱 Spend a few minutes in nature or looking at plants",
        "🎵 Listen to a song that makes you feel peaceful",
        "🛁 Take a warm shower or bath mindfully",
        "📚 Read something inspiring for 10 minutes",
        "😊 Practice smiling - it can actually improve mood",
        "🧘‍♀️ Try the 5-4-3-2-1 grounding technique",
        "☕ Make a cup of tea and savor it slowly",
        "🎨 Do something creative for 15 minutes",
        "📞 Call someone who makes you laugh",
        "🌅 Watch the sunrise or sunset mindfully"
    ]
    
    import random
    return random.choice(tips)

def create_status_indicator(status: str) -> str:
    """Create HTML status indicator"""
    status_colors = {
        "healthy": "#4CAF50",
        "warning": "#FF9800", 
        "error": "#f44336",
        "offline": "#757575"
    }
    
    status_icons = {
        "healthy": "✅",
        "warning": "⚠️",
        "error": "❌", 
        "offline": "⚪"
    }
    
    color = status_colors.get(status, "#757575")
    icon = status_icons.get(status, "⚪")
    
    return f"""
    <div style="display: inline-flex; align-items: center; gap: 5px;">
        <span style="color: {color};">{icon}</span>
        <span style="color: {color}; font-weight: 600;">{status.title()}</span>
    </div>
    """

def save_conversation_locally(conversation_history: List[Dict], conversation_id: str):
    """Save conversation to browser local storage (if supported)"""
    try:
        conversation_data = {
            "id": conversation_id,
            "history": conversation_history,
            "timestamp": datetime.now().isoformat(),
            "summary": get_conversation_summary(conversation_history)
        }
        
        # This would require JavaScript integration in Streamlit
        # For now, we'll store in session state
        if "saved_conversations" not in st.session_state:
            st.session_state.saved_conversations = {}
        
        st.session_state.saved_conversations[conversation_id] = conversation_data
        
    except Exception as e:
        logger.error(f"Failed to save conversation locally: {str(e)}")

def load_conversation_locally(conversation_id: str) -> Optional[Dict]:
    """Load conversation from local storage"""
    try:
        saved_conversations = st.session_state.get("saved_conversations", {})
        return saved_conversations.get(conversation_id)
    except Exception as e:
        logger.error(f"Failed to load conversation locally: {str(e)}")
        return None

def export_conversation_json(conversation_history: List[Dict], conversation_id: str) -> str:
    """Export conversation as JSON string"""
    export_data = {
        "conversation_id": conversation_id,
        "exported_at": datetime.now().isoformat(),
        "summary": get_conversation_summary(conversation_history),
        "messages": conversation_history
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def get_quick_responses() -> List[Tuple[str, str]]:
    """Get list of quick response options"""
    return [
        ("😰 Feeling Anxious", "I'm feeling really anxious right now and could use some support."),
        ("😢 Feeling Sad", "I've been feeling really sad lately and don't know what to do."),
        ("💪 Need Motivation", "I'm struggling to find motivation and could use some encouragement."),
        ("😴 Sleep Issues", "I've been having trouble sleeping and it's affecting my mood."),
        ("🧘 Want Coping Tips", "Can you share some coping strategies for managing stress?"),
        ("💬 Just Talk", "I just need someone to talk to about how I'm feeling."),
        ("🏠 Work/Life Balance", "I'm struggling with work-life balance and feeling overwhelmed."),
        ("👥 Relationship Issues", "I'm having some difficulties in my relationships and need advice."),
        ("🎯 Goal Setting", "I want to set some mental health goals but don't know where to start."),
        ("📈 Check Progress", "I'd like to talk about my mental health progress lately.")
    ]

def render_typing_animation() -> str:
    """Return CSS for typing animation"""
    return """
    <style>
    .typing-animation {
        display: inline-block;
        width: 60px;
        height: 20px;
        position: relative;
    }
    
    .typing-animation span {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #4CAF50;
        animation: typing 1.4s infinite ease-in-out both;
    }
    
    .typing-animation span:nth-child(1) {
        animation-delay: -0.32s;
    }
    
    .typing-animation span:nth-child(2) {
        animation-delay: -0.16s;
    }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
    </style>
    
    <div class="typing-animation">
        <span></span>
        <span></span>
        <span></span>
    </div>
    """

def check_browser_compatibility() -> Dict[str, bool]:
    """Check browser compatibility for advanced features"""
    # This is a placeholder - in a real app, you'd use JavaScript
    # to check browser capabilities
    return {
        "local_storage": True,  # Assume supported
        "notifications": False,  # Would need permission
        "speech_recognition": False,  # Advanced feature
        "offline_support": False  # Would need service worker
    }

def get_emergency_resources() -> List[Dict[str, str]]:
    """Get list of emergency resources"""
    return [
        {
            "name": "National Suicide Prevention Lifeline",
            "number": "988",
            "description": "24/7 crisis support",
            "type": "phone"
        },
        {
            "name": "Crisis Text Line", 
            "number": "741741",
            "description": "Text HOME for crisis support",
            "type": "text"
        },
        {
            "name": "Emergency Services",
            "number": "911",
            "description": "For immediate medical emergencies",
            "type": "emergency"
        },
        {
            "name": "SAMHSA National Helpline",
            "number": "1-800-662-4357",
            "description": "Treatment referral and information service",
            "type": "phone"
        }
    ]