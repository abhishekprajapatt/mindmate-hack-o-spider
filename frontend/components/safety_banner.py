import streamlit as st

def render_safety_disclaimer():
    """Render the main safety disclaimer banner"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FFF3E0 0%, #FFF8E1 100%); 
                border-left: 4px solid #FF9800; 
                border-radius: 8px;
                padding: 20px; 
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: flex-start;">
            <div style="font-size: 24px; margin-right: 15px;">🛡️</div>
            <div>
                <h4 style="margin: 0 0 10px 0; color: #E65100;">Important Safety Information</h4>
                <p style="margin: 5px 0;"><strong>This is an AI chatbot</strong> designed to provide emotional support and wellness resources. 
                It is <strong>NOT a replacement</strong> for professional mental health care, medical advice, or emergency services.</p>
                
                <div style="background-color: #FFEBEE; border-radius: 6px; padding: 15px; margin: 15px 0;">
                    <p style="margin: 0; font-weight: bold; color: #C62828;">🚨 In Case of Emergency:</p>
                    <p style="margin: 5px 0;">If you're experiencing thoughts of self-harm, suicide, or immediate danger:</p>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li><strong>Call 911</strong> for immediate emergencies</li>
                        <li><strong>Call 988</strong> - National Suicide Prevention Lifeline</li>
                        <li><strong>Text HOME to 741741</strong> - Crisis Text Line</li>
                    </ul>
                </div>
                
                <p style="margin: 5px 0; font-size: 0.9em; color: #666;">
                    💝 <strong>Privacy:</strong> Your conversations are handled with care. We log anonymized data for safety and improvement purposes only.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_crisis_alert(resources=None):
    """Render crisis alert banner when crisis is detected"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FFEBEE 0%, #FCE4EC 100%); 
                border: 2px solid #F44336; 
                border-radius: 10px;
                padding: 20px; 
                margin: 20px 0;
                box-shadow: 0 4px 8px rgba(244,67,54,0.2);">
        <div style="display: flex; align-items: flex-start;">
            <div style="font-size: 32px; margin-right: 15px;">🚨</div>
            <div>
                <h3 style="margin: 0 0 10px 0; color: #C62828;">Crisis Support Activated</h3>
                <p style="margin: 5px 0; font-weight: bold;">Your safety is our top priority. Professional help is available right now.</p>
                
                <div style="background-color: #ffffff; border-radius: 8px; padding: 15px; margin: 15px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #1565C0;">📞 Immediate Help Available:</h4>
                    <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                        <li><strong>Emergency Services:</strong> 911</li>
                        <li><strong>National Suicide Prevention Lifeline:</strong> 988</li>
                        <li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
                        <li><strong>SAMHSA National Helpline:</strong> 1-800-662-4357</li>
                    </ul>
                </div>
                
                <p style="margin: 10px 0 0 0; font-style: italic; color: #666;">
                    You don't have to face this alone. Trained counselors are available 24/7 to provide immediate support.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show additional resources if provided
    if resources:
        st.markdown("### 📚 Additional Resources")
        for resource in resources:
            st.markdown(f"• {resource}")

def render_resource_panel(resources=None, show_extended=False):
    """Render mental health resources panel"""
    if not resources and not show_extended:
        return
    
    st.markdown("---")
    st.markdown("### 📚 Mental Health Resources")
    
    if resources:
        st.markdown("**Recommended for you:**")
        for resource in resources:
            st.markdown(f"• {resource}")
    
    if show_extended:
        with st.expander("🔍 Find More Resources"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **National Organizations:**
                - [NAMI](https://nami.org) - National Alliance on Mental Illness
                - [Mental Health America](https://mhanational.org)
                - [SAMHSA](https://samhsa.gov) - Treatment Locator
                - [Psychology Today](https://psychologytoday.com) - Find Therapists
                """)
                
                st.markdown("""
                **Crisis Support:**
                - National Suicide Prevention Lifeline: 988
                - Crisis Text Line: Text HOME to 741741  
                - Trans Lifeline: 877-565-8860
                - LGBT Hotline: 1-888-843-4564
                """)
            
            with col2:
                st.markdown("""
                **Specialized Support:**
                - [PTSD Alliance](https://ptsdalliance.org)
                - [Anxiety & Depression Assoc.](https://adaa.org)
                - [National Eating Disorders Assoc.](https://nationaleatingdisorders.org)
                - [RAINN](https://rainn.org) - Sexual Assault Hotline
                """)
                
                st.markdown("""
                **Self-Help Tools:**
                - Mindfulness apps (Headspace, Calm)
                - Crisis text apps (Crisis Text Line)
                - Mood tracking apps
                - Online therapy platforms
                """)

def render_wellbeing_tips():
    """Render daily wellbeing tips"""
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
        "😊 Practice smiling - it can actually improve mood"
    ]
    
    import random
    daily_tip = random.choice(tips)
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #E8F5E8 0%, #F1F8E9 100%); 
                border-left: 4px solid #4CAF50; 
                border-radius: 8px;
                padding: 15px; 
                margin: 15px 0;">
        <h4 style="margin: 0 0 8px 0; color: #2E7D32;">💡 Wellbeing Tip of the Day</h4>
        <p style="margin: 0; font-size: 16px;">{daily_tip}</p>
    </div>
    """, unsafe_allow_html=True)