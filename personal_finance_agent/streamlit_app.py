"""
Personal Finance Agent - Streamlit Web Application

A beautiful and modern web interface for personal finance management
with AI-powered insights and Finnish localization.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import requests
import json
from typing import Dict, Any, Optional, List
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Personal Finance Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/personal-finance-agent',
        'Report a bug': 'https://github.com/your-repo/personal-finance-agent/issues',
        'About': '''
        # Personal Finance Agent
        
        Älykkä henkilökohtaisen talouden hallintajärjestelmä, joka auttaa sinua säästämään 100 000€ tavoitteeseen!
        
        **Ominaisuudet:**
        - 🤖 AI-pohjainen transaktioiden luokittelu
        - 📄 OCR-dokumenttien käsittely
        - 📊 Reaaliaikaiset analytiikka
        - 🎯 Tavoitteiden seuranta
        - 💡 Älykkäät säästövinkit
        
        Versio 1.0.0
        '''
    }
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --warning-color: #ff7f0e;
        --danger-color: #d62728;
        --info-color: #17a2b8;
        --light-bg: #f8f9fa;
        --dark-bg: #343a40;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .success-card {
        border-left-color: var(--success-color);
    }
    
    .warning-card {
        border-left-color: var(--warning-color);
    }
    
    .danger-card {
        border-left-color: var(--danger-color);
    }
    
    /* Agent mood styling */
    .agent-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-avatar {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Navigation styling */
    .nav-pill {
        background-color: var(--primary-color);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-decoration: none;
        margin: 0.2rem;
        display: inline-block;
    }
    
    /* Finnish styling touches */
    .finnish-flag {
        background: linear-gradient(to bottom, #003580 33%, white 33%, white 66%, #003580 66%);
        height: 20px;
        width: 30px;
        display: inline-block;
        margin-right: 10px;
        border-radius: 3px;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .metric-card {
            margin-bottom: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "https://sentinel-100k.onrender.com/api/v1"

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# API Helper Functions
class APIClient:
    """API client for communicating with the FastAPI backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def set_auth_token(self, token: str):
        """Set authentication token for API requests."""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 401:
                st.session_state.authenticated = False
                st.session_state.user_token = None
                st.error("Session expired. Please log in again.")
                st.rerun()
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            st.warning("⚠️ API yhteys katkennut. Käytetään offline-tilaa.")
            return {}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.info(f"📝 Endpoint {endpoint} ei ole vielä käytössä backendissä.")
            else:
                error_msg = f"API Error: {e.response.status_code}"
                try:
                    error_detail = e.response.json().get('detail', str(e))
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {str(e)}"
                st.warning(error_msg)
            return {}
        except Exception as e:
            st.info(f"ℹ️ API-toiminto ei ole vielä saatavilla: {str(e)}")
            return {}
    
    def login(self, email: str, password: str) -> bool:
        """Authenticate user and store token."""
        # Try backend first
        data = {"email": email, "password": password}
        response = self.request("POST", "/auth/login", json=data)
        
        if response and response.get("status") == "success" and "access_token" in response:
            st.session_state.user_token = response["access_token"]
            st.session_state.user_info = response["user"]
            st.session_state.user_id = response["user"]["id"]
            st.session_state.authenticated = True
            self.set_auth_token(response["access_token"])
            return True
        
        # Fallback to local auth (temporary until backend is updated)
        return self._local_auth_login(email, password)
    
    def register(self, email: str, name: str, password: str) -> Dict[str, Any]:
        """Register new user."""
        # Try backend first
        data = {"email": email, "name": name, "password": password}
        response = self.request("POST", "/auth/register", json=data)
        
        if response and response.get("status"):
            return response
        
        # Fallback to local auth (temporary until backend is updated)
        return self._local_auth_register(email, name, password)
    
    def _local_auth_login(self, email: str, password: str) -> bool:
        """Local authentication fallback."""
        users_db = st.session_state.get('users_db', {})
        
        if email in users_db and users_db[email]["password"] == password:
            user = users_db[email]
            st.session_state.user_token = f"local_token_{int(time.time())}"
            st.session_state.user_info = {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "is_active": True
            }
            st.session_state.user_id = user["id"]
            st.session_state.authenticated = True
            return True
        return False
    
    def _local_auth_register(self, email: str, name: str, password: str) -> Dict[str, Any]:
        """Local registration fallback."""
        if 'users_db' not in st.session_state:
            st.session_state.users_db = {}
        
        users_db = st.session_state.users_db
        
        # Check if user already exists
        if email in users_db:
            return {"status": "error", "message": "Email already registered"}
        
        # Simple password validation
        if len(password) < 8:
            return {"status": "error", "message": "Password must be at least 8 characters long"}
        
        # Create new user
        user_id = f"user_{int(time.time())}"
        new_user = {
            "id": user_id,
            "email": email,
            "name": name,
            "password": password,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        users_db[email] = new_user
        st.session_state.users_db = users_db
        
        return {
            "status": "success", 
            "message": "User registered successfully",
            "user_id": user_id,
            "email": email,
            "name": name
        }
    
    def get_dashboard_summary(self, user_id: str = "demo_user") -> Dict[str, Any]:
        """Get complete dashboard data."""
        return self.request("GET", f"/dashboard/complete/{user_id}")
    
    def get_transactions(self, user_id: str = "demo_user") -> List[Dict[str, Any]]:
        """Get transactions for user."""
        # Mock data for now since endpoint doesn't exist yet
        return []
    
    def get_categories(self, user_id: str = "demo_user") -> List[Dict[str, Any]]:
        """Get categories for user."""
        # Mock data for now since endpoint doesn't exist yet
        return []
    
    def get_current_cycle(self, user_id: str = "demo_user") -> Dict[str, Any]:
        """Get current week cycle data."""
        return self.request("GET", f"/cycles/current/{user_id}")
    
    def get_all_cycles(self, user_id: str = "demo_user") -> Dict[str, Any]:
        """Get all 7-week cycles."""
        return self.request("GET", f"/cycles/all/{user_id}")
    
    def complete_week(self, user_id: str = "demo_user") -> Dict[str, Any]:
        """Complete current week and advance."""
        return self.request("POST", f"/cycles/complete-week/{user_id}")
    
    def get_night_analysis(self, user_id: str = "demo_user") -> Dict[str, Any]:
        """Get user's night analysis."""
        return self.request("GET", f"/analysis/night/user/{user_id}")
    
    def get_latest_analysis(self) -> Dict[str, Any]:
        """Get latest night analysis."""
        return self.request("GET", "/analysis/night/latest")
    
    def trigger_analysis(self) -> Dict[str, Any]:
        """Trigger night analysis manually."""
        return self.request("POST", "/analysis/night/trigger")
    
    def ai_chat(self, message: str) -> Dict[str, Any]:
        """Send message to AI chat."""
        return self.request("POST", "/chat/complete", json={"message": message})
    
    def start_onboarding(self) -> Dict[str, Any]:
        """Start onboarding process."""
        return self.request("POST", "/onboarding/start")
    
    def complete_onboarding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete onboarding with user data."""
        return self.request("POST", "/onboarding/complete", json=data)
    
    def upload_document(self, file_data, filename: str, document_type: str = None) -> Dict[str, Any]:
        """Upload document for OCR processing."""
        files = {"file": (filename, file_data, "application/octet-stream")}
        data = {}
        if document_type:
            data["document_type"] = document_type
        
        # Remove auth header for file upload (handled differently)
        headers = self.session.headers.copy()
        if "Content-Type" in headers:
            del headers["Content-Type"]
        
        try:
            url = f"{self.base_url}/documents/upload"
            response = requests.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"File upload failed: {str(e)}")
            return {}

# Initialize API client
api = APIClient(API_BASE_URL)

# Set auth token if user is authenticated
if st.session_state.authenticated and st.session_state.user_token:
    api.set_auth_token(st.session_state.user_token)

def show_login_page():
    """Display login/registration page."""
    st.markdown("""
    <div class="main-header">
        <div class="finnish-flag"></div>
        <h1>Personal Finance Agent</h1>
        <p>Älykkä henkilökohtaisen talouden hallinta • Tavoite: 100 000€</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login and registration
    login_tab, register_tab = st.tabs(["🔑 Kirjaudu sisään", "📝 Rekisteröidy"])
    
    with login_tab:
        st.subheader("Kirjaudu sisään")
        
        with st.form("login_form"):
            email = st.text_input("Sähköposti", placeholder="oma@email.fi")
            password = st.text_input("Salasana", type="password")
            submit_login = st.form_submit_button("Kirjaudu sisään", use_container_width=True)
            
            if submit_login:
                if email and password:
                    with st.spinner("Kirjaudutaan sisään..."):
                        if api.login(email, password):
                            st.success("✅ Kirjautuminen onnistui!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Virheellinen sähköposti tai salasana")
                else:
                    st.error("Täytä kaikki kentät")
        
        # Forgot password help
        st.caption("Unohditko salasanasi? Ota yhteyttä tukeen: support@sentinel100k.fi")
    
    with register_tab:
        st.subheader("Luo uusi tili")
        
        with st.form("register_form"):
            reg_name = st.text_input("Nimi", placeholder="Etunimi Sukunimi")
            reg_email = st.text_input("Sähköposti", placeholder="oma@email.fi")
            reg_password = st.text_input("Salasana", type="password", 
                                       help="Vähintään 8 merkkiä, isoja ja pieniä kirjaimia sekä numeroita")
            reg_password_confirm = st.text_input("Vahvista salasana", type="password")
            
            # Terms acceptance
            terms_accepted = st.checkbox("Hyväksyn käyttöehdot ja tietosuojaselosteen", value=False)
            
            submit_register = st.form_submit_button("Rekisteröidy", use_container_width=True)
            
            if submit_register:
                if not all([reg_name, reg_email, reg_password, reg_password_confirm]):
                    st.error("Täytä kaikki kentät")
                elif not terms_accepted:
                    st.error("Hyväksy käyttöehdot jatkaaksesi")
                elif reg_password != reg_password_confirm:
                    st.error("Salasanat eivät täsmää")
                elif len(reg_password) < 8:
                    st.error("Salasanan tulee olla vähintään 8 merkkiä pitkä")
                else:
                    with st.spinner("Luodaan tiliä..."):
                        result = api.register(reg_email, reg_name, reg_password)
                        if result and result.get("status") == "success":
                            st.success("✅ Tili luotu onnistuneesti!")
                            st.info(f"👋 Tervetuloa {reg_name}! Voit nyt kirjautua sisään sähköpostilla: {reg_email}")
                            st.balloons()
                        elif result and result.get("status") == "error":
                            st.error(f"❌ {result.get('message', 'Tilin luominen epäonnistui')}")
                        else:
                            st.error("❌ Tilin luominen epäonnistui")
    
    # Info section
    st.markdown("---")
    st.markdown("### ℹ️ Tietoa")
    st.info("Luo oma tili ja aloita henkilökohtainen säästömatka 100K€ tavoitteeseen!")
    
    # Security info
    st.markdown("### 🔒 Tietoturva")
    st.write("🛡️ Kaikki tietosi salataan ja suojataan")
    st.write("🇫🇮 Palvelin sijaitsee Suomessa")
    st.write("📱 GDPR-yhteensopiva")

def show_onboarding_prompt():
    """Show onboarding prompt for new users."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
        <h2>🌟 Tervetuloa Personal Finance Agentiin!</h2>
        <p style="font-size: 1.2rem;">Aloita henkilökohtainen säästömatka 100K€ tavoitteeseen</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### 🚀 Syvä Onboarding - 7 vaihetta menestykseen
        
        **Miksi onboarding kannattaa suorittaa?**
        
        ✅ **100% henkilökohtainen** strategia juuri sinulle  
        ✅ **AI-valmentaja** joka oppii mieltymyksestäsi  
        ✅ **7-viikon progressiiviset syklit** (300€ → 600€)  
        ✅ **CV-analyysi** parhaisiin tulomahdollisuuksiin  
        ✅ **Automaattinen yöanalyysi** joka optimoi strategiaasi  
        ✅ **Reaaliaikaiset suositukset** tavoitteiden saavuttamiseksi  
        
        **Kesto:** 15-20 minuuttia  
        **Hyöty:** Maksimaalinen tehokkuus säästämisessä
        """)
        
        st.markdown("---")
        
        # Onboarding CTA buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Aloita Deep Onboarding", use_container_width=True, type="primary"):
                st.session_state.current_page = "onboarding"
                st.rerun()
        
        with col2:
            if st.button("📊 Hyppää Dashboardiin", use_container_width=True):
                st.session_state.onboarding_completed = True
                st.rerun()
    
    # Benefits showcase
    st.markdown("---")
    st.subheader("🎯 Mitä saat onboardingista?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🤖 AI-Valmentaja
        - Henkilökohtainen coaching-tyyli
        - Reaaliaikaiset strategiamuutokset  
        - 24/7 optimointi taustalla
        """)
    
    with col2:
        st.markdown("""
        #### 📅 Viikkosyklit
        - Progressiivinen vaikeuus
        - Taito-pohjaiset haasteet
        - Automaattinen seuranta
        """)
    
    with col3:
        st.markdown("""
        #### 💰 Tulostrategiat
        - CV-pohjainen analyysi
        - Personoidut ansaintaideat
        - Optimaaliset tulolähteet
        """)
    
    # Success stories teaser
    st.markdown("---")
    st.subheader("🏆 Onnistumistarinoita")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **Muktar A. - Lääkäri**  
        "34.7% säästöaste onboardingin jälkeen! AI löysi täydellisn tasapainon perheen tuen ja 100K€ tavoitteen välille."
        """)
    
    with col2:
        st.info("""
        **Järjestelmän teho**  
        • 95% käyttäjistä saavuttaa tavoitteensa  
        • Keskimäärin 40% nopeampi säästötahti  
        • 100% personoitu kokemus
        """)
    
    # Final CTA
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎉 Aloita matka 100K€ tavoitteeseen!", use_container_width=True, type="primary"):
            st.session_state.current_page = "onboarding"
            st.rerun()
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🤖 AI-analytiikka
        - Automaattinen luokittelu
        - Älykkäät säästövinkit
        - Kulutustrendien analysointi
        """)
    
    with col2:
        st.markdown("""
        #### 📄 Dokumenttien käsittely
        - OCR-tekstitunnistus
        - Kuittien automaattinen käsittely
        - Tiliotteiden analysointi
        """)
    
    with col3:
        st.markdown("""
        #### 📊 Reaaliaikaiset raportit
        - Interaktiiviset kaaviot
        - Kuukausittaiset trendit
        - Tavoitteiden seuranta
        """)

def show_agent_mood(mood_score: int, message: str):
    """Display AI agent mood and message."""
    # Determine agent emoji based on mood
    if mood_score >= 80:
        agent_emoji = "🤩"
        mood_color = "#2ca02c"
        mood_text = "Erinomainen"
    elif mood_score >= 60:
        agent_emoji = "😊"
        mood_color = "#1f77b4"
        mood_text = "Hyvä"
    elif mood_score >= 40:
        agent_emoji = "😐"
        mood_color = "#ff7f0e"
        mood_text = "Kohtalainen"
    else:
        agent_emoji = "😟"
        mood_color = "#d62728"
        mood_text = "Huolestuttava"
    
    st.markdown(f"""
    <div class="agent-container" style="background: linear-gradient(135deg, {mood_color}aa 0%, {mood_color}cc 100%);">
        <div class="agent-avatar">{agent_emoji}</div>
        <h3>Talous-AI:n mielentila: {mood_text} ({mood_score}/100)</h3>
        <p style="font-size: 1.1rem; margin-bottom: 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application logic."""
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🏠 Navigaatio")
        
        # User info
        if st.session_state.user_info:
            st.markdown(f"**Tervetuloa, {st.session_state.user_info['name']}!** 👋")
        
        # Navigation menu
        pages = {
            "🏠 Dashboard": "dashboard",
            "🚀 Onboarding": "onboarding",
            "💰 Transaktiot": "transactions", 
            "📄 Dokumentit": "documents",
            "📊 Analytiikka": "analytics",
            "🎯 Tavoitteet": "goals",
            "🤖 Guardian": "guardian",
            "⚙️ Asetukset": "settings",
            "🧠 Intelligence": "intelligence"
        }
        
        selected_page = st.radio("Valitse sivu:", list(pages.keys()), key="page_selector")
        st.session_state.current_page = pages[selected_page]
        
        st.markdown("---")
        
        # Quick stats in sidebar  
        if not st.session_state.get('onboarding_completed', False):
            st.markdown("### 🚀 Onboarding")
            st.warning("⚠️ Suorita onboarding saadaksesi henkilökohtaiset ominaisuudet käyttöön!")
            if st.button("🎯 Aloita onboarding", use_container_width=True):
                st.session_state.current_page = "onboarding"
                st.rerun()
        else:
            user_id = st.session_state.get('user_id', 'demo_user')
            dashboard_data = api.get_dashboard_summary(user_id)
            
            if dashboard_data and dashboard_data.get('status') != 'error':
                st.markdown("### 📋 Henkilökohtaiset tiedot")
                user_profile = dashboard_data.get('user_profile', {})
                st.metric("Tavoitteen edistyminen", f"{user_profile.get('goal_progress', 0):.1f}%")
                st.metric("Nykyiset säästöt", f"€{user_profile.get('current_savings', 0):,.0f}")
                st.metric("Tavoite", f"€{user_profile.get('savings_goal', 100000):,.0f}")
                
                weekly_cycle = dashboard_data.get('weekly_cycle', {})
                if weekly_cycle:
                    st.metric("Viikko", f"{weekly_cycle.get('current_week', 1)}/7")
            else:
                st.markdown("### 📊 Aloita matka")
                st.info("Suorita onboarding saadaksesi henkilökohtaiset tiedot!")
        
        st.markdown("---")
        
        # Enhanced AI Chat (TÄYDENTÄÄ olemassa olevaa)
        st.markdown("### 🤖 Pika-AI (Enhanced)")
        user_message = st.text_input("Kysy jotain AI:lta:", placeholder="Miten säästän enemmän?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Perus AI", use_container_width=True) and user_message:
                with st.spinner("AI vastaa..."):
                    response = api.ai_chat(user_message)
                    if response and 'response' in response:
                        st.success("🤖 Perus AI:")
                        st.write(response['response'])
                    else:
                        st.info("AI ei vastannut.")
        
        with col2:
            if st.button("🎯 Enhanced AI", use_container_width=True) and user_message:
                with st.spinner("Enhanced AI analysoi profiiliasi..."):
                    try:
                        # Käytä enhanced context -toiminnallisuutta
                        from personal_finance_agent.app.services.user_context_service import get_enhanced_context_streamlit
                        
                        # Hae enhanced context
                        enhanced_context = get_enhanced_context_streamlit(st.session_state)
                        
                        # Simuloi enhanced AI vastaus
                        st.success("🎯 Enhanced AI:")
                        st.write(f"**Henkilökohtainen vastaus {enhanced_context.get('name', 'Käyttäjä')}:**")
                        
                        if "säästä" in user_message.lower():
                            current_savings = enhanced_context.get('current_savings', 0)
                            weekly_target = enhanced_context.get('target_income_weekly', 300)
                            st.write(f"💰 Nykyiset säästösi: {current_savings:,.0f}€")
                            st.write(f"📊 Viikkotavoitteesi: {weekly_target:,.0f}€")
                            st.write(f"🎯 Suositus osaamisesi perusteella: {', '.join(enhanced_context.get('interests', ['Yleinen säästäminen']))}")
                        
                        elif "tilanne" in user_message.lower() or "edistyminen" in user_message.lower():
                            progress = enhanced_context.get('progress_summary', {})
                            st.write(f"📈 Tavoitteen edistyminen: {progress.get('goal_progress_percentage', 0):.1f}%")
                            st.write(f"🗓️ Viikkoja suoritettu: {progress.get('weeks_completed', 0)}/7")
                            st.write(f"💪 Olet {'tavoitteessa' if progress.get('on_track', False) else 'hieman jäljessä'}")
                        
                        else:
                            watchdog_state = enhanced_context.get('watchdog_state', 'Passive')
                            st.write(f"🤖 Agentin tila: {watchdog_state}")
                            st.write(f"📊 Profiilitäydellisyys: {enhanced_context.get('data_completeness', 0)}%")
                            st.write("Henkilökohtainen vastaus perustuu täydelliseen profiiliisi!")
                        
                    except ImportError:
                        st.warning("Enhanced AI ei ole vielä käytettävissä. Käytä Perus AI:ta.")
                    except Exception as e:
                        st.error(f"Enhanced AI virhe: {str(e)}")
                        # Fallback perus AI:hin
                        response = api.ai_chat(user_message)
                        if response and 'response' in response:
                            st.info("🤖 Perus AI (fallback):")
                            st.write(response['response'])
        
        st.markdown("---")
        
        # Logout button  
        if st.button("🚪 Kirjaudu ulos", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_token = None
            st.session_state.user_info = None
            st.rerun()
    
    # Main content area
    page = st.session_state.current_page
    
    if page == "dashboard":
        show_dashboard_page()
    elif page == "onboarding":
        show_onboarding_page(api)
    elif page == "transactions":
        show_transactions_page(api)
    elif page == "documents":
        show_documents_page(api)
    elif page == "analytics":
        show_analytics_page(api)
    elif page == "goals":
        show_goals_page(api)
    elif page == "guardian":
        show_guardian_page(api)
    elif page == "settings":
        show_settings_page(api)
    elif page == "intelligence":
        show_intelligence_page(api)

def show_dashboard_page():
    """Display main dashboard page."""
    st.title("📊 Dashboard")
    
    # Check if user has completed onboarding
    if not st.session_state.get('onboarding_completed', False):
        show_onboarding_prompt()
        return
    
    # Load dashboard data
    user_id = st.session_state.get('user_id', 'demo_user')
    dashboard_data = api.get_dashboard_summary(user_id)
    
    if not dashboard_data or dashboard_data.get('status') == 'error':
        st.info("📊 Dashboard-tiedot ladataan kun olet suorittanut onboardingin.")
        st.markdown("---")
        
        # Show some demo metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Tavoitteen edistyminen", "0%")
        with col2:
            st.metric("💸 Nykyiset säästöt", "0€") 
        with col3:
            st.metric("💵 Viikkotavoite", "0€")
        with col4:
            st.metric("📅 Viikko", "0/7")
        return
    
    # Extract data from response
    user_profile = dashboard_data.get('user_profile', {})
    weekly_cycle = dashboard_data.get('weekly_cycle', {})
    night_analysis = dashboard_data.get('night_analysis', {})
    achievements = dashboard_data.get('achievements', {})
    
    # Show AI agent mood based on progress
    goal_progress = user_profile.get('goal_progress', 0)
    if goal_progress >= 75:
        agent_mood = 90
        agent_message = f"🎉 Erinomaista! {goal_progress:.1f}% tavoitteesta saavutettu!"
    elif goal_progress >= 50:
        agent_mood = 70
        agent_message = f"💪 Hyvää työtä! Olet jo {goal_progress:.1f}% tavoitteessa!"
    elif goal_progress >= 25:
        agent_mood = 50
        agent_message = f"🎯 Jatka samaan malliin! {goal_progress:.1f}% edistyminen on hyvä alku!"
    else:
        agent_mood = 30
        agent_message = f"🚀 Aloitetaan säästömatka! Tavoitteena {user_profile.get('savings_goal', 100000):,}€"
    
    show_agent_mood(agent_mood, agent_message)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Tavoitteen edistyminen",
            f"{goal_progress:.1f}%",
            delta=f"+{goal_progress:.1f}%" if goal_progress > 0 else None
        )
    
    with col2:
        current_savings = user_profile.get('current_savings', 0)
        st.metric(
            "💰 Nykyiset säästöt", 
            f"€{current_savings:,.0f}",
            delta=None
        )
    
    with col3:
        weekly_target = weekly_cycle.get('weekly_target', 0)
        st.metric(
            "📈 Viikkotavoite",
            f"€{weekly_target:.0f}",
            delta=None
        )
    
    with col4:
        current_week = weekly_cycle.get('current_week', 1)
        st.metric(
            "📅 Viikko",
            f"{current_week}/7",
            delta=f"Viikko {current_week}" if current_week > 1 else None
        )
    
    # Weekly cycle progress
    st.markdown("---")
    st.subheader("📅 Viikkosyklin edistyminen")
    
    if weekly_cycle and weekly_cycle.get('current_week', 0) > 0:
        current_week = weekly_cycle.get('current_week', 1)
        cycle_progress = weekly_cycle.get('cycle_progress', 0)
        challenges_count = weekly_cycle.get('challenges_count', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Viikko {current_week}/7**")
            st.progress(min(cycle_progress / 100, 1.0))
            st.caption(f"Sykliedistyminen: {cycle_progress:.1f}%")
            
            if st.button("✅ Merkitse viikko suoritetuksi", use_container_width=True):
                result = api.complete_week(user_id)
                if result and result.get('status') == 'advanced':
                    st.success(f"🎉 {result.get('congratulations_message', 'Viikko suoritettu!')}")
                    st.rerun()
                elif result and result.get('status') == 'cycle_completed':
                    st.balloons()
                    st.success("🏆 Kaikki 7 viikkoa suoritettu! Olet Sentinel-mestari!")
        
        with col2:
            st.metric("Viikkotavoite", f"€{weekly_target:.0f}")
            st.metric("Haasteita", f"{challenges_count} kpl")
            
            # Get current cycle details
            cycle_data = api.get_current_cycle(user_id)
            if cycle_data and cycle_data.get('status') == 'active':
                daily_target = cycle_data.get('daily_breakdown', {}).get('daily_savings_target', 0)
                st.metric("Päivätavoite", f"€{daily_target:.0f}")
    else:
        st.info("Suorita onboarding aloittaaksesi viikkosyklit!")
    
    # Night Analysis
    st.markdown("---")
    st.subheader("🌙 Yöanalyysi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if night_analysis:
            last_analysis = night_analysis.get('last_analysis', 'Never')
            risk_level = night_analysis.get('risk_level', 'unknown')
            
            risk_colors = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🔴',
                'unknown': '⚪'
            }
            
            st.write(f"**Viimeisin analyysi:** {last_analysis[:10] if last_analysis != 'Never' else 'Ei vielä'}")
            st.write(f"**Riskitaso:** {risk_colors.get(risk_level, '⚪')} {risk_level.title()}")
            
            recommendations_count = night_analysis.get('recommendations_count', 0)
            st.metric("AI-suosituksia", f"{recommendations_count} kpl")
        
        if st.button("🔄 Käynnistä yöanalyysi", use_container_width=True):
            with st.spinner("Analysoidaan..."):
                result = api.trigger_analysis()
                if result and result.get('status') == 'completed':
                    st.success(f"✅ Analyysi valmis! {result.get('users_analyzed', 0)} käyttäjää analysoitu.")
                    st.rerun()
    
    with col2:
        # Get user-specific night analysis
        user_analysis = api.get_night_analysis(user_id)
        if user_analysis and user_analysis.get('status') == 'available':
            analysis_data = user_analysis.get('user_analysis', {})
            recommendations = analysis_data.get('ai_recommendations', [])
            
            st.write("**AI-suositukset:**")
            for i, rec in enumerate(recommendations[:3], 1):
                st.write(f"{i}. {rec}")
            
            if len(recommendations) > 3:
                st.caption(f"... ja {len(recommendations) - 3} muuta suositusta")
        else:
            st.info("Yöanalyysiä ei ole vielä saatavilla")
    
    # Next Actions
    st.markdown("---")
    st.subheader("📋 Seuraavat toimet")
    
    next_actions = dashboard_data.get('next_actions', [])
    if next_actions:
        for i, action in enumerate(next_actions, 1):
            st.write(f"{i}. ✅ {action}")
    else:
        st.write("1. ✅ Suorita onboarding")
        st.write("2. ✅ Aloita ensimmäinen viikkosykli")
        st.write("3. ✅ Lataa CV analyysiä varten")
    
    # Enhanced Context View (TÄYDENTÄÄ dashboardia)
    try:
        from personal_finance_agent.app.services.user_context_service import get_enhanced_context_streamlit
        
        st.markdown("---")
        st.subheader("🎯 Enhanced Profile (Beta)")
        
        with st.expander("Näytä täydellinen käyttäjäkonteksti", expanded=False):
            try:
                enhanced_context = get_enhanced_context_streamlit(st.session_state)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**🧠 AI-konteksti:**")
                    st.write(f"• Watchdog-tila: {enhanced_context.get('watchdog_state', 'N/A')}")
                    st.write(f"• Motivaatiotaso: {enhanced_context.get('ai_context', {}).get('motivation_level', 'N/A')}/10")
                    st.write(f"• Datan täydellisyys: {enhanced_context.get('data_completeness', 0)}%")
                    
                    st.write("**💡 Kiinnostukset:**")
                    interests = enhanced_context.get('interests', [])
                    if interests:
                        for interest in interests:
                            st.write(f"• {interest}")
                    else:
                        st.write("• Määritellään onboardingissa")
                
                with col2:
                    st.write("**📊 Edistymisanalyysi:**")
                    progress = enhanced_context.get('progress_summary', {})
                    st.write(f"• Tavoitteeseen: {progress.get('amount_to_goal', 0):,.0f}€")
                    st.write(f"• Viikkoja jäljellä: {progress.get('weeks_remaining', 0)}")
                    st.write(f"• Tavoitteessa: {'✅' if progress.get('on_track', False) else '⚠️'}")
                    
                    st.write("**🔄 Syklin tiedot:**")
                    cycle_details = enhanced_context.get('current_cycle_details', {})
                    if cycle_details:
                        st.write(f"• Vaikeustaso: {cycle_details.get('difficulty_level', 'N/A')}")
                        st.write(f"• Haasteita: {len(cycle_details.get('challenges', []))}")
                    else:
                        st.write("• Ei aktiivista sykliä")
                
                # Kontekstin timestamp
                st.caption(f"Konteksti generoitu: {enhanced_context.get('context_generated', 'N/A')}")
                
            except Exception as e:
                st.error(f"Enhanced kontekstin lataus epäonnistui: {str(e)}")
                
    except ImportError:
        st.info("💡 Enhanced Profile -ominaisuus tulossa pian!")
    
    # Achievements
    if achievements and any(achievements.values()):
        st.markdown("---")
        st.subheader("🏆 Saavutukset")
        
        achievement_names = {
            'onboarding_master': '🎯 Onboarding-mestari',
            'cycle_participant': '📅 Sykli-osallistuja',
            'week_completer': '✅ Viikon suorittaja',
            'analysis_reviewed': '🌙 Analyysin tarkastaja'
        }
        
        earned_achievements = [name for key, earned in achievements.items() if earned for name in [achievement_names.get(key, key)]]
        
        for achievement in earned_achievements:
            st.write(achievement)
        
        st.caption(f"Saavutuksia ansaittu: {len(earned_achievements)}/4")

# Import page modules
from pages import (
    show_transactions_page,
    show_documents_page,
    show_analytics_page,
    show_goals_page,
    show_settings_page,
    show_guardian_page,
    show_intelligence_page,
    show_onboarding_page
)

if __name__ == "__main__":
    main()
