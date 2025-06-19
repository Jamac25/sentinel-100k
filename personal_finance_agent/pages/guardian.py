"""
Sentinel Watchdog™ - Guardian Page
Älykkään käyttäytymismallin mukainen 100k€ tavoitteen valvonta
"""
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List
import json

# Sivun konfiguraatio
st.set_page_config(
    page_title="Sentinel Watchdog™",
    page_icon="🤖🛡️",
    layout="wide"
)

def make_api_request(api, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Tee API-pyyntö käyttäen API-objektia"""
    try:
        return api.request(method, endpoint, json=data) if data else api.request(method, endpoint)
    except Exception as e:
        return {"status": "error", "message": str(e)}

def display_watchdog_mode_badge(mode: str, risk_level: str):
    """Näytä Watchdog-moodi merkki"""
    mode_colors = {"passive": "#28a745", "active": "#ffc107", "aggressive": "#fd7e14", "emergency": "#dc3545"}
    mode_emojis = {"passive": "😊", "active": "💪", "aggressive": "😤", "emergency": "🚨"}
    mode_names = {"passive": "PASSIIVINEN", "active": "AKTIIVINEN", "aggressive": "AGGRESSIIVINEN", "emergency": "HÄTÄTILA"}
    
    color = mode_colors.get(mode, "#6c757d")
    emoji = mode_emojis.get(mode, "🤖")
    name = mode_names.get(mode, mode.upper())
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}20, {color}10); border: 2px solid {color}; border-radius: 15px; padding: 15px; text-align: center; margin: 10px 0;">
        <div style="font-size: 2.5rem; margin-bottom: 5px;">{emoji}</div>
        <div style="font-size: 1.2rem; font-weight: bold; color: {color};">SENTINEL WATCHDOG™</div>
        <div style="font-size: 1.5rem; font-weight: bold; margin: 5px 0;">{name}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Riskitaso: {risk_level.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

def display_situation_room(situation_data: Dict):
    """Näytä Situation Room -analyysi"""
    st.subheader("🧠 Situation Room - Tilanneanalyysi")
    
    col1, col2, col3 = st.columns(3)
    periods = {"7d": {"name": "7 päivää", "col": col1}, "30d": {"name": "30 päivää", "col": col2}, "90d": {"name": "90 päivää", "col": col3}}
    
    for period_key, period_info in periods.items():
        if period_key in situation_data:
            data = situation_data[period_key]
            with period_info["col"]:
                st.metric(f"📊 {period_info['name']}", f"{data['net_savings']:.0f}€", f"Päivässä: {data['daily_savings']:.1f}€")
                
                # Pieni graafi volatiliteetista
                if data['income_volatility'] > 0 or data['expense_volatility'] > 0:
                    volatility_data = pd.DataFrame({
                        'Tyyppi': ['Tulot', 'Menot'],
                        'Volatiliteetti': [data['income_volatility'], data['expense_volatility']]
                    })
                    
                    fig = px.bar(
                        volatility_data, 
                        x='Tyyppi', 
                        y='Volatiliteetti',
                        title=f"Volatiliteetti ({period_info['name']})",
                        color_discrete_map={'Tulot': '#28a745', 'Menot': '#dc3545'}
                    )
                    fig.update_layout(height=200, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

def display_target_analysis(target_data: Dict):
    """Näytä tavoiteanalyysi"""
    st.subheader("🎯 Tavoiteanalyysi - 100k€ Polku")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏆 Tavoite", f"{target_data['target_amount']:,}€".replace(',', ' '), "100 000€")
    with col2:
        st.metric("📈 Vaadittu/kk", f"{target_data['required_monthly_savings']:.0f}€", "5 vuodessa")
    with col3:
        st.metric("💰 Nykyinen/kk", f"{target_data['current_monthly_savings']:.0f}€", f"{target_data['savings_gap']:+.0f}€")
    with col4:
        gap_percentage = target_data.get('gap_percentage', 0)
        st.metric("⚡ Vaje", f"{abs(gap_percentage):.1f}%", "tavoitteesta" if gap_percentage > 0 else "ylitys!")
    
    progress = max(0, min(1, target_data['current_monthly_savings'] / target_data['required_monthly_savings']))
    st.progress(progress)
    
    if gap_percentage > 0:
        st.error(f"⚠️ Tarvitset {abs(target_data['savings_gap']):.0f}€/kk lisää saavuttaaksesi tavoitteen!")
    else:
        st.success(f"🎉 Olet {abs(target_data['savings_gap']):.0f}€/kk edellä tavoitetta!")

def display_risk_assessment(risk_data: Dict):
    """Näytä riskiarvio"""
    st.subheader("⚠️ Riskiarvio")
    
    risk_score = risk_data['risk_score']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Riskimittari (%)"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 80], 'color': "orange"},
                {'range': [80, 100], 'color': "red"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 85}
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def display_watchdog_communication(communication: Dict):
    """Näytä Watchdog-kommunikaatio"""
    st.subheader("🤖 Sentinel Watchdog™ Viesti")
    
    comm_data = communication['communication']
    mood = comm_data['mood']
    message = comm_data['message']
    daily_action = comm_data['daily_action']
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 20px; color: white; margin: 15px 0;">
        <div style="font-size: 2rem; text-align: center; margin-bottom: 10px;">{mood}</div>
        <div style="font-size: 1.1rem; line-height: 1.6; text-align: center;">{message}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #f8f9fa; border-left: 4px solid #007bff; border-radius: 5px; padding: 15px; margin: 15px 0;">
        <strong>📋 Tänään teet:</strong><br>{daily_action}
    </div>
    """, unsafe_allow_html=True)
    
    if 'action_plan' in comm_data:
        st.markdown("**🎯 Toimintasuunnitelma:**")
        for action in comm_data['action_plan']:
            st.markdown(f"- {action}")

def display_survival_suggestions(suggestions: Dict):
    """Näytä Goal Survival Engine ehdotukset"""
    st.subheader("🔍 Goal Survival Engine - Ehdotukset")
    
    if 'suggestions' not in suggestions or not suggestions['suggestions']:
        st.info("Ei ehdotuksia tällä hetkellä.")
        return
    
    income_suggestions = [s for s in suggestions['suggestions'] if s['type'] == 'income_increase']
    expense_suggestions = [s for s in suggestions['suggestions'] if s['type'] == 'expense_reduction']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Lisätulo-ehdotukset")
        for suggestion in income_suggestions:
            with st.expander(f"💼 {suggestion['category']} (+{suggestion['potential_income']}€/kk)"):
                st.markdown(f"**Arvioitu lisätulo:** {suggestion['potential_income']}€/kk")
                st.markdown(f"**Kiireellisyys:** {suggestion['urgency'].upper()}")
                st.markdown("**Toimenpiteet:**")
                for action in suggestion['actions']:
                    st.markdown(f"- {action}")
    
    with col2:
        st.markdown("### ✂️ Kulusäästö-ehdotukset")
        for suggestion in expense_suggestions:
            with st.expander(f"💸 {suggestion['category']} (-{suggestion['potential_savings']:.0f}€/kk)"):
                st.markdown(f"**Nykyinen kulutus:** {suggestion['current_spend']:.0f}€/kk")
                st.markdown(f"**Säästöpotentiaali:** {suggestion['potential_savings']:.0f}€/kk")
                st.markdown(f"**Kiireellisyys:** {suggestion['urgency'].upper()}")
                st.markdown("**Toimenpiteet:**")
                for action in suggestion['actions']:
                    st.markdown(f"- {action}")

def display_emergency_protocol(protocol: Dict):
    """Näytä hätätila-protokolla"""
    if protocol['status'] == 'not_required':
        st.success(f"✅ Hätätila-protokolla ei ole tarpeen (Tila: {protocol['current_mode']})")
        return
    
    st.error("🚨 **HÄTÄTILA-PROTOKOLLA AKTIVOITU**")
    
    emergency_data = protocol['emergency_protocol']
    
    st.markdown("### ⚫ Välittömät rajoitukset")
    lockdown = emergency_data['immediate_lockdown']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔒 Lukitut kategoriat:**")
        for category in lockdown['budget_categories_locked']:
            st.markdown(f"- {category}")
    
    with col2:
        st.markdown("**💳 Kulutusrajat:**")
        for limit_type, amount in lockdown['spending_limits'].items():
            st.markdown(f"- {limit_type}: {amount}€")
    
    st.markdown("### 🚨 Pakolliset toimenpiteet")
    
    for action in emergency_data['mandatory_actions']:
        priority = action['priority']
        action_name = action['action']
        deadline = action['deadline']
        target = action.get('target', 'Ei määritelty')
        
        st.markdown(f"""
        <div style="background: {'#ff4444' if priority == 1 else '#ff8800'}; color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <strong>Prioriteetti {priority}: {action_name}</strong><br>
            📅 Deadline: {deadline}<br>🎯 Tavoite: {target}
        </div>
        """, unsafe_allow_html=True)
        
        if 'methods' in action:
            st.markdown("**Menetelmät:**")
            for method in action['methods']:
                st.markdown(f"- {method}")

def show_guardian_page():
    """
    Sentinel Guardian™ - Kehittynyt älykkäinen valvonta ja oppiminen
    6 välilehteä: Analyysi, Kommunikaatio, Ehdotukset, Hätätila, Oppiminen, Tiedot
    """
    
    st.title("🛡️ Sentinel Guardian™")
    st.markdown("**Älykkäin talousvalvoja - Oppiva AI-kumppani kohti 100k€ tavoitetta**")
    
    # Tarkista API-yhteys
    if not check_api_connection():
        st.error("⚠️ Yhteysvirhe API:in. Tarkista että backend on käynnissä.")
        return
    
    # Luo 6 välilehteä
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Tilanne-analyysi", 
        "💬 Kommunikaatio", 
        "💡 Ehdotukset", 
        "🚨 Hätätila", 
        "🧠 Oppiminen",
        "ℹ️ Tiedot"
    ])
    
    with tab1:
        show_situation_analysis()
    
    with tab2:
        show_communication()
    
    with tab3:
        show_suggestions()
    
    with tab4:
        show_emergency_protocol()
    
    with tab5:
        show_learning_dashboard()
    
    with tab6:
        show_information()

def check_api_connection() -> bool:
    """Tarkista API-yhteys"""
    try:
        if 'access_token' not in st.session_state:
            st.warning("Kirjaudu sisään käyttääksesi Guardian-ominaisuuksia")
            return False
        
        response = requests.get(
            "http://localhost:8000/guardian/health-check",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.status_code == 200
    except:
        return False

def show_situation_analysis():
    """Tilanne-analyysi välilehti"""
    st.header("📊 Tilanne-analyysi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Tavoiteanalyysi")
        
        # Hae tavoiteanalyysi
        goal_analysis = get_goal_analysis()
        if goal_analysis and goal_analysis.get('status') == 'success':
            analysis = goal_analysis['goal_analysis']
            
            # Näytä nykyinen tilanne
            current_savings = analysis.get('current_savings', 0)
            target = 100000
            progress = (current_savings / target) * 100
            
            st.metric(
                "Nykyiset säästöt", 
                f"{current_savings:,.0f} €",
                f"{progress:.1f}% tavoitteesta"
            )
            
            # Ennuste
            months_to_goal = analysis.get('months_to_goal')
            if months_to_goal:
                st.metric(
                    "Arvioitu aika tavoitteeseen",
                    f"{months_to_goal:.0f} kuukautta",
                    f"Trendi: {analysis.get('monthly_trend', 0):+.0f} €/kk"
                )
            
            # Onnistumistodennäköisyys
            success_prob = analysis.get('success_probability', 0)
            prob_color = "green" if success_prob > 0.7 else "orange" if success_prob > 0.4 else "red"
            st.markdown(f"**Onnistumistodennäköisyys:** :{prob_color}[{success_prob:.1%}]")
            
            # Suositus
            if 'recommendation' in analysis:
                st.info(f"💡 **Suositus:** {analysis['recommendation']}")
        else:
            st.info("Ei riittävästi dataa tavoiteanalyysiin")
    
    with col2:
        st.subheader("⚠️ Riski-analyysi")
        
        # Hae Watchdog-status
        status_data = get_watchdog_status()
        if status_data and status_data.get('status') == 'success':
            situation = status_data['situation_room']
            
            # Riskimittari
            risk_score = situation.get('risk_score', 0)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = risk_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Riskitaso"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgreen"},
                        {'range': [25, 50], 'color': "yellow"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 85
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Watchdog-tila
            mode = situation.get('current_mode', 'passive')
            mode_emoji = {"passive": "🟢", "active": "🟡", "aggressive": "🔴", "emergency": "⚫"}
            st.markdown(f"**Watchdog-tila:** {mode_emoji.get(mode, '❓')} {mode.upper()}")
            
            # Riskitekijät
            risk_factors = situation.get('risk_factors', {})
            if risk_factors:
                st.markdown("**Riskitekijät:**")
                for factor, value in risk_factors.items():
                    st.text(f"• {factor}: {value:.1f}%")
        else:
            st.error("Virhe riski-analyysin haussa")

def show_communication():
    """Kommunikaatio välilehti"""
    st.header("💬 Sentinel Kommunikaatio")
    
    # Hae kommunikaatio
    comm_data = get_watchdog_communication()
    if comm_data and comm_data.get('status') == 'success':
        communication = comm_data['communication']
        
        # Päivän viesti
        st.subheader("📢 Päivän viesti")
        mood = communication.get('mood', 'neutral')
        mood_colors = {
            'encouraging': 'green',
            'concerned': 'orange', 
            'urgent': 'red',
            'neutral': 'blue'
        }
        
        st.markdown(f":{mood_colors.get(mood, 'blue')}[{communication.get('message', 'Ei viestiä')}]")
        
        # Päivän toimenpiteet
        st.subheader("✅ Päivän toimenpiteet")
        daily_actions = communication.get('daily_actions', [])
        for i, action in enumerate(daily_actions, 1):
            st.checkbox(f"{i}. {action}", key=f"action_{i}")
        
        # Optimaalinen kommunikaatioaika
        st.subheader("⏰ Optimaalinen kommunikaatioaika")
        timing_data = get_optimal_timing()
        if timing_data and timing_data.get('status') == 'success':
            timing = timing_data['optimal_timing']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Paras tunti", f"{timing.get('best_hour', 18)}:00")
            with col2:
                weekdays = ['Ma', 'Ti', 'Ke', 'To', 'Pe', 'La', 'Su']
                best_day = timing.get('best_weekday', 1)
                st.metric("Paras päivä", weekdays[best_day] if best_day < 7 else 'Ti')
            with col3:
                st.metric("Tiheys", timing.get('frequency', 'weekly'))
            
            st.info(f"💡 **Tyyli:** {timing.get('preferred_style', 'balanced').title()}")
    else:
        st.error("Virhe kommunikaation haussa")

def show_suggestions():
    """Ehdotukset välilehti"""
    st.header("💡 Älykkäät ehdotukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Personoidut ehdotukset")
        
        # Hae personoidut ehdotukset
        suggestions_data = get_personalized_suggestions()
        if suggestions_data and suggestions_data.get('status') == 'success':
            suggestions = suggestions_data['suggestions']
            
            for i, suggestion in enumerate(suggestions):
                with st.expander(f"💡 {suggestion.get('category', 'Ehdotus')} (Tehokkuus: {suggestion.get('effectiveness_score', 0):.1%})"):
                    st.write(suggestion.get('message', ''))
                    
                    # Toimenpiteet
                    actions = suggestion.get('actions', [])
                    if actions:
                        st.markdown("**Toimenpiteet:**")
                        for action in actions:
                            st.write(f"• {action}")
                    
                    # Palautenappit
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("👍 Hyväksy", key=f"accept_{i}"):
                            submit_feedback(f"suggestion_{i}", "accepted", 0.8)
                            st.success("Palaute lähetetty!")
                    with col_b:
                        if st.button("👎 Hylkää", key=f"reject_{i}"):
                            submit_feedback(f"suggestion_{i}", "rejected", 0.2)
                            st.info("Palaute lähetetty!")
                    with col_c:
                        if st.button("⚖️ Osittain", key=f"partial_{i}"):
                            submit_feedback(f"suggestion_{i}", "partially_followed", 0.5)
                            st.info("Palaute lähetetty!")
        else:
            st.info("Ei personoituja ehdotuksia saatavilla")
    
    with col2:
        st.subheader("📈 Kulutusennusteet")
        
        # Ennusteet
        days_ahead = st.slider("Ennusta päiviä eteenpäin", 1, 30, 7)
        
        if st.button("🔮 Luo ennuste"):
            with st.spinner("Analysoidaan kulutuskuvioita..."):
                predictions_data = get_spending_predictions(days_ahead)
                
                if predictions_data and predictions_data.get('status') == 'success':
                    predictions = predictions_data['predictions']
                    
                    if predictions.get('status') == 'success':
                        # Näytä ennusteet
                        pred_values = predictions['predictions']
                        dates = [datetime.now() + timedelta(days=i+1) for i in range(len(pred_values))]
                        
                        fig = px.line(
                            x=dates, 
                            y=pred_values,
                            title=f"Kulutusennuste {days_ahead} päivälle",
                            labels={'x': 'Päivämäärä', 'y': 'Ennustettu kulutus (€)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tilastot
                        st.metric("Kokonaisennuste", f"{predictions['total_predicted']:.0f} €")
                        st.metric("Päivittäinen keskiarvo", f"{predictions['daily_average']:.0f} €")
                        st.metric("Mallin tarkkuus", f"{predictions.get('model_accuracy', 0):.1%}")
                    else:
                        st.warning(predictions.get('message', 'Ei riittävästi dataa ennustamiseen'))
                else:
                    st.error("Virhe ennusteiden haussa")

def show_emergency_protocol():
    """Hätätila välilehti"""
    st.header("🚨 Hätätila-protokolla")
    
    # Hae hätätila-tiedot
    emergency_data = get_emergency_protocol()
    if emergency_data and emergency_data.get('status') == 'success':
        protocol = emergency_data['emergency_protocol']
        
        if protocol.get('is_active', False):
            st.error("🚨 **HÄTÄTILA AKTIIVINEN!**")
            
            # Lukitut kategoriat
            st.subheader("🔒 Lukitut kategoriat")
            locked_categories = protocol.get('locked_categories', [])
            for category in locked_categories:
                st.markdown(f"❌ {category}")
            
            # Kulurajat
            st.subheader("💰 Kulurajat")
            limits = protocol.get('spending_limits', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Päiväraja", f"{limits.get('daily', 0)} €")
            with col2:
                st.metric("Viikkoraja", f"{limits.get('weekly', 0)} €")
            with col3:
                st.metric("Kuukausiraja", f"{limits.get('monthly', 0)} €")
            
            # Pakolliset toimenpiteet
            st.subheader("⚡ Pakolliset toimenpiteet")
            mandatory_actions = protocol.get('mandatory_actions', [])
            for action in mandatory_actions:
                st.markdown(f"• **{action}**")
            
            # Hätätilan lopetus
            if st.button("🔓 Lopeta hätätila", type="primary"):
                st.warning("Ota yhteyttä tukeen hätätilan lopettamiseksi")
        else:
            st.success("✅ Hätätila ei ole aktiivinen")
            st.info("Hätätila aktivoituu automaattisesti kun riskitaso ylittää 85%")
    else:
        st.error("Virhe hätätila-tietojen haussa")
    
    # Anomaliat
    st.subheader("🔍 Epätavalliset kulutukset")
    anomalies_data = get_anomalies()
    if anomalies_data and anomalies_data.get('status') == 'success':
        anomalies = anomalies_data['anomalies']
        
        if anomalies:
            st.warning(f"Löytyi {len(anomalies)} epätavallista kulutusta:")
            
            for anomaly in anomalies:
                with st.expander(f"⚠️ {anomaly.get('amount', 0):.2f} € - {anomaly.get('description', 'Tuntematon')}"):
                    st.write(f"**Päivämäärä:** {anomaly.get('date', '')}")
                    st.write(f"**Syy:** {anomaly.get('anomaly_reason', '')}")
        else:
            st.success("Ei epätavallisia kulutuksia havaittu")
    else:
        st.error("Virhe anomalioiden haussa")

def show_learning_dashboard():
    """Oppiminen välilehti - Kehittynyt AI-oppiminen"""
    st.header("🧠 Sentinel Oppimismoottori™")
    st.markdown("*Älykkäin talous-AI joka oppii sinusta ja mukautuu käyttäytymiseesi*")
    
    # Oppimisen oivallukset
    st.subheader("📊 Oppimisstatistiikka")
    insights_data = get_learning_insights()
    if insights_data and insights_data.get('status') == 'success':
        insights = insights_data['learning_insights']
        
        if insights.get('status') != 'no_data':
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🔄 Vuorovaikutukset", insights.get('total_interactions', 0))
            with col2:
                success_rate = insights.get('success_rate', 0)
                st.metric("✅ Onnistumisprosentti", f"{success_rate:.1%}")
            with col3:
                comm_style = insights.get('preferred_communication', 'balanced').title()
                st.metric("💬 Kommunikaatiotyyli", comm_style)
            with col4:
                sentinel_iq = insights_data.get('sentinel_iq', 'Aloittelija')
                iq_color = "🎓" if sentinel_iq == "Kehittyvä" else "🌱"
                st.metric("🧠 Sentinel IQ", f"{iq_color} {sentinel_iq}")
            
            # Tehokkaimmat ehdotukset
            st.subheader("🏆 Tehokkaimmat ehdotustyypit")
            effective_suggestions = insights.get('most_effective_suggestions', {})
            if effective_suggestions:
                df = pd.DataFrame(list(effective_suggestions.items()), columns=['Ehdotustyyppi', 'Tehokkuus'])
                df['Tehokkuus'] = (df['Tehokkuus'] * 100).round(1)
                df = df.sort_values('Tehokkuus', ascending=True)
                
                fig = px.bar(df, x='Tehokkuus', y='Ehdotustyyppi', orientation='h',
                           title="Ehdotusten tehokkuus (%)", color='Tehokkuus',
                           color_continuous_scale='RdYlGn')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Oppimisen taso
            learning_progress = insights.get('learning_progress', {})
            if learning_progress.get('advanced'):
                st.success("🎓 **Edistynyt taso** - Sentinel tuntee sinut hyvin ja osaa ennakoida tarpeesi!")
            elif learning_progress.get('intermediate'):
                st.info("📚 **Keskitaso** - Sentinel oppii sinusta lisää ja mukautuu käyttäytymiseesi")
            else:
                st.warning("🌱 **Aloittelija** - Anna Sentinelille aikaa oppia! Käytä ehdotuksia ja anna palautetta.")
        else:
            st.info("🚀 Ei oppimisdataa vielä saatavilla. Aloita käyttämällä ehdotuksia ja antamalla palautetta!")
    
    # ML-ennusteet ja analytiikka
    st.subheader("🔮 Älykkäät ennusteet")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Kulutusennusteet**")
        days_ahead = st.slider("Ennusta päiviä eteenpäin", 1, 30, 7, key="pred_days")
        
        if st.button("🔮 Luo ennuste", key="create_prediction"):
            with st.spinner("🤖 Analysoidaan kulutuskuvioita ML:llä..."):
                predictions_data = get_spending_predictions(days_ahead)
                
                if predictions_data and predictions_data.get('status') == 'success':
                    predictions = predictions_data['predictions']
                    
                    if predictions.get('status') == 'success':
                        # Näytä ennusteet
                        pred_values = predictions['predictions']
                        dates = [datetime.now() + timedelta(days=i+1) for i in range(len(pred_values))]
                        
                        fig = px.line(
                            x=dates, 
                            y=pred_values,
                            title=f"🔮 AI-kulutusennuste {days_ahead} päivälle",
                            labels={'x': 'Päivämäärä', 'y': 'Ennustettu kulutus (€)'}
                        )
                        fig.update_traces(line=dict(color='#FF6B6B', width=3))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tilastot
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("💰 Kokonaisennuste", f"{predictions['total_predicted']:.0f} €")
                        with col_b:
                            st.metric("📊 Päivittäinen keskiarvo", f"{predictions['daily_average']:.0f} €")
                        with col_c:
                            accuracy = predictions.get('model_accuracy', 0)
                            st.metric("🎯 Mallin tarkkuus", f"{accuracy:.1%}")
                    else:
                        st.warning(f"⚠️ {predictions.get('message', 'Ei riittävästi dataa ennustamiseen')}")
                else:
                    st.error("❌ Virhe ennusteiden haussa")
    
    with col2:
        st.markdown("**🚨 Anomalioiden tunnistus**")
        if st.button("🔍 Tunnista anomaliat", key="detect_anomalies"):
            with st.spinner("🤖 Analysoidaan epätavallisia kulutuskuvioita..."):
                anomalies_data = get_anomalies()
                
                if anomalies_data and anomalies_data.get('status') == 'success':
                    anomalies = anomalies_data['anomalies']
                    
                    if anomalies:
                        st.warning(f"⚠️ Löytyi {len(anomalies)} epätavallista kulutusta:")
                        
                        for i, anomaly in enumerate(anomalies):
                            with st.expander(f"🚨 {anomaly.get('amount', 0):.2f} € - {anomaly.get('description', 'Tuntematon')[:30]}..."):
                                st.write(f"**📅 Päivämäärä:** {anomaly.get('date', '')}")
                                st.write(f"**💡 Syy:** {anomaly.get('anomaly_reason', '')}")
                                st.write(f"**🆔 Transaktio ID:** {anomaly.get('id', 'N/A')}")
                    else:
                        st.success("✅ Ei epätavallisia kulutuksia havaittu viimeisen 30 päivän aikana!")
                else:
                    st.error("❌ Virhe anomalioiden tunnistuksessa")
    
    # Tavoiteanalyysi ML:llä
    st.subheader("🎯 Älykkäs tavoiteanalyysi")
    goal_analysis = get_goal_analysis()
    if goal_analysis and goal_analysis.get('status') == 'success':
        analysis = goal_analysis['goal_analysis']
        
        if analysis.get('status') != 'insufficient_data':
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_savings = analysis.get('current_savings', 0)
                st.metric("💰 Nykyiset säästöt", f"{current_savings:,.0f} €")
            
            with col2:
                months_to_goal = analysis.get('months_to_goal')
                if months_to_goal and months_to_goal != float('inf'):
                    st.metric("📅 Kuukausia tavoitteeseen", f"{months_to_goal:.0f}")
                else:
                    st.metric("📅 Kuukausia tavoitteeseen", "∞")
            
            with col3:
                success_prob = analysis.get('success_probability', 0)
                prob_color = "success" if success_prob > 0.7 else "warning" if success_prob > 0.4 else "error"
                st.metric("📊 Onnistumistodennäköisyys", f"{success_prob:.1%}")
            
            # Suositus
            if 'recommendation' in analysis:
                if success_prob > 0.7:
                    st.success(f"🎉 **AI-suositus:** {analysis['recommendation']}")
                elif success_prob > 0.4:
                    st.warning(f"⚠️ **AI-suositus:** {analysis['recommendation']}")
                else:
                    st.error(f"🚨 **AI-suositus:** {analysis['recommendation']}")
        else:
            st.info("📊 Kerää enemmän dataa tarkempaa tavoiteanalyysiä varten")
    
    # Oppimisen hallinta
    st.subheader("⚙️ Oppimisen hallinta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Vie oppimisdata", key="export_learning"):
            with st.spinner("📦 Pakataan oppimisdataa..."):
                export_data = export_learning_data()
                if export_data:
                    st.download_button(
                        "💾 Lataa Sentinel-oppimisdata",
                        json.dumps(export_data, indent=2, ensure_ascii=False),
                        "sentinel_learning_data.json",
                        "application/json",
                        key="download_learning"
                    )
                    st.success("✅ Oppimisdata valmis lataukseen!")
                else:
                    st.error("❌ Virhe oppimisdatan viennissä")
    
    with col2:
        uploaded_file = st.file_uploader("📥 Tuo oppimisdata", type="json", key="import_file")
        if uploaded_file and st.button("📥 Tuo data", key="import_learning"):
            try:
                import_data = json.load(uploaded_file)
                with st.spinner("🔄 Tuodaan oppimisdataa..."):
                    result = import_learning_data(import_data)
                    if result and result.get('status') == 'success':
                        st.success("✅ Oppimisdata tuotu onnistuneesti! Sentinel jatkaa siitä mihin jäi.")
                    else:
                        st.error("❌ Virhe oppimisdatan tuonnissa")
            except Exception as e:
                st.error(f"❌ Virhe datan käsittelyssä: {e}")
    
    with col3:
        if st.button("🔄 Nollaa oppiminen", type="secondary", key="reset_learning"):
            st.warning("⚠️ Tämä poistaa kaiken oppimisdatan!")
            if st.button("⚠️ Vahvista nollaus", key="confirm_reset"):
                with st.spinner("🔄 Nollataan Sentinel..."):
                    result = reset_learning()
                    if result and result.get('status') == 'success':
                        st.success("✅ Oppiminen nollattu! Sentinel aloittaa alusta.")
                        st.rerun()
                    else:
                        st.error("❌ Virhe oppimisen nollauksessa")
    
    # Optimaalinen kommunikaatioaika
    st.subheader("⏰ Optimaalinen kommunikaatioaika")
    timing_data = get_optimal_timing()
    if timing_data and timing_data.get('status') == 'success':
        timing = timing_data['optimal_timing']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            best_hour = timing.get('best_hour', 18)
            st.metric("🕐 Paras tunti", f"{best_hour}:00")
        with col2:
            weekdays = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
            best_day = timing.get('best_weekday', 1)
            day_name = weekdays[best_day] if best_day < 7 else 'Tiistai'
            st.metric("📅 Paras päivä", day_name)
        with col3:
            frequency = timing.get('frequency', 'weekly')
            freq_emoji = "📅" if frequency == "daily" else "📆"
            st.metric("🔄 Tiheys", f"{freq_emoji} {frequency}")
        with col4:
            style = timing.get('preferred_style', 'balanced')
            style_emoji = {"gentle": "😊", "balanced": "⚖️", "firm": "💪", "aggressive": "🔥"}
            st.metric("💬 Tyyli", f"{style_emoji.get(style, '⚖️')} {style}")
        
        st.info(f"💡 **AI-suositus:** Sentinel kommunikoi kanssasi tehokkaimmin {day_name.lower()}isin klo {best_hour}:00 käyttäen {style}-tyyliä.")
    else:
        st.info("⏰ Kerää enemmän dataa optimaalisen kommunikaatioajan määrittämiseksi")

def show_information():
    """Tiedot välilehti"""
    st.header("ℹ️ Sentinel Guardian™ Tiedot")
    
    # Järjestelmätiedot
    st.subheader("🔧 Järjestelmätiedot")
    
    # Guardian health check
    health_data = get_guardian_health()
    if health_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                "Guardian Status": health_data.get('status', 'unknown'),
                "Versio": health_data.get('version', '1.0.0'),
                "Ominaisuudet": len(health_data.get('capabilities', []))
            })
        
        with col2:
            # Learning engine health
            learning_health = get_learning_health()
            if learning_health:
                st.json({
                    "Learning Status": learning_health.get('status', 'unknown'),
                    "Aktiivisia käyttäjiä": learning_health.get('active_learning_users', 0),
                    "Oppimisinteraktiot": learning_health.get('total_learning_interactions', 0)
                })
    
    # Ominaisuudet
    st.subheader("🚀 Ominaisuudet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🛡️ Watchdog-valvonta:**
        - 4 toimintatilaa (Passiivinen → Hätätila)
        - Reaaliaikainen riskianalyysi
        - Automaattiset hälytykset
        - Budjettilukitukset
        
        **💡 Älykkäät ehdotukset:**
        - Goal Survival Engine
        - Kategoria-spesifiset toimenpiteet
        - Personoitu kommunikaatio
        - Tehokkuuden seuranta
        """)
    
    with col2:
        st.markdown("""
        **🧠 Oppimismoottori:**
        - Kulutuskuvioiden tunnistus
        - ML-pohjaiset ennusteet
        - Anomalioiden havaitseminen
        - Käyttäytymisen mukautuminen
        
        **📊 Analytiikka:**
        - Tavoitteen edistymisanalyysi
        - Onnistumistodennäköisyys
        - Optimaalinen kommunikaatioaika
        - Personoidut oivallukset
        """)
    
    # Käyttöohje
    st.subheader("📖 Käyttöohje")
    
    with st.expander("🔰 Aloittelijalle"):
        st.markdown("""
        1. **Aloita** lisäämällä transaktioita järjestelmään
        2. **Seuraa** Watchdog-tilaa ja riskimittaria
        3. **Reagoi** ehdotuksiin ja anna palautetta
        4. **Anna** Sentinelin oppia käyttäytymisestäsi
        5. **Hyödynnä** ennusteita ja analytiikkaa
        """)
    
    with st.expander("🎯 Edistyneelle"):
        st.markdown("""
        - **Vie/tuo** oppimisdata laitteiden välillä
        - **Mukautat** kommunikaatiotyyliä palautteen avulla
        - **Seuraat** anomalioita ja epätavallisia kulutuksia
        - **Hyödynnät** ML-ennusteita budjetoinnissa
        - **Optimoit** tavoitteen saavuttamista analytiikan avulla
        """)

# API-kutsut

def get_watchdog_status():
    """Hae Watchdog-status"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/status",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_watchdog_communication():
    """Hae Watchdog-kommunikaatio"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/communication",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_emergency_protocol():
    """Hae hätätila-protokolla"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/emergency-protocol",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_guardian_health():
    """Hae Guardian-terveystarkistus"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/health-check",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Uudet oppimismoottori API-kutsut

def get_personalized_suggestions():
    """Hae personoidut ehdotukset"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/suggestions",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_spending_predictions(days_ahead: int):
    """Hae kulutusennusteet"""
    try:
        response = requests.get(
            f"http://localhost:8000/guardian/learning/predictions/{days_ahead}",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_anomalies():
    """Hae anomaliat"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/anomalies",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_optimal_timing():
    """Hae optimaalinen kommunikaatioaika"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/communication-timing",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_goal_analysis():
    """Hae tavoiteanalyysi"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/goal-analysis",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_learning_insights():
    """Hae oppimisen oivallukset"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/insights",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_learning_health():
    """Hae oppimismoottorin terveystarkistus"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/health-check",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def submit_feedback(suggestion_id: str, response_type: str, effectiveness: float):
    """Lähetä palaute ehdotuksesta"""
    try:
        response = requests.post(
            "http://localhost:8000/guardian/learning/feedback",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json={
                "suggestion_id": suggestion_id,
                "response_type": response_type,
                "effectiveness": effectiveness
            }
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def export_learning_data():
    """Vie oppimisdata"""
    try:
        response = requests.get(
            "http://localhost:8000/guardian/learning/export",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json().get('learning_data') if response.status_code == 200 else None
    except:
        return None

def import_learning_data(data: Dict):
    """Tuo oppimisdata"""
    try:
        response = requests.post(
            "http://localhost:8000/guardian/learning/import",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json=data
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def reset_learning():
    """Nollaa oppiminen"""
    try:
        response = requests.post(
            "http://localhost:8000/guardian/learning/reset",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

# Pääfunktio yhteensopivuutta varten
def main():
    """Pääfunktio kun ajetaan suoraan"""
    # Mock API-objekti testausta varten
    class MockAPI:
        def __init__(self):
            self.base_url = "http://localhost:8000"
        def request(self, method, endpoint, **kwargs):
            return {"status": "error", "message": "Mock API - käynnistä oikea API"}
    
    show_guardian_page(MockAPI())

if __name__ == "__main__":
    main() 