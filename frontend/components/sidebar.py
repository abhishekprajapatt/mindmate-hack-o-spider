import streamlit as st
import requests
from typing import Optional

def render_sidebar(conversation_id: str, backend_url: str) -> Optional[str]:
    """Render the sidebar with app information and controls"""
    
    with st.sidebar:
        # App header
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1>🧠 MindMate</h1>
            <p style="color: #666; font-style: italic;">Your mental wellness companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        # About section
        st.markdown("---")
        st.subheader("💙 About MindMate")
        st.markdown("""
        MindMate provides empathetic, non-judgmental support for mental wellness. 
        Our AI is designed to:
        
        - 👂 **Listen** with empathy and understanding
        - 🧘 **Provide** practical coping strategies  
        - 🚨 **Detect** crisis situations immediately
        - 📞 **Connect** you with professional resources
        - 🛡️ **Protect** your privacy and wellbeing
        """)
        
        # Features section
        st.markdown("---")
        st.subheader("🔧 Features")
        
        feature_status = get_system_status(backend_url)
        
        st.markdown("**AI Capabilities:**")
        status_icon = "✅" if feature_status.get("sentiment_available", False) else "⚠️"
        st.markdown(f"{status_icon} Sentiment Analysis")
        
        status_icon = "✅" if feature_status.get("llm_available", False) else "⚠️"
        st.markdown(f"{status_icon} Intelligent Responses")
        
        st.markdown(f"✅ Crisis Detection")
        st.markdown(f"✅ Resource Connection")
        
        # Conversation controls
        st.markdown("---")
        st.subheader("🗨️ Conversation")
        
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            try:
                response = requests.delete(f"{backend_url}/conversations/{conversation_id}")
                if response.status_code == 200:
                    st.success("Conversation cleared!")
                    return "clear_chat"
            except:
                st.warning("Could not clear conversation on server")
                return "clear_chat"
        
        # Settings
        st.markdown("---")
        st.subheader("⚙️ Settings")
        
        show_sentiment = st.checkbox("Show sentiment analysis", value=True)
        show_resources = st.checkbox("Show resources panel", value=False)
        
        # Statistics (if available)
        stats = get_conversation_stats(backend_url)
        if stats:
            st.markdown("---")
            st.subheader("📊 Session Stats")
            st.metric("Messages sent", stats.get("message_count", 0))
            st.metric("Average sentiment", f"{stats.get('avg_sentiment', 0):.2f}")
        
        # Emergency resources
        st.markdown("---")
        render_emergency_resources()
        
        # Feedback
        st.markdown("---")
        st.subheader("💝 Feedback")
        if st.button("Rate this session", use_container_width=True):
            render_feedback_form()
        
        return {
            "show_sentiment": show_sentiment,
            "show_resources": show_resources
        }

def render_emergency_resources():
    """Render emergency resources in sidebar"""
    st.subheader("🆘 Emergency Resources")
    
    st.markdown("""
    **If you're in immediate danger:**
    
    📞 **Call 911** for emergencies
    
    📞 **988** - Suicide Prevention Lifeline
    
    📱 **Text HOME to 741741** - Crisis Text Line
    
    🌐 **SAMHSA.gov** - Find local resources
    """)
    
    if st.button("🔗 More Resources", use_container_width=True):
        st.markdown("""
        **Additional Support:**
        - National Alliance on Mental Illness: nami.org
        - Mental Health America: mhanational.org
        - Psychology Today: psychologytoday.com
        - Crisis Text Line: crisistextline.org
        - SAMHSA National Helpline: 1-800-662-4357
        """)

def get_system_status(backend_url: str) -> dict:
    """Get system status from backend"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            return {
                "sentiment_available": True,
                "llm_available": True,
                "backend_connected": True
            }
    except:
        pass
    
    return {
        "sentiment_available": False,
        "llm_available": False,
        "backend_connected": False
    }

def get_conversation_stats(backend_url: str) -> dict:
    """Get conversation statistics"""
    try:
        # This would need an endpoint to get session stats
        # For now, return empty dict
        return {}
    except:
        return {}

def render_feedback_form():
    """Render feedback form in sidebar"""
    with st.form("feedback_form"):
        st.markdown("**How was your experience?**")
        
        rating = st.select_slider(
            "Overall rating",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda x: "⭐" * x
        )
        
        helpful = st.radio(
            "Was MindMate helpful?",
            ["Very helpful", "Somewhat helpful", "Not helpful"]
        )
        
        comments = st.text_area(
            "Comments (optional)",
            placeholder="What worked well? What could be improved?"
        )
        
        if st.form_submit_button("Submit Feedback"):
            # In a real app, this would send to analytics
            st.success("Thank you for your feedback!")