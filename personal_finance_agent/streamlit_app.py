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
API_BASE_URL = "http://localhost:8000/api/v1"

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
            st.error("❌ Cannot connect to API. Please ensure the API server is running.")
            st.info("Run: `python run_api.py` to start the API server")
            return {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"API Error: {e.response.status_code}"
            try:
                error_detail = e.response.json().get('detail', str(e))
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {str(e)}"
            st.error(error_msg)
            return {}
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return {}
    
    def login(self, email: str, password: str) -> bool:
        """Authenticate user and store token."""
        data = {"email": email, "password": password}
        response = self.request("POST", "/auth/login", json=data)
        
        if response and "access_token" in response:
            st.session_state.user_token = response["access_token"]
            st.session_state.user_info = response["user"]
            st.session_state.authenticated = True
            self.set_auth_token(response["access_token"])
            return True
        return False
    
    def register(self, email: str, name: str, password: str) -> bool:
        """Register new user."""
        data = {"email": email, "name": name, "password": password}
        response = self.request("POST", "/auth/register", json=data)
        return bool(response)
    
    def get_dashboard_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """Get dashboard summary data."""
        return self.request("GET", f"/dashboard/summary?period_days={period_days}")
    
    def get_transactions(self, **filters) -> List[Dict[str, Any]]:
        """Get transactions with filters."""
        params = {k: v for k, v in filters.items() if v is not None}
        response = self.request("GET", "/transactions/", params=params)
        return response if isinstance(response, list) else []
    
    def get_categories(self, include_stats: bool = False) -> List[Dict[str, Any]]:
        """Get categories."""
        params = {"include_stats": include_stats} if include_stats else {}
        response = self.request("GET", "/categories/", params=params)
        return response if isinstance(response, list) else []
    
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
    
    with register_tab:
        st.subheader("Luo uusi tili")
        
        with st.form("register_form"):
            reg_name = st.text_input("Nimi", placeholder="Etunimi Sukunimi")
            reg_email = st.text_input("Sähköposti", placeholder="oma@email.fi")
            reg_password = st.text_input("Salasana", type="password", 
                                       help="Vähintään 8 merkkiä, isoja ja pieniä kirjaimia sekä numeroita")
            reg_password_confirm = st.text_input("Vahvista salasana", type="password")
            submit_register = st.form_submit_button("Rekisteröidy", use_container_width=True)
            
            if submit_register:
                if not all([reg_name, reg_email, reg_password, reg_password_confirm]):
                    st.error("Täytä kaikki kentät")
                elif reg_password != reg_password_confirm:
                    st.error("Salasanat eivät täsmää")
                elif len(reg_password) < 8:
                    st.error("Salasanan tulee olla vähintään 8 merkkiä pitkä")
                else:
                    with st.spinner("Luodaan tiliä..."):
                        if api.register(reg_email, reg_name, reg_password):
                            st.success("✅ Tili luotu onnistuneesti! Voit nyt kirjautua sisään.")
                        else:
                            st.error("❌ Tilin luominen epäonnistui")
    
    # Demo section
    st.markdown("---")
    st.markdown("### 🚀 Demo-tili")
    st.info("Voit kokeilla sovellusta demo-tilillä: **demo@example.com** / **DemoPass123**")
    
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
        with st.spinner("Ladataan pikatilatietoja..."):
            dashboard_data = api.get_dashboard_summary(period_days=30)
            
            if dashboard_data:
                st.markdown("### 📋 Pikatilatiedot (30 pv)")
                st.metric("Tulot", f"€{dashboard_data.get('total_income', 0):.2f}")
                st.metric("Menot", f"€{dashboard_data.get('total_expenses', 0):.2f}")
                net_amount = dashboard_data.get('net_amount', 0)
                st.metric("Netto", f"€{net_amount:.2f}", 
                         delta=f"€{net_amount:.2f}" if net_amount != 0 else None)
        
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
        show_intelligence_page()

def show_dashboard_page():
    """Display main dashboard page."""
    st.title("📊 Dashboard")
    
    # Load dashboard data
    with st.spinner("Ladataan dashboard-tietoja..."):
        dashboard_data = api.get_dashboard_summary(period_days=30)
    
    if not dashboard_data:
        st.error("Dashboard-tietojen lataaminen epäonnistui")
        return
    
    # Show agent mood
    agent_mood = dashboard_data.get('agent_mood', 50)
    agent_message = dashboard_data.get('agent_message', 'Tervetuloa Personal Finance Agentiin!')
    show_agent_mood(agent_mood, agent_message)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Tulot (30 pv)",
            f"€{dashboard_data.get('total_income', 0):.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "💸 Menot (30 pv)", 
            f"€{dashboard_data.get('total_expenses', 0):.2f}",
            delta=f"{dashboard_data.get('expense_change_percent', 0):.1f}%"
        )
    
    with col3:
        net_amount = dashboard_data.get('net_amount', 0)
        st.metric(
            "💵 Nettosäästö",
            f"€{net_amount:.2f}",
            delta=f"€{net_amount:.2f}" if net_amount != 0 else None
        )
    
    with col4:
        st.metric(
            "📱 Transaktioita",
            dashboard_data.get('transaction_count', 0),
            delta=None
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Kuukausittaiset trendit")
        monthly_trends = dashboard_data.get('monthly_trends', [])
        
        if monthly_trends:
            df_trends = pd.DataFrame(monthly_trends)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_trends['month_name'],
                y=df_trends['income'],
                mode='lines+markers',
                name='Tulot',
                line=dict(color='#2ca02c', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=df_trends['month_name'],
                y=df_trends['expenses'],
                mode='lines+markers',
                name='Menot',
                line=dict(color='#d62728', width=3)
            ))
            
            fig.update_layout(
                title="Tulot vs Menot",
                xaxis_title="Kuukausi",
                yaxis_title="Summa (€)",
                hovermode='x unified',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ei riittävästi tietoja kuukausittaisille trendeille")
    
    with col2:
        st.subheader("🥧 Menot kategorioittain")
        top_categories = dashboard_data.get('top_categories', [])
        
        if top_categories:
            df_categories = pd.DataFrame(top_categories)
            
            fig = px.pie(
                df_categories,
                values='amount',
                names='name',
                title="Top 5 kategoriaa"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(template='plotly_white')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ei kategoriatietoja saatavilla")
    
    # Goals progress
    st.subheader("🎯 Tavoitteiden edistyminen")
    goal_progress = dashboard_data.get('goal_progress', [])
    
    if goal_progress:
        for goal in goal_progress:
            progress = goal['progress_percent']
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{goal['goal_name']}**")
                st.progress(min(progress / 100, 1.0))
                st.caption(f"€{goal['current_amount']:.2f} / €{goal['target_amount']:.2f}")
            
            with col2:
                status_emoji = {
                    'completed': '✅',
                    'on_track': '🟢', 
                    'behind': '🟡',
                    'overdue': '🔴'
                }.get(goal['status'], '⚪')
                st.metric("Tila", f"{status_emoji} {progress:.1f}%")
    else:
        st.info("Ei tavoitteita asetettu. Luo ensimmäinen tavoitteesi!")

# Import page modules
from pages import (
    show_transactions_page,
    show_documents_page,
    show_analytics_page,
    show_goals_page,
    show_settings_page,
    show_guardian_page,
    show_intelligence_page
)

if __name__ == "__main__":
    main()
