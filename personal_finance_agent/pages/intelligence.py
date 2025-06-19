import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

def show_intelligence_page():
    """
    Advanced Intelligence™ - Kattava älykkyyden dashboard
    4 välilehteä: Tulot, Velat, Ideat, Yhteenveto
    """
    
    st.title("🧠 Advanced Intelligence™")
    st.markdown("**Kattava taloudellinen älykkyys - Optimoi tulot, velat ja ansaintaideat**")
    
    # Tarkista API-yhteys
    if not check_api_connection():
        st.error("⚠️ Yhteysvirhe API:in. Tarkista että backend on käynnissä.")
        return
    
    # Luo 4 välilehteä
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Tulojen älykkyys", 
        "💳 Velkakäyttäytyminen", 
        "💡 Idea Engine", 
        "📊 Yhteenveto"
    ])
    
    with tab1:
        show_income_intelligence()
    
    with tab2:
        show_liabilities_insight()
    
    with tab3:
        show_idea_engine()
    
    with tab4:
        show_comprehensive_summary()

def check_api_connection() -> bool:
    """Tarkista API-yhteys"""
    try:
        if 'access_token' not in st.session_state:
            st.warning("Kirjaudu sisään käyttääksesi Intelligence-ominaisuuksia")
            return False
        
        response = requests.get(
            "http://localhost:8000/api/v1/status",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.status_code == 200
    except:
        return False

def show_income_intelligence():
    """Tulojen älykkyys välilehti"""
    st.header("💰 Income Stream Intelligence™")
    
    # Hae tuloanalyysi
    income_data = get_income_analysis()
    if income_data and income_data.get('status') == 'success':
        analysis = income_data['income_analysis']
        
        if analysis.get('status') == 'success':
            # Tulojen terveys
            st.subheader("🏥 Tulojen terveys")
            health_data = analysis['analysis']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                health_score = health_data.get('health_score', 0)
                st.metric("Terveyspistemäärä", f"{health_score:.1%}")
            with col2:
                monthly_income = health_data.get('monthly_income_estimate', 0)
                st.metric("Kuukausitulo", f"{monthly_income:.0f} €")
            with col3:
                diversity = health_data.get('income_diversity', 0)
                st.metric("Diversifikaatio", f"{diversity:.1%}")
            with col4:
                reliability = health_data.get('average_reliability', 0)
                st.metric("Luotettavuus", f"{reliability:.1%}")
            
            # Tulovirrat
            st.subheader("🌊 Tulovirrat")
            streams = analysis.get('income_streams', [])
            if streams:
                df = pd.DataFrame(streams)
                
                # Näytä tulovirrat
                fig = px.bar(df, x='source', y='average_amount', 
                           title="Tulovirrat ja niiden keskiarvot",
                           color='reliability',
                           color_discrete_map={'high': 'green', 'medium': 'orange', 'low': 'red'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Tulovirran yksityiskohdat
                for stream in streams:
                    with st.expander(f"💼 {stream['source']} ({stream['category']})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Keskiarvo", f"{stream['average_amount']:.0f} €")
                        with col2:
                            st.metric("Luotettavuus", stream['reliability'].title())
                        with col3:
                            st.metric("Trendi", f"{stream['trend']:+.0f} €/kk")
                        
                        # Volatiliteetti
                        volatility = stream.get('volatility', 0)
                        if volatility > 0.5:
                            st.warning(f"⚠️ Korkea volatiliteetti: {volatility:.1%}")
                        elif volatility < 0.2:
                            st.success(f"✅ Vakaa tulovirta: {volatility:.1%}")
            
            # Ehdotukset
            st.subheader("💡 Tulonlisäysehdotukset")
            suggestions = health_data.get('income_suggestions', [])
            if suggestions:
                for suggestion in suggestions:
                    with st.expander(f"🎯 {suggestion.get('category', 'Ehdotus').title()} ({suggestion.get('priority', 'medium')})"):
                        if suggestion.get('type') == 'new_income_stream':
                            st.write(f"**Tyyppi:** Uusi tulovirta")
                            st.write(f"**Hankaluus:** {suggestion.get('difficulty', 'medium')}")
                            st.write(f"**Aikasijoitus:** {suggestion.get('time_investment', '5-10h/viikko')}")
                            
                            estimated = suggestion.get('estimated_monthly', {})
                            st.write(f"**Tuottopotentiaali:** {estimated.get('min', 0)}-{estimated.get('max', 0)}€/kk")
                            
                            st.write("**Ehdotukset:**")
                            for idea in suggestion.get('suggestions', []):
                                st.write(f"• {idea}")
                        
                        elif suggestion.get('type') == 'optimize_existing':
                            st.write(f"**Tyyppi:** Optimointi")
                            st.write(f"**Ongelma:** {suggestion.get('issue', 'unknown')}")
                            st.write(f"**Lähde:** {suggestion.get('source', 'unknown')}")
                            
                            st.write("**Optimointiehdotukset:**")
                            for tip in suggestion.get('optimization_tips', []):
                                st.write(f"• {tip}")
            
            # Riskit
            st.subheader("⚠️ Riskit ja varoitukset")
            risks = health_data.get('risk_alerts', [])
            if risks:
                for risk in risks:
                    severity_color = "red" if risk.get('severity') == 'high' else "orange"
                    st.markdown(f":{severity_color}[**{risk.get('type', 'Risk').replace('_', ' ').title()}:** {risk.get('message', '')}]")
                    st.info(f"💡 **Suositus:** {risk.get('recommendation', '')}")
            else:
                st.success("✅ Ei merkittäviä riskejä havaittu")
        
        else:
            st.info(analysis.get('message', 'Ei tulotietoja'))
            # Näytä aloittajaehdotukset
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                st.subheader("🚀 Aloittajaehdotukset")
                for rec in recommendations:
                    with st.expander(f"💡 {rec.get('category', 'Ehdotus').title()}"):
                        st.write(rec.get('message', ''))
                        for suggestion in rec.get('suggestions', []):
                            st.write(f"• {suggestion}")
    
    # Päivittäinen mahdollisuus
    st.subheader("🌟 Päivittäinen tulonlisäysmahdollisuus")
    daily_opp = get_daily_income_opportunity()
    if daily_opp and daily_opp.get('status') == 'success':
        opp = daily_opp['daily_opportunity']
        
        st.markdown(f"**{opp.get('suggestion', 'Tuntematon')}**")
        st.write(f"**Kategoria:** {opp.get('category', 'unknown').title()}")
        st.write(f"**Aika:** {opp.get('estimated_time', '1-3h')}")
        st.write(f"**Tuotto:** {opp.get('potential_earning', '20-100€')}")
        
        st.info(f"💬 **{daily_opp.get('motivational_message', '')}**")
        
        st.write("**Toimenpiteet:**")
        for step in daily_opp.get('action_steps', []):
            st.write(f"• {step}")

def show_liabilities_insight():
    """Velkakäyttäytyminen välilehti"""
    st.header("💳 Liabilities Insight™")
    
    # Hae velka-analyysi
    liabilities_data = get_liabilities_analysis()
    if liabilities_data and liabilities_data.get('status') == 'success':
        analysis = liabilities_data['liabilities_analysis']
        
        if analysis.get('status') == 'success':
            # Velkatilanne
            st.subheader("📊 Velkatilanne")
            debt_analysis = analysis['debt_analysis']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_debt = debt_analysis.get('total_debt', 0)
                st.metric("Kokonaisvelka", f"{total_debt:,.0f} €")
            with col2:
                monthly_payments = debt_analysis.get('monthly_payments', 0)
                st.metric("Kuukausimaksut", f"{monthly_payments:.0f} €")
            with col3:
                annual_interest = debt_analysis.get('annual_interest_cost', 0)
                st.metric("Vuosikorkomenot", f"{annual_interest:.0f} €")
            with col4:
                debt_ratio = debt_analysis.get('debt_to_income_ratio', 0)
                st.metric("Velka-tulo-suhde", f"{debt_ratio:.1f}%")
            
            # Velkatilanteen status
            debt_status = debt_analysis.get('debt_status', 'manageable')
            status_colors = {
                'manageable': 'success',
                'moderate': 'info', 
                'concerning': 'warning',
                'critical': 'error'
            }
            st.markdown(f":{status_colors.get(debt_status, 'info')}[**Velkatilanne:** {debt_status.upper()}]")
            
            # Velat
            st.subheader("💳 Velat")
            liabilities = analysis.get('liabilities', [])
            if liabilities:
                df = pd.DataFrame(liabilities)
                
                # Velkojen jakauma
                fig = px.pie(df, values='principal_balance', names='name',
                           title="Velkojen jakauma")
                st.plotly_chart(fig, use_container_width=True)
                
                # Velkojen yksityiskohdat
                for liability in liabilities:
                    with st.expander(f"💳 {liability['name']} ({liability['type']})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Pääoma", f"{liability['principal_balance']:.0f} €")
                        with col2:
                            st.metric("Korko", f"{liability['interest_rate']:.1f}%")
                        with col3:
                            st.metric("Kuukausimaksu", f"{liability['monthly_payment']:.0f} €")
                        
                        # Maksusuunnitelma
                        if st.button(f"📊 Laske maksusuunnitelma", key=f"calc_{liability['name']}"):
                            extra_payment = st.number_input("Ylimaksu €/kk", value=0, key=f"extra_{liability['name']}")
                            
                            if st.button("Laske", key=f"calc_btn_{liability['name']}"):
                                payoff_data = calculate_debt_payoff(liability, extra_payment)
                                if payoff_data and payoff_data.get('status') == 'success':
                                    calc = payoff_data['payoff_calculation']
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Maksukuukaudet", calc.get('months_to_payoff', 0))
                                    with col2:
                                        st.metric("Kokonaiskorko", f"{calc.get('total_interest', 0):.0f} €")
                                    with col3:
                                        st.metric("Kokonaismaksu", f"{calc.get('total_amount_paid', 0):.0f} €")
            
            # Optimointisuunnitelma
            st.subheader("🎯 Optimointisuunnitelma")
            optimization = analysis.get('optimization_plan', {})
            if optimization.get('status') == 'success':
                strategies = optimization.get('optimization_strategies', [])
                
                for strategy in strategies:
                    priority_colors = {'high': 'red', 'medium': 'orange', 'low': 'blue'}
                    with st.expander(f"🎯 {strategy['name']} ({strategy.get('priority', 'medium')})"):
                        st.write(strategy.get('description', ''))
                        
                        if strategy.get('strategy') == 'avalanche_method':
                            st.write("**Kohdevelat:**")
                            for debt in strategy.get('target_debts', []):
                                st.write(f"• {debt}")
                            st.write(f"**Mahdolliset säästöt:** {strategy.get('potential_savings', 0):.0f} €")
                        
                        elif strategy.get('strategy') == 'snowball_method':
                            st.write("**Psykologinen hyöty:** Nopeat voitot motivoivat")
                            st.write("**Kohdevelat:**")
                            for debt in strategy.get('target_debts', []):
                                st.write(f"• {debt}")
            
            # Nettoedistymä
            st.subheader("📈 Nettoedistymä 100k€ tavoitteeseen")
            net_progress = analysis.get('net_progress_to_goal', {})
            if net_progress.get('status') != 'error':
                col1, col2, col3 = st.columns(3)
                with col1:
                    available = net_progress.get('available_for_goal', 0)
                    st.metric("Käytettävissä", f"{available:.0f} €/kk")
                with col2:
                    months = net_progress.get('months_to_goal')
                    if months and months != float('inf'):
                        st.metric("Kuukausia tavoitteeseen", f"{months:.0f}")
                    else:
                        st.metric("Kuukausia tavoitteeseen", "∞")
                with col3:
                    impact = net_progress.get('debt_impact_on_goal', {})
                    delay = impact.get('goal_delay_months', 0)
                    st.metric("Velkojen viive", f"{delay:.0f} kk")
                
                # Suositukset
                recommendations = net_progress.get('recommendations', [])
                if recommendations:
                    st.write("**Suositukset:**")
                    for rec in recommendations:
                        st.write(f"• {rec}")
        
        else:
            st.success("🎉 Velaton! Sinulla ei ole merkittäviä velkoja.")
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                st.write("**Suositukset velattomille:**")
                for rec in recommendations:
                    st.write(f"• {rec}")

def show_idea_engine():
    """Idea Engine välilehti"""
    st.header("💡 Idea Engine™")
    
    # Käyttäjäprofiili
    st.subheader("👤 Käyttäjäprofiili")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        skill_level = st.selectbox("Taitotaso", ["beginner", "intermediate", "advanced"], key="skill_level")
    with col2:
        available_time = st.slider("Käytettävissä tuntia/viikko", 1, 40, 10, key="available_time")
    with col3:
        preferred_categories = st.multiselect(
            "Suosikkikategoriat",
            ["freelance", "gig_economy", "selling", "passive_income", "quick_tasks"],
            default=["gig_economy", "selling"],
            key="preferred_categories"
        )
    
    user_profile = {
        "skill_level": skill_level,
        "available_time_hours": available_time,
        "preferred_categories": preferred_categories,
        "skills": ["Tietokoneen käyttö", "Sosiaalinen media", "Valokuvaus"]
    }
    
    # Hae päivittäiset ideat
    if st.button("🚀 Hae päivittäiset ideat"):
        with st.spinner("🤖 Generoidaan personoituja ideoita..."):
            ideas_data = get_daily_ideas(user_profile)
            
            if ideas_data and ideas_data.get('status') == 'success':
                ideas = ideas_data['daily_ideas']
                
                # Päivän teema
                st.subheader(f"🎯 {ideas.get('daily_theme', 'Daily Ideas').replace('_', ' ').title()}")
                
                # Motivoiva viesti
                st.info(f"💬 {ideas.get('motivational_message', '')}")
                
                # Erityistarjous
                special = ideas.get('special_opportunity', {})
                if special:
                    st.markdown(f"**🌟 {special.get('title', '')}**")
                    st.write(special.get('description', ''))
                    st.write(f"**Toimenpide:** {special.get('action', '')}")
                    st.write(f"**Tuottopotentiaali:** {special.get('potential_earning', '')}")
                    st.write(f"**Deadline:** {special.get('deadline', '')}")
                
                # Ideat
                st.subheader("💡 Personoidut ideat")
                idea_list = ideas.get('ideas', [])
                
                selected_ideas = []
                for i, idea in enumerate(idea_list):
                    with st.expander(f"💡 {idea.get('title', 'Idea')} ({idea.get('category', 'unknown').title()})"):
                        st.write(f"**Kuvaus:** {idea.get('description', '')}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tuotto", idea.get('estimated_earning', '0€'))
                        with col2:
                            st.metric("Aika", idea.get('time_needed', '0h'))
                        with col3:
                            st.metric("Hankaluus", idea.get('difficulty', 'medium').title())
                        
                        st.write("**Tarvittavat taidot:**")
                        for skill in idea.get('skills_needed', []):
                            st.write(f"• {skill}")
                        
                        st.write("**Alustat:**")
                        for platform in idea.get('platforms', []):
                            st.write(f"• {platform}")
                        
                        # Valitse idea
                        if st.checkbox(f"Valitse tämä idea", key=f"select_idea_{i}"):
                            selected_ideas.append(idea)
                
                # Toimintasuunnitelma
                if selected_ideas:
                    st.subheader("📋 Toimintasuunnitelma")
                    
                    # Käyttäjän aikataulu
                    st.write("**Aikataulu:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        available_days = st.slider("Käytettävissä päiviä", 1, 30, 7)
                    with col2:
                        daily_time_limit = st.slider("Tuntiraja/päivä", 1, 8, 3)
                    
                    user_schedule = {
                        "available_days": available_days,
                        "daily_time_limit": daily_time_limit
                    }
                    
                    if st.button("📅 Luo toimintasuunnitelma"):
                        with st.spinner("📋 Luodaan toimintasuunnitelmaa..."):
                            plan_data = create_action_plan(selected_ideas, user_schedule)
                            
                            if plan_data and plan_data.get('status') == 'success':
                                plan = plan_data['action_plan']
                                
                                st.success(f"✅ Toimintasuunnitelma luotu! {plan.get('total_ideas', 0)} ideaa, {plan.get('estimated_total_earning', 0):.0f}€ potentiaali")
                                
                                # Päivittäinen aikataulu
                                st.write("**Päivittäinen aikataulu:**")
                                for day in plan.get('daily_schedule', []):
                                    with st.expander(f"📅 Päivä {day.get('day', 0)} - {day.get('total_time', 0):.1f}h - {day.get('estimated_earning', 0):.0f}€"):
                                        for idea in day.get('ideas', []):
                                            st.write(f"• {idea.get('title', 'Idea')} ({idea.get('time_needed', '0h')})")
                                
                                # Käytännön vinkit
                                st.write("**💡 Käytännön vinkit:**")
                                for tip in plan.get('practical_tips', []):
                                    st.write(f"• {tip}")
                                
                                # Onnistumisen mittarit
                                metrics = plan.get('success_metrics', {})
                                st.write("**🎯 Onnistumisen mittarit:**")
                                st.write(f"• Tavoite: {metrics.get('target_earnings', 0):.0f}€")
                                st.write(f"• Minimihyvitys: {metrics.get('minimum_acceptable', 0):.0f}€")
                                st.write(f"• Erinomainen: {metrics.get('excellent_result', 0):.0f}€")
                                st.write(f"• Deadline: {metrics.get('completion_deadline', '')}")
                
                # Tilastot
                st.subheader("📊 Tilastot")
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_potential = ideas.get('total_potential_earning', 0)
                    st.metric("Kokonaispotentiaali", f"{total_potential:.0f} €")
                with col2:
                    estimated_time = ideas.get('estimated_time', '0h')
                    st.metric("Arvioitu aika", estimated_time)
                with col3:
                    idea_count = len(idea_list)
                    st.metric("Ideoita", idea_count)

def show_comprehensive_summary():
    """Yhteenveto välilehti"""
    st.header("📊 Comprehensive Intelligence Dashboard™")
    
    # Hae kattava dashboard
    dashboard_data = get_comprehensive_dashboard()
    if dashboard_data and dashboard_data.get('status') == 'success':
        # Taloudellinen terveys
        st.subheader("🏥 Taloudellinen terveys")
        health_score = dashboard_data.get('financial_health_score', 0)
        
        # Terveysmittari
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_score * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Taloudellinen terveys (%)"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 60], 'color': "orange"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Terveystaso
        if health_score > 0.8:
            st.success("🎉 Erinomainen taloudellinen terveys!")
        elif health_score > 0.6:
            st.info("✅ Hyvä taloudellinen terveys")
        elif health_score > 0.4:
            st.warning("⚠️ Kohtalainen taloudellinen terveys - parannuksia tarpeen")
        else:
            st.error("🚨 Huono taloudellinen terveys - välitöntä toimintaa tarpeen")
        
        # Suositukset
        st.subheader("💡 Kattavat suositukset")
        recommendations = dashboard_data.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        
        # Yksityiskohtaiset analyysit
        st.subheader("🔍 Yksityiskohtaiset analyysit")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tulojen analyysi
            income_data = dashboard_data.get('income_intelligence', {})
            if income_data.get('status') == 'success':
                st.markdown("**💰 Tulojen analyysi**")
                income_analysis = income_data.get('income_analysis', {})
                if income_analysis.get('status') == 'success':
                    analysis = income_analysis.get('analysis', {})
                    st.write(f"• Terveyspistemäärä: {analysis.get('health_score', 0):.1%}")
                    st.write(f"• Kuukausitulo: {analysis.get('monthly_income_estimate', 0):.0f}€")
                    st.write(f"• Tulovirrat: {income_analysis.get('total_streams', 0)}")
                else:
                    st.write("• Ei tulotietoja")
        
        with col2:
            # Velkojen analyysi
            liabilities_data = dashboard_data.get('liabilities_insight', {})
            if liabilities_data.get('status') == 'success':
                st.markdown("**💳 Velkojen analyysi**")
                liabilities_analysis = liabilities_data.get('liabilities_analysis', {})
                if liabilities_analysis.get('status') == 'success':
                    debt_analysis = liabilities_analysis.get('debt_analysis', {})
                    st.write(f"• Velkatilanne: {debt_analysis.get('debt_status', 'unknown')}")
                    st.write(f"• Kokonaisvelka: {debt_analysis.get('total_debt', 0):.0f}€")
                    st.write(f"• Kuukausimaksut: {debt_analysis.get('monthly_payments', 0):.0f}€")
                else:
                    st.write("• Ei velkoja")
        
        # Idea Engine
        idea_data = dashboard_data.get('idea_engine', {})
        if idea_data.get('status') == 'success':
            st.markdown("**💡 Idea Engine**")
            ideas = idea_data.get('daily_ideas', {})
            st.write(f"• Päivän teema: {ideas.get('daily_theme', 'unknown').replace('_', ' ').title()}")
            st.write(f"• Ideoita: {len(ideas.get('ideas', []))}")
            st.write(f"• Kokonaispotentiaali: {ideas.get('total_potential_earning', 0):.0f}€")
        
        # Toimenpiteet
        st.subheader("🚀 Seuraavat toimenpiteet")
        st.write("1. **Priorisoi kriittisimmät parannukset** yllä olevien suositusten perusteella")
        st.write("2. **Aloita yhdellä idealla** Idea Enginesta")
        st.write("3. **Seuraa edistymistä** säännöllisesti")
        st.write("4. **Päivitä profiiliasi** kun oppii uutta")
        st.write("5. **Käytä toimintasuunnitelmaa** ideoiden toteuttamiseen")

# API-kutsut

def get_income_analysis():
    """Hae tuloanalyysi"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/intelligence/income/analysis",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_daily_income_opportunity():
    """Hae päivittäinen tulonlisäysmahdollisuus"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/intelligence/income/daily-opportunity",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_liabilities_analysis():
    """Hae velka-analyysi"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/intelligence/liabilities/analysis",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def calculate_debt_payoff(liability_data, extra_payment):
    """Laske velan maksusuunnitelma"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/intelligence/liabilities/calculate-payoff",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json={"liability_data": liability_data, "extra_payment": extra_payment}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_daily_ideas(user_profile):
    """Hae päivittäiset ideat"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/intelligence/ideas/daily",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            params={"user_profile": user_profile}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def create_action_plan(selected_ideas, user_schedule):
    """Luo toimintasuunnitelma"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/intelligence/ideas/action-plan",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"},
            json={"selected_ideas": selected_ideas, "user_schedule": user_schedule}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_comprehensive_dashboard():
    """Hae kattava dashboard"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/intelligence/dashboard/comprehensive",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None 