import streamlit as st
from typing import List, Dict, Any
from datetime import datetime

def render_message(message: str, is_user: bool, sentiment: Dict = None, crisis_detected: bool = False):
    """Render a single chat message with appropriate styling"""
    
    if is_user:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
            <div style="background-color: #E3F2FD; padding: 15px; border-radius: 15px 15px 5px 15px; max-width: 80%; margin-left: 20%;">
                <strong>You:</strong><br/>
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message
        crisis_indicator = ""
        if crisis_detected:
            crisis_indicator = """
            <div style="background-color: #FFEBEE; border: 2px solid #F44336; border-radius: 8px; padding: 10px; margin: 5px 0;">
                <strong>⚠️ Crisis Response Activated</strong><br/>
                <small>This response includes emergency resources and support information.</small>
            </div>
            """
        
        sentiment_badge = ""
        if sentiment:
            sentiment_color = {
                'positive': '#C8E6C9',
                'negative': '#FFCDD2', 
                'neutral': '#E0E0E0'
            }.get(sentiment.get('label', 'neutral'), '#E0E0E0')
            
            sentiment_text_color = {
                'positive': '#2E7D32',
                'negative': '#C62828',
                'neutral': '#424242'
            }.get(sentiment.get('label', 'neutral'), '#424242')
            
            confidence = sentiment.get('confidence', 0) * 100
            
            sentiment_badge = f"""
            <div style="margin: 5px 0;">
                <span style="background-color: {sentiment_color}; color: {sentiment_text_color}; 
                           padding: 4px 8px; border-radius: 12px; font-size: 0.8em;">
                    Sentiment: {sentiment.get('label', 'neutral').title()} ({confidence:.0f}%)
                </span>
            </div>
            """
        
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
            <div style="background-color: #F1F8E9; padding: 15px; border-radius: 15px 15px 15px 5px; max-width: 80%; margin-right: 20%;">
                <strong>🧠 MindMate:</strong><br/>
                {message}
                {sentiment_badge}
                {crisis_indicator}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_chat_history(conversation_history: List[Dict[str, Any]]):
    """Render the complete chat history"""
    if not conversation_history:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #666;">
            <h3>👋 Welcome to MindMate!</h3>
            <p>I'm here to provide emotional support and listen to what's on your mind.</p>
            <p>Feel free to share how you're feeling today, or use the quick action buttons below.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for message_data in conversation_history:
        render_message(
            message=message_data["message"],
            is_user=message_data["is_user"],
            sentiment=message_data.get("sentiment"),
            crisis_detected=message_data.get("crisis_detected", False)
        )

def render_typing_indicator():
    """Show typing indicator while waiting for response"""
    st.markdown("""
    <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
        <div style="background-color: #F1F8E9; padding: 15px; border-radius: 15px 15px 15px 5px;">
            <strong>🧠 MindMate:</strong><br/>
            <div style="display: flex; align-items: center;">
                <div style="margin-right: 10px;">Thinking</div>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    .typing-dots {
        display: inline-flex;
    }
    .typing-dots span {
        height: 8px;
        width: 8px;
        background-color: #666;
        border-radius: 50%;
        margin: 0 2px;
        animation: typing 1.4s infinite ease-in-out both;
    }
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

def render_quick_actions():
    """Render quick action buttons for common scenarios"""
    st.markdown("### 🚀 Quick Actions")
    st.markdown("*Click any button below to start a conversation*")
    
    col1, col2, col3 = st.columns(3)
    
    actions = []
    
    with col1:
        if st.button("😰 Feeling Anxious", use_container_width=True):
            actions.append(("anxious", "I'm feeling really anxious right now and could use some support."))
        
        if st.button("😢 Feeling Sad", use_container_width=True):
            actions.append(("sad", "I've been feeling really sad lately and don't know what to do."))
    
    with col2:
        if st.button("💪 Need Motivation", use_container_width=True):
            actions.append(("motivation", "I'm struggling to find motivation and could use some encouragement."))
        
        if st.button("😴 Sleep Issues", use_container_width=True):
            actions.append(("sleep", "I've been having trouble sleeping and it's affecting my mood."))
    
    with col3:
        if st.button("🧘 Want Coping Tips", use_container_width=True):
            actions.append(("coping", "Can you share some coping strategies for managing stress?"))
        
        if st.button("💬 Just Talk", use_container_width=True):
            actions.append(("talk", "I just need someone to talk to about how I'm feeling."))
    
    return actions

def render_message_input():
    """Render the message input form"""
    with st.form("chat_form", clear_on_submit=True):
        st.markdown("### 💬 Share what's on your mind...")
        
        user_message = st.text_area(
            label="Message",
            height=100,
            placeholder="I'm here to listen. Feel free to share how you're feeling today...",
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            send_button = st.form_submit_button("Send 💙", use_container_width=True)
        
        with col2:
            if st.form_submit_button("Clear Chat", use_container_width=True):
                return None, True  # Signal to clear chat
        
        with col3:
            st.markdown("<small>Press Ctrl+Enter to send</small>", unsafe_allow_html=True)
        
        return user_message if send_button and user_message.strip() else None, False