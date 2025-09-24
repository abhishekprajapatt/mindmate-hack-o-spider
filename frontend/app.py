import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="MindMate - Mental Health Support",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BACKEND_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #F1F8E9;
        margin-right: 2rem;
    }
    .crisis-alert {
        background-color: #FFEBEE;
        border: 2px solid #F44336;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .sentiment-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.25rem;
    }
    .sentiment-positive { background-color: #C8E6C9; color: #2E7D32; }
    .sentiment-negative { background-color: #FFCDD2; color: #C62828; }
    .sentiment-neutral { background-color: #E0E0E0; color: #424242; }
    .safety-info {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = f"conv_{int(time.time())}"
    if 'show_resources' not in st.session_state:
        st.session_state.show_resources = False

def display_safety_disclaimer():
    """Display safety information"""
    st.markdown("""
    <div class="safety-info">
        <h4>🛡️ Safety Information</h4>
        <p><strong>This is an AI chatbot</strong> designed to provide emotional support and wellness resources. 
        It is NOT a replacement for professional mental health care.</p>
        
        <p><strong>In case of emergency:</strong> If you're experiencing thoughts of self-harm or suicide, 
        please contact emergency services (911) or the National Suicide Prevention Lifeline (988) immediately.</p>
    </div>
    """, unsafe_allow_html=True)

def display_message(message, is_user=True, sentiment=None, crisis_detected=False):
    """Display a chat message with styling"""
    css_class = "user-message" if is_user else "assistant-message"
    role = "You" if is_user else "MindMate"
    
    message_html = f"""
    <div class="chat-message {css_class}">
        <strong>{role}:</strong><br>
        {message}
    """
    
    if not is_user and sentiment:
        sentiment_class = f"sentiment-{sentiment.get('label', 'neutral')}"
        confidence = sentiment.get('confidence', 0) * 100
        message_html += f"""
        <br><span class="sentiment-badge {sentiment_class}">
            Sentiment: {sentiment.get('label', 'neutral').title()} ({confidence:.0f}% confidence)
        </span>
        """
    
    if crisis_detected:
        message_html += """
        <br><div class="crisis-alert">
            <strong>⚠️ Crisis Response Activated</strong><br>
            This message has been flagged for immediate attention. Please see the response above for important resources.
        </div>
        """
    
    message_html += "</div>"
    st.markdown(message_html, unsafe_allow_html=True)

def send_message(message):
    """Send message to backend and get response"""
    try:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "message": message,
                    "conversation_id": st.session_state.conversation_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Backend error: {response.status_code}")
                return None
                
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Please ensure the backend server is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def display_resources(resources):
    """Display mental health resources"""
    if resources:
        st.markdown("### 📚 Helpful Resources")
        for resource in resources:
            st.markdown(f"• {resource}")

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🧠 MindMate - Mental Health Support</h1>', unsafe_allow_html=True)
    st.markdown("*A compassionate AI companion for mental wellness support*")
    
    # Sidebar
    with st.sidebar:
        st.header("💙 About MindMate")
        st.markdown("""
        MindMate provides empathetic, non-judgmental support for mental wellness. 
        Our AI is trained to:
        - Listen with empathy
        - Provide coping strategies  
        - Detect crisis situations
        - Connect you with resources
        """)
        
        st.header("🔧 Features")
        st.markdown("""
        - **Sentiment Analysis**: Real-time emotion detection
        - **Crisis Detection**: Immediate escalation when needed
        - **Coping Strategies**: Practical wellness tips
        - **Resource Connection**: Links to professional help
        """)
        
        if st.button("🗑️ Clear Conversation"):
            try:
                requests.delete(f"{BACKEND_URL}/conversations/{st.session_state.conversation_id}")
            except:
                pass
            st.session_state.conversation_history = []
            st.session_state.conversation_id = f"conv_{int(time.time())}"
            st.rerun()
        
        if st.checkbox("Show Resources", value=st.session_state.show_resources):
            st.session_state.show_resources = True
        else:
            st.session_state.show_resources = False
    
    # Safety disclaimer
    display_safety_disclaimer()
    
    # Chat interface
    st.header("💬 Chat with MindMate")
    
    # Display conversation history
    for item in st.session_state.conversation_history:
        display_message(
            item["message"], 
            item["is_user"], 
            item.get("sentiment"), 
            item.get("crisis_detected", False)
        )
    
    # Message input
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_area(
            "Share what's on your mind...", 
            height=100,
            placeholder="I'm here to listen. Feel free to share how you're feeling today."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.form_submit_button("Send 💙", use_container_width=True)
        
        if send_button and user_message.strip():
            # Add user message to history
            st.session_state.conversation_history.append({
                "message": user_message,
                "is_user": True,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get response from backend
            response = send_message(user_message)
            
            if response:
                # Add assistant response to history
                st.session_state.conversation_history.append({
                    "message": response["response"],
                    "is_user": False,
                    "sentiment": response.get("sentiment"),
                    "crisis_detected": response.get("crisis_detected", False),
                    "timestamp": response.get("timestamp")
                })
                
                # Show resources if crisis detected or user wants to see them
                if response.get("crisis_detected") or st.session_state.show_resources:
                    if response.get("resources"):
                        st.markdown("---")
                        display_resources(response["resources"])
            
            st.rerun()
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😰 I'm feeling anxious"):
            st.session_state.conversation_history.append({
                "message": "I'm feeling really anxious right now and could use some support.",
                "is_user": True,
                "timestamp": datetime.now().isoformat()
            })
            response = send_message("I'm feeling really anxious right now and could use some support.")
            if response:
                st.session_state.conversation_history.append({
                    "message": response["response"],
                    "is_user": False,
                    "sentiment": response.get("sentiment"),
                    "crisis_detected": response.get("crisis_detected", False),
                    "timestamp": response.get("timestamp")
                })
            st.rerun()
    
    with col2:
        if st.button("😢 I'm feeling sad"):
            st.session_state.conversation_history.append({
                "message": "I've been feeling really sad lately and don't know what to do.",
                "is_user": True,
                "timestamp": datetime.now().isoformat()
            })
            response = send_message("I've been feeling really sad lately and don't know what to do.")
            if response:
                st.session_state.conversation_history.append({
                    "message": response["response"],
                    "is_user": False,
                    "sentiment": response.get("sentiment"),
                    "crisis_detected": response.get("crisis_detected", False),
                    "timestamp": response.get("timestamp")
                })
            st.rerun()
    
    with col3:
        if st.button("💪 I need motivation"):
            st.session_state.conversation_history.append({
                "message": "I'm struggling to find motivation and could use some encouragement.",
                "is_user": True,
                "timestamp": datetime.now().isoformat()
            })
            response = send_message("I'm struggling to find motivation and could use some encouragement.")
            if response:
                st.session_state.conversation_history.append({
                    "message": response["response"],
                    "is_user": False,
                    "sentiment": response.get("sentiment"),
                    "crisis_detected": response.get("crisis_detected", False),
                    "timestamp": response.get("timestamp")
                })
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🌟 Remember: You're not alone. Professional help is always available when you need it.</p>
        <p><small>MindMate Hackathon Demo • Built with ❤️ for mental wellness</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()