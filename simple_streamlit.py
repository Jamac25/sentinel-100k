#!/usr/bin/env python3
"""
🎯 ENHANCED SENTINEL 100K STREAMLIT - UPDATED 
=============================================
Päivitetty versio enhanced ominaisuuksilla:
✅ Goal Tracking Integration
✅ Enhanced Context System  
✅ Watchdog Monitoring
✅ Smart Dashboard
✅ Enhanced AI Chat
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 🌐 BACKEND CONNECTION (Updated for Enhanced Features)
# BACKEND_URL = "https://sentinel-100k.onrender.com"  # Production
BACKEND_URL = "http://localhost:8001"  # Local testing with enhanced features

# 🎨 Streamlit konfiguraatio
st.set_page_config(
    page_title="Sentinel 100K",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎯 API Helper Functions
class RenderAPI:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
    
    def test_connection(self):
        """Testaa yhteys Render-backendiin"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, {"error": str(e)}
    
    def health_check(self):
        """Terveystarkistus"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def start_onboarding(self):
        """Aloita onboarding"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/onboarding/start")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def complete_onboarding(self, data):
        """Täydennä onboarding"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/onboarding/complete", json=data)
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_current_cycle(self, user_id):
        """Hae nykyinen viikko"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/cycles/current/{user_id}")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def trigger_night_analysis(self):
        """Käynnistä yöanalyysi"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/analysis/night/trigger")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_latest_analysis(self):
        """Hae viimeisin analyysi"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/analysis/night/latest")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def chat_ai(self, message):
        """AI-chat (basic)"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/chat/complete", json={"message": message})
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    # 🎯 ENHANCED FEATURES - NEW!
    def get_enhanced_context(self, user_email):
        """Hae enhanced user context"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/context/{user_email}")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_goal_progress(self, user_email):
        """Hae goal tracking tiedot"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/goals/progress/{user_email}")
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def enhanced_ai_chat(self, message, user_email):
        """Enhanced AI chat with full context"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat/enhanced?user_email={user_email}", 
                json={"message": message}
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def get_dashboard_summary(self, user_email):
        """Hae complete dashboard summary"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/dashboard/complete/{user_email}")
            return response.json() if response.status_code == 200 else None
        except:
            return None

# Initialize API
api = RenderAPI()

# 🔐 Session State Setup
if 'user_email' not in st.session_state:
    st.session_state.user_email = "demo@example.com"  # Default demo user
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 🏠 Main App
def main():
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; color: white; text-align: center;">
        <h1>🇫🇮 Sentinel 100K - Suomalainen Talous-AI</h1>
        <p>Älykkä henkilökohtaisen talouden hallinta • Tavoite: 100 000€</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 🔌 Test Connection
    st.subheader("🔌 Yhteyden testi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌐 Testaa Render-yhteys", use_container_width=True):
            with st.spinner("Testataan yhteyttä..."):
                connected, result = api.test_connection()
                if connected:
                    st.success("✅ Yhteys Render-backendiin toimii!")
                    st.json(result)
                else:
                    st.error("❌ Yhteys epäonnistui!")
                    st.error(result.get("error", "Tuntematon virhe"))
    
    with col2:
        if st.button("🏥 Terveystarkistus", use_container_width=True):
            with st.spinner("Tarkistetaan backend..."):
                health = api.health_check()
                if health:
                    st.success("✅ Backend terve!")
                    st.json(health)
                else:
                    st.error("❌ Backend ei vastaa")
    
    # 📊 Navigation
    st.markdown("---")
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigaatio")
        
        # User Selection - ENHANCED!
        st.markdown("### 👤 Käyttäjä")
        demo_users = {
            "demo@example.com": "Demo Käyttäjä (35% edistymistä)",
            "muktar.ali.l@gmail.com": "Muktar Ali (0% edistymistä)", 
            "test@example.com": "Test User (Alert mode)"
        }
        
        selected_email = st.selectbox(
            "Valitse käyttäjä:", 
            list(demo_users.keys()),
            format_func=lambda x: demo_users[x],
            index=0
        )
        st.session_state.user_email = selected_email
        
        # Quick Enhanced Stats
        if st.button("🎯 Lataa Enhanced Context"):
            context_data = api.get_enhanced_context(selected_email)
            if context_data:
                ctx = context_data.get('enhanced_context', {})
                st.success(f"✅ {ctx.get('name', 'Käyttäjä')} ladattu!")
                st.metric("Edistyminen", f"{ctx.get('progress_summary', {}).get('goal_progress_percentage', 0):.1f}%")
                st.metric("Watchdog", ctx.get('watchdog_state', 'Unknown'))
                st.metric("Viikko", f"{ctx.get('current_week', 1)}/7")
        
        st.markdown("---")
        
        page = st.selectbox("Valitse sivu:", [
            "🎯 Enhanced Dashboard",  # NEW!
            "📊 Goal Tracking",       # NEW!
            "🧠 Psykologinen Profiili", # NEW!
            "🤖 Enhanced AI Chat",    # NEW!
            "🏠 Dashboard",
            "🚀 Onboarding", 
            "📊 Viikkoanalyysi",
            "🌙 Yöanalyysi",
            "🤖 AI-Chat",
            "⚙️ API-testit"
        ])
    
    # 📱 Page Content - ENHANCED!
    if page == "🎯 Enhanced Dashboard":
        show_enhanced_dashboard()  # NEW!
    elif page == "📊 Goal Tracking":
        show_goal_tracking()       # NEW!
    elif page == "🧠 Psykologinen Profiili":
        show_psychological_profile()  # NEW!
    elif page == "🤖 Enhanced AI Chat":
        show_enhanced_ai_chat()    # NEW!
    elif page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🚀 Onboarding":
        show_onboarding()
    elif page == "📊 Viikkoanalyysi":
        show_cycles()
    elif page == "🌙 Yöanalyysi":
        show_analysis()
    elif page == "🤖 AI-Chat":
        show_ai_chat()
    elif page == "⚙️ API-testit":
        show_api_tests()

# 🎯 NEW ENHANCED PAGES

def show_enhanced_dashboard():
    """Enhanced Dashboard with full context integration"""
    st.header("🎯 Enhanced Dashboard")
    
    user_email = st.session_state.user_email
    
    # Load dashboard summary using enhanced context
    with st.spinner("🎯 Ladataan enhanced dashboard..."):
        dashboard_data = api.get_dashboard_summary(user_email)
    
    if dashboard_data and dashboard_data.get('status') == 'success':
        st.success(f"✅ Enhanced dashboard ladattu käyttäjälle: {user_email}")
        
        # User Profile Section
        user_profile = dashboard_data.get('user_profile', {})
        st.subheader("👤 Käyttäjäprofiili")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Nykyiset säästöt", f"€{user_profile.get('current_savings', 0):,.0f}")
        with col2:
            st.metric("🎯 Tavoite", f"€{user_profile.get('savings_goal', 100000):,.0f}")
        with col3:
            st.metric("📈 Edistyminen", f"{user_profile.get('goal_progress', 0):.1f}%")
        with col4:
            st.metric("📊 Profiilin täydellisyys", f"{user_profile.get('data_completeness', 0)}%")
        
        # Weekly Cycle Section
        weekly_cycle = dashboard_data.get('weekly_cycle', {})
        st.subheader("📅 Viikkosykli")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Viikko", f"{weekly_cycle.get('current_week', 1)}/7")
            st.metric("Viikkotavoite", f"€{weekly_cycle.get('weekly_target', 0):.0f}")
        with col2:
            progress = weekly_cycle.get('cycle_progress', 0) / 100
            st.progress(progress)
            st.write(f"Sykli: {weekly_cycle.get('cycle_progress', 0):.1f}% valmis")
            st.write(f"Vaikeustaso: {weekly_cycle.get('difficulty_level', 'beginner')}")
        
        # Night Analysis & Watchdog
        night_analysis = dashboard_data.get('night_analysis', {})
        st.subheader("🌙 Yöanalyysi & Watchdog")
        
        col1, col2 = st.columns(2)
        with col1:
            watchdog_state = night_analysis.get('watchdog_state', 'Unknown')
            risk_level = night_analysis.get('risk_level', 'unknown')
            
            # Watchdog status with color coding
            if watchdog_state == "Alert":
                st.error(f"🚨 Watchdog: {watchdog_state}")
            elif watchdog_state == "Active":
                st.warning(f"⚡ Watchdog: {watchdog_state}")
            elif watchdog_state == "Optimized":
                st.success(f"✅ Watchdog: {watchdog_state}")
            else:
                st.info(f"🤖 Watchdog: {watchdog_state}")
            
            st.write(f"Riskitaso: {risk_level}")
        
        with col2:
            recommendations_count = night_analysis.get('recommendations_count', 0)
            st.metric("AI-suosituksia", f"{recommendations_count} kpl")
            
            if st.button("🔥 Käynnistä Watchdog analyysi"):
                analysis_result = api.trigger_night_analysis()
                if analysis_result:
                    st.success("✅ Watchdog analyysi käynnistetty!")
        
        # Enhanced Features Status
        enhanced_features = dashboard_data.get('enhanced_features', {})
        st.subheader("🚀 Enhanced Features Status")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"🎯 Goal Tracking: {enhanced_features.get('goal_tracking', 'inactive')}")
            st.write(f"🤖 Watchdog: {enhanced_features.get('watchdog_monitoring', 'inactive')}")
        with col2:
            st.write(f"🧠 AI Context: {enhanced_features.get('ai_context', 'inactive')}")
            st.write(f"📊 Data Sources: {enhanced_features.get('data_sources', 'incomplete')}")
        with col3:
            st.write(f"🎨 Personalization: {enhanced_features.get('personalization_level', 'basic')}")
            st.write(f"🌍 Environment: {dashboard_data.get('environment', 'unknown')}")
        
        # Next Actions
        next_actions = dashboard_data.get('next_actions', [])
        if next_actions:
            st.subheader("📋 Seuraavat toimet")
            for i, action in enumerate(next_actions, 1):
                st.write(f"{i}. {action}")
        
        # Achievements
        achievements = dashboard_data.get('achievements', {})
        earned = [name for name, earned in achievements.items() if earned]
        if earned:
            st.subheader("🏆 Saavutukset")
            for achievement in earned:
                st.write(f"✅ {achievement.replace('_', ' ').title()}")
    
    else:
        st.error("❌ Enhanced dashboard lataus epäonnistui")
        st.info("💡 Tarkista että backend on käynnissä ja käyttäjä on olemassa")

def show_goal_tracking():
    """Goal Tracking page with detailed progress analysis"""
    st.header("📊 Goal Tracking")
    
    user_email = st.session_state.user_email
    
    # Load goal progress
    with st.spinner("📊 Ladataan goal tracking dataa..."):
        goal_data = api.get_goal_progress(user_email)
    
    if goal_data and goal_data.get('status') == 'active':
        st.success(f"✅ Goal tracking aktiivinen käyttäjälle: {user_email}")
        
        # Main Goal Tracking Metrics
        goal_tracking = goal_data.get('goal_tracking', {})
        st.subheader("🎯 Päätaloustavoite")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            current_savings = goal_tracking.get('current_savings', 0)
            st.metric("💰 Nykyiset säästöt", f"€{current_savings:,.0f}")
        with col2:
            savings_goal = goal_tracking.get('savings_goal', 100000)
            st.metric("🎯 Tavoite", f"€{savings_goal:,.0f}")
        with col3:
            amount_to_goal = goal_tracking.get('amount_to_goal', 0)
            st.metric("🚀 Jäljellä tavoitteeseen", f"€{amount_to_goal:,.0f}")
        
        # Progress Visualization
        progress_percentage = goal_tracking.get('progress_percentage', 0)
        st.subheader("📈 Edistyminen")
        
        # Progress bar with color coding
        if progress_percentage >= 75:
            st.success(f"🌟 Erinomaista! {progress_percentage:.1f}% tavoitteesta saavutettu!")
        elif progress_percentage >= 50:
            st.warning(f"💪 Hyvää edistymistä! {progress_percentage:.1f}% tavoitteesta saavutettu!")
        elif progress_percentage >= 25:
            st.info(f"🎯 Hyvä alku! {progress_percentage:.1f}% tavoitteesta saavutettu!")
        else:
            st.error(f"🚨 Kiihdytä tahtia! Vain {progress_percentage:.1f}% tavoitteesta saavutettu!")
        
        # Progress bar
        st.progress(min(progress_percentage / 100, 1.0))
        
        # Weekly Status
        weekly_status = goal_data.get('weekly_status', {})
        st.subheader("📅 Viikkostatus")
        
        col1, col2 = st.columns(2)
        with col1:
            current_week = weekly_status.get('current_week', 1)
            weekly_target = weekly_status.get('weekly_target', 0)
            st.metric("Viikko", f"{current_week}/7")
            st.metric("Viikkotavoite", f"€{weekly_target:.0f}")
        
        with col2:
            cycle_progress = weekly_status.get('cycle_progress', 0)
            difficulty = weekly_status.get('difficulty_level', 'beginner')
            st.metric("Sykli edistyminen", f"{cycle_progress:.1f}%")
            st.metric("Vaikeustaso", difficulty.title())
        
        # Watchdog Monitoring
        watchdog_monitoring = goal_data.get('watchdog_monitoring', {})
        st.subheader("🤖 Watchdog Monitoring")
        
        col1, col2 = st.columns(2)
        with col1:
            watchdog_state = watchdog_monitoring.get('state', 'Unknown')
            risk_assessment = watchdog_monitoring.get('risk_assessment', 'unknown')
            
            # State indicator with appropriate styling
            if watchdog_state == "Alert":
                st.error(f"🚨 Watchdog Tila: {watchdog_state}")
                st.write("⚠️ Vaatii välitöntä huomiota!")
            elif watchdog_state == "Active":
                st.warning(f"⚡ Watchdog Tila: {watchdog_state}")
                st.write("📊 Aktiivinen seuranta käynnissä")
            elif watchdog_state == "Optimized":
                st.success(f"✅ Watchdog Tila: {watchdog_state}")
                st.write("🌟 Optimaalinen suorituskyky!")
            else:
                st.info(f"🤖 Watchdog Tila: {watchdog_state}")
            
            st.write(f"🎯 Riskinarvio: {risk_assessment}")
        
        with col2:
            recommendations = watchdog_monitoring.get('recommendations', [])
            if recommendations:
                st.write("💡 **Watchdog suositukset:**")
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
            else:
                st.write("✅ Ei aktiivisia suosituksia")
        
        # Time Analysis  
        weeks_completed = goal_tracking.get('weeks_completed', 0)
        weeks_remaining = goal_tracking.get('weeks_remaining', 0)
        on_track = goal_tracking.get('on_track', False)
        
        st.subheader("⏱️ Aikatauluanalyysi")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Viikkoja suoritettu", weeks_completed)
        with col2:
            st.metric("📅 Viikkoja jäljellä", weeks_remaining)
        with col3:
            track_status = "✅ Tavoitteessa" if on_track else "⚠️ Hieman jäljessä"
            st.metric("📊 Aikataulussa", track_status)
        
        # Enhanced Chart
        if progress_percentage > 0:
            st.subheader("📊 Edistymisen visualisointi")
            
            # Create progress chart
            progress_data = {
                'Kategoria': ['Saavutettu', 'Jäljellä'],
                'Summa': [current_savings, amount_to_goal],
                'Väri': ['#2ca02c', '#ff7f0e']
            }
            
            fig = px.pie(
                values=progress_data['Summa'], 
                names=progress_data['Kategoria'],
                title=f"Tavoitteen edistyminen: {progress_percentage:.1f}%",
                color_discrete_sequence=['#2ca02c', '#ff7f0e']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("❌ Goal tracking data ei saatavilla")
        st.info("💡 Tarkista että backend on käynnissä ja käyttäjä on suorittanut onboardingin")

def show_enhanced_ai_chat():
    """Enhanced AI Chat with full user context"""
    st.header("🤖 Enhanced AI Chat")
    
    user_email = st.session_state.user_email
    
    # Context info
    st.info(f"💡 Enhanced AI käyttää täydellistä kontekstia käyttäjälle: {user_email}")
    
    # Quick context load
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Lataa käyttäjäkonteksti"):
            context_data = api.get_enhanced_context(user_email)
            if context_data:
                ctx = context_data.get('enhanced_context', {})
                st.success("✅ Konteksti ladattu!")
                st.write(f"👤 **{ctx.get('name', 'Käyttäjä')}**")
                st.write(f"📊 Edistyminen: {ctx.get('progress_summary', {}).get('goal_progress_percentage', 0):.1f}%")
                st.write(f"🤖 Watchdog: {ctx.get('watchdog_state', 'Unknown')}")
                st.write(f"📅 Viikko: {ctx.get('current_week', 1)}/7")
    
    with col2:
        if st.button("📊 Lataa Goal Progress"):
            goal_data = api.get_goal_progress(user_email)
            if goal_data:
                goal_tracking = goal_data.get('goal_tracking', {})
                st.success("✅ Goal data ladattu!")
                st.write(f"💰 Säästöt: €{goal_tracking.get('current_savings', 0):,.0f}")
                st.write(f"🎯 Tavoite: €{goal_tracking.get('savings_goal', 100000):,.0f}")
                st.write(f"📈 Edistys: {goal_tracking.get('progress_percentage', 0):.1f}%")
    
    st.markdown("---")
    
    # Chat Interface
    st.subheader("💬 Enhanced AI Chat")
    
    # Predefined questions for easy testing
    st.write("**🎯 Pikakysmykset:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Säästötilanne"):
            test_enhanced_chat("Miten menee säästäminen?", user_email)
    
    with col2:
        if st.button("📊 Edistyminen"):
            test_enhanced_chat("Mikä on tilanne tavoitteessa?", user_email)
    
    with col3:
        if st.button("🎯 Neuvoja"):
            test_enhanced_chat("Mitä suosituksia minulle?", user_email)
    
    # Custom message input
    st.subheader("✍️ Vapaa kysymys")
    
    message = st.text_area(
        "Kysy jotain Enhanced AI:lta:", 
        "Analysoi tilannettani ja anna henkilökohtaisia neuvoja säästämiseen.",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Enhanced AI Chat", use_container_width=True):
            if message:
                test_enhanced_chat(message, user_email)
            else:
                st.warning("⚠️ Kirjoita viesti ensin")
    
    with col2:
        if st.button("🤖 Perus AI Chat", use_container_width=True):
            if message:
                with st.spinner("🤖 Perus AI vastaa..."):
                    result = api.chat_ai(message)
                    if result:
                        st.info("🤖 **Perus AI vastaus:**")
                        st.write(result.get('response', 'Ei vastausta'))
                        st.caption("(Ei henkilökohtaista kontekstia)")
                    else:
                        st.error("❌ Perus AI ei vastannut")

def test_enhanced_chat(message, user_email):
    """Helper function for enhanced chat testing"""
    with st.spinner("🎯 Enhanced AI analysoi henkilökohtaista profiiliasi..."):
        result = api.enhanced_ai_chat(message, user_email)
        if result:
            st.success("🎯 **Enhanced AI vastaus:**")
            
            # Display the enhanced response
            response = result.get('response', 'Ei vastausta')
            st.markdown(response)
            
            # Show metadata
            with st.expander("🔍 Enhanced AI metatiedot"):
                st.write(f"**Model:** {result.get('model', 'unknown')}")
                st.write(f"**Personalization:** {result.get('personalization_level', 'unknown')}")
                st.write(f"**Watchdog State:** {result.get('watchdog_state', 'unknown')}")
                st.write(f"**Goal Progress:** {result.get('goal_progress', 0):.1f}%")
                st.write(f"**Context Sources:** {', '.join(result.get('context_sources', []))}")
                st.write(f"**Environment:** {result.get('environment', 'unknown')}")
                st.write(f"**Enhanced Prompt:** {'✅' if result.get('enhanced_prompt_used', False) else '❌'}")
        else:
            st.error("❌ Enhanced AI ei vastannut")

def show_psychological_profile():
    """🧠 Psykologinen Profiili - UUSI SIVU!"""
    st.header("🧠 Psykologinen Profiili")
    
    user_email = st.session_state.user_email
    
    # Load enhanced context with psychological profiling
    with st.spinner("🧠 Ladataan psykologista profiilia..."):
        context_data = api.get_enhanced_context(user_email)
    
    if context_data and context_data.get('status') == 'success':
        enhanced_context = context_data.get('enhanced_context', {})
        psychological_profile = enhanced_context.get('psychological_profile', {})
        ai_coaching = enhanced_context.get('ai_coaching', {})
        
        if psychological_profile:
            st.success(f"✅ Psykologinen profiili ladattu käyttäjälle: {user_email}")
            
            # Persoonallisuusanalyysi
            st.subheader("🎭 Persoonallisuusanalyysi")
            
            dominant_personality = psychological_profile.get('dominant_personality', 'ACHIEVER')
            personality_profile = psychological_profile.get('personality_profile', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                ### {personality_profile.get('emoji', '🤖')} {personality_profile.get('name', 'Tuntematon')}
                
                **Luonteenpiirteet:**
                """)
                traits = personality_profile.get('traits', [])
                for trait in traits:
                    st.write(f"• {trait.title()}")
                
                st.write(f"**Coaching-tyyli:** {personality_profile.get('coaching_style', 'N/A')}")
            
            with col2:
                # Persoonallisuuspisteet
                personality_scores = psychological_profile.get('personality_scores', {})
                
                if personality_scores:
                    st.write("**Persoonallisuuspisteet:**")
                    
                    for personality_type, score in personality_scores.items():
                        progress_value = score / 3.0 if score > 0 else 0.1
                        
                        # Color coding based on score
                        if personality_type == dominant_personality:
                            st.success(f"🎯 {personality_type}: {score}/3")
                        else:
                            st.info(f"• {personality_type}: {score}/3")
            
            # Psykologiset ominaisuudet
            st.subheader("🧠 Psykologiset ominaisuudet")
            
            psychological_traits = psychological_profile.get('psychological_traits', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                motivation = psychological_traits.get('motivation_level', 5)
                st.metric("💪 Motivaatiotaso", f"{motivation}/10")
                
                if motivation >= 8:
                    st.success("🔥 Erittäin korkea!")
                elif motivation >= 6:
                    st.info("✅ Hyvä taso")
                else:
                    st.warning("⚠️ Tarvitsee tukea")
            
            with col2:
                commitment = psychological_traits.get('commitment_level', 5)
                st.metric("🎯 Sitoutumistaso", f"{commitment}/10")
                
                if commitment >= 8:
                    st.success("💎 Sitoutunut!")
                elif commitment >= 6:
                    st.info("✅ Kohtuullinen")
                else:
                    st.warning("⚠️ Heikko sitoutuminen")
            
            with col3:
                learning_style = psychological_traits.get('learning_style', 'N/A')
                st.metric("📚 Oppimistyyli", learning_style)
                
                support_needs = psychological_traits.get('support_needs', 'N/A')
                st.write(f"🤝 **Tuen tarve:** {support_needs}")
            
            # Motivaation laukaisijoita
            motivation_triggers = psychological_profile.get('motivation_triggers', [])
            if motivation_triggers:
                st.subheader("🎯 Motivaation laukaisijoita")
                
                cols = st.columns(len(motivation_triggers))
                for i, trigger in enumerate(motivation_triggers):
                    with cols[i]:
                        st.info(f"💡 {trigger.title()}")
            
            # Psykologiset oivallukset
            psychological_insights = psychological_profile.get('psychological_insights', [])
            if psychological_insights:
                st.subheader("🔍 Psykologiset oivallukset")
                
                for i, insight in enumerate(psychological_insights, 1):
                    st.write(f"{i}. {insight}")
        
        # AI Coaching profiili
        if ai_coaching:
            st.markdown("---")
            st.subheader("🤖 AI Coaching Profiili")
            
            optimal_coaching = ai_coaching.get('optimal_coaching_style', 'COACH')
            coaching_profile = ai_coaching.get('coaching_profile', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                ### {coaching_profile.get('emoji', '🤖')} {coaching_profile.get('name', 'Valmentaja')}
                
                **Tyyli:** {coaching_profile.get('style', 'N/A')}
                
                **Lähestymistapa:** {coaching_profile.get('approach', 'N/A')}
                """)
            
            with col2:
                # Personalized approach
                personalized_approach = ai_coaching.get('personalized_approach', {})
                
                if personalized_approach:
                    st.write("**Henkilökohtainen lähestymistapa:**")
                    st.write(f"💬 **Viestintä:** {personalized_approach.get('communication_style', 'N/A')}")
                    st.write(f"🎯 **Tavoitteet:** {personalized_approach.get('goal_setting_approach', 'N/A')}")
                    st.write(f"📅 **Palaute:** {personalized_approach.get('feedback_frequency', 'N/A')}")
            
            # Adaptiiviset vastaukset
            adaptive_responses = ai_coaching.get('adaptive_responses', {})
            if adaptive_responses:
                st.subheader("💬 Adaptiiviset AI-vastaukset")
                
                st.write("**Eri tilanteisiin räätälöidyt vastaukset:**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"**Onnistuminen:** {adaptive_responses.get('success_response', 'N/A')}")
                    st.info(f"**Ohjaus:** {adaptive_responses.get('guidance_response', 'N/A')}")
                
                with col2:
                    st.warning(f"**Vaikeudet:** {adaptive_responses.get('struggle_response', 'N/A')}")
                    st.error(f"**Motivointi:** {adaptive_responses.get('motivation_response', 'N/A')}")
            
            # Personoidut AI promptit
            personalized_prompts = ai_coaching.get('personalized_prompts', {})
            if personalized_prompts:
                with st.expander("🔧 Personoidut AI Promptit (Tekninen)", expanded=False):
                    st.code(personalized_prompts.get('system_prompt', 'Ei saatavilla'), language='markdown')
        
        # Psykologinen kehityssuunnitelma
        st.markdown("---")
        st.subheader("📈 Psykologinen kehityssuunnitelma")
        
        if psychological_profile and ai_coaching:
            # Analysoi kehityskohteita
            traits = psychological_profile.get('psychological_traits', {})
            motivation = traits.get('motivation_level', 5)
            commitment = traits.get('commitment_level', 5)
            
            development_plan = []
            
            if motivation < 7:
                development_plan.append("💪 Motivation boosting - säännölliset onnistumiset ja palkinnot")
            
            if commitment < 7:
                development_plan.append("🎯 Sitoutumisen vahvistaminen - selkeät välitavoitteet")
            
            support_needs = traits.get('support_needs', '')
            if 'paljon' in support_needs.lower():
                development_plan.append("🤝 Tuen järjestäminen - säännöllinen yhteydenpito")
            
            if development_plan:
                st.write("**Suositellut kehityskohteet:**")
                for i, item in enumerate(development_plan, 1):
                    st.write(f"{i}. {item}")
            else:
                st.success("✅ Psykologinen profiili on tasapainossa! Jatka samaan malliin.")
        
        # Testaa psykologista AI:ta
        st.markdown("---")
        st.subheader("🧪 Testaa psykologista AI:ta")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💪 Motivoi minua", use_container_width=True):
                test_enhanced_chat("Tarvitsen motivointia", user_email)
        
        with col2:
            if st.button("🎯 Anna ohjausta", use_container_width=True):
                test_enhanced_chat("Anna minulle henkilökohtaista ohjausta", user_email)
        
        with col3:
            if st.button("🏆 Kannusta onnistumisesta", use_container_width=True):
                test_enhanced_chat("Onnistuin tavoitteessani!", user_email)
    
    else:
        st.error("❌ Psykologisen profiilin lataus epäonnistui")
        st.info("💡 Tarkista että backend on käynnissä ja enhanced context on saatavilla")
        
        # Fallback: näytä demo psykologinen profiili
        st.markdown("---")
        st.subheader("📖 Demo Psykologinen Profiili")
        
        st.info("Kun enhanced context on saatavilla, näet täällä:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 ACHIEVER-tyyppi:**")
            st.write("• Tavoitteellinen")
            st.write("• Määrätietoinen") 
            st.write("• Tuloshakuinen")
            st.write("• Motivaatiolaukaisijoita: kilpailu, edistyminen")
        
        with col2:
            st.write("**🤖 COACH-valmentaja:**")
            st.write("• Haastava ja tavoiteorientoitunut")
            st.write("• Konkreettiset toimenpiteet")
            st.write("• Viikoittainen palaute")
            st.write("• Antaa itsenäisyyttä")

def show_dashboard():
    """Dashboard-sivu"""
    st.header("📊 Dashboard")
    
    # Test backend connection
    connected, result = api.test_connection()
    
    if connected:
        st.success("🌐 Yhdistetty Render-backendiin!")
        
        # Show service info
        if isinstance(result, dict):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🏢 Palvelu", result.get("service", "Unknown"))
            with col2:
                st.metric("📊 Tila", result.get("status", "Unknown"))
            with col3:
                st.metric("🔄 Versio", result.get("version", "Unknown"))
            
            # Features
            features = result.get("features", {})
            if features:
                st.subheader("🚀 Saatavilla olevat ominaisuudet")
                
                for feature, status in features.items():
                    status_emoji = "✅" if status == "active" else "❌"
                    st.write(f"{status_emoji} **{feature.replace('_', ' ').title()}**: {status}")
    else:
        st.error("❌ Ei yhteyttä backendiin")
        st.info("🔧 Tarkista että Render-backend on käynnissä")

def show_onboarding():
    """Onboarding-sivu"""
    st.header("🚀 Deep Onboarding")
    
    # Start onboarding
    if st.button("▶️ Aloita onboarding"):
        with st.spinner("Aloitetaan onboarding..."):
            result = api.start_onboarding()
            if result:
                st.success("✅ Onboarding aloitettu!")
                st.json(result)
            else:
                st.error("❌ Onboarding epäonnistui")
    
    # Complete onboarding form
    st.subheader("📝 Täydennä profiilit")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nimi", "Testi Käyttäjä")
            email = st.text_input("Sähköposti", "testi@example.com")
            age = st.number_input("Ikä", 25, 80, 30)
            profession = st.text_input("Ammatti", "Ohjelmistokehittäjä")
        
        with col2:
            current_savings = st.number_input("Nykyiset säästöt (€)", 0, 100000, 5000)
            savings_goal = st.number_input("Säästötavoite (€)", 10000, 200000, 100000)
            monthly_income = st.number_input("Kuukausitulot (€)", 1000, 20000, 3500)
            monthly_expenses = st.number_input("Kuukausimenot (€)", 500, 15000, 2500)
        
        # Skills and preferences
        skills = st.multiselect("Taidot", [
            "Ohjelmointi", "Suunnittelu", "Markkinointi", "Myynti", 
            "Opetus", "Käännöstyö", "Valokuvaus", "Kirjoittaminen"
        ])
        
        work_experience_years = st.slider("Työkokemusta (vuotta)", 0, 40, 5)
        education_level = st.selectbox("Koulutustaso", [
            "Peruskoulu", "Lukio", "Ammattikoulu", "AMK", "Yliopisto", "Tohtori"
        ])
        risk_tolerance = st.selectbox("Riskinsietokyky", [
            "Konservatiivinen", "Maltillinen", "Aggressiivinen"
        ])
        
        submitted = st.form_submit_button("✅ Täydennä onboarding")
        
        if submitted:
            onboarding_data = {
                "name": name,
                "email": email,
                "age": age,
                "profession": profession,
                "current_savings": current_savings,
                "savings_goal": savings_goal,
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "skills": skills,
                "work_experience_years": work_experience_years,
                "education_level": education_level,
                "risk_tolerance": risk_tolerance,
                "time_availability_hours": 10,
                "financial_goals": ["Säästäminen", "Sijoittaminen"],
                "investment_experience": "Aloittelija",
                "preferred_income_methods": ["Freelancing", "Sijoittaminen"]
            }
            
            with st.spinner("Lähetetään tiedot..."):
                result = api.complete_onboarding(onboarding_data)
                if result:
                    st.success("🎉 Onboarding valmis!")
                    st.json(result)
                else:
                    st.error("❌ Virhe onboardingissa")

def show_cycles():
    """Viikkoanalyysi-sivu"""
    st.header("📊 Viikkoanalyysi")
    
    user_id = st.text_input("Käyttäjä ID", "user_1735831285")
    
    if st.button("📈 Hae viikkosykli"):
        with st.spinner("Haetaan sykliä..."):
            result = api.get_current_cycle(user_id)
            if result:
                st.success("✅ Sykli haettu!")
                st.json(result)
                
                # Visualize cycle if data available
                if "savings_target" in result:
                    st.subheader("🎯 Viikon tavoite")
                    progress = st.progress(0.3)  # Example progress
                    st.metric("Säästötavoite", f"€{result['savings_target']}")
                    st.metric("Tulotavoite", f"€{result.get('income_target', 0)}")
            else:
                st.error("❌ Syklin haku epäonnistui")

def show_analysis():
    """Yöanalyysi-sivu"""
    st.header("🌙 Yöanalyysi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔥 Käynnistä yöanalyysi"):
            with st.spinner("🌙 Analysoidaan..."):
                result = api.trigger_night_analysis()
                if result:
                    st.success("✅ Yöanalyysi valmis!")
                    st.json(result)
                else:
                    st.error("❌ Analyysi epäonnistui")
    
    with col2:
        if st.button("📊 Hae viimeisin analyysi"):
            with st.spinner("Haetaan analyysiä..."):
                result = api.get_latest_analysis()
                if result:
                    st.success("✅ Analyysi haettu!")
                    st.json(result)
                else:
                    st.error("❌ Analyysin haku epäonnistui")

def show_ai_chat():
    """AI-Chat-sivu"""
    st.header("🤖 AI-Chat")
    
    # Chat interface
    message = st.text_input("💬 Kysy jotain AI:lta:", "Miten voin säästää enemmän rahaa?")
    
    if st.button("📤 Lähetä viesti"):
        if message:
            with st.spinner("🤖 AI vastaa..."):
                result = api.chat_ai(message)
                if result:
                    st.success("✅ AI vastasi!")
                    st.write(f"**🤖 AI:** {result.get('response', 'Ei vastausta')}")
                    st.json(result)
                else:
                    st.error("❌ AI ei vastannut")
        else:
            st.warning("⚠️ Kirjoita viesti ensin")

def show_api_tests():
    """API-testit-sivu"""
    st.header("⚙️ API-testit")
    
    # Backend info
    st.subheader("🔧 Backend-tiedot")
    st.code(f"Backend URL: {BACKEND_URL}")
    
    # Test all endpoints
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("POST", "/api/v1/onboarding/start", "Start onboarding"),
        ("GET", "/api/v1/analysis/night/latest", "Latest analysis"),
        ("POST", "/api/v1/analysis/night/trigger", "Trigger analysis"),
        ("POST", "/api/v1/chat/complete", "AI Chat")
    ]
    
    st.subheader("🧪 Endpoint-testit")
    
    for method, endpoint, description in endpoints:
        if st.button(f"{method} {endpoint}", key=f"test_{endpoint}"):
            test_endpoint(method, endpoint, description)

def test_endpoint(method, endpoint, description):
    """Testaa yksittäinen endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    with st.spinner(f"Testataan {description}..."):
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                if "chat" in endpoint:
                    response = requests.post(url, json={"message": "Testi"})
                else:
                    response = requests.post(url)
            
            if response.status_code == 200:
                st.success(f"✅ {description} toimii!")
                st.json(response.json())
            else:
                st.error(f"❌ {description} epäonnistui: {response.status_code}")
                try:
                    st.error(response.json())
                except:
                    st.error(response.text)
        except Exception as e:
            st.error(f"❌ Virhe: {str(e)}")

if __name__ == "__main__":
    main() 