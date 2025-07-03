"""
Advanced Onboarding Page for Personal Finance Agent

Comprehensive deep onboarding process with CV analysis, 
skills assessment, and personalized financial profiling.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, Any, List, Optional
import time

def show_onboarding_page(api):
    """Display comprehensive onboarding page."""
    st.title("🚀 Syvä Onboarding - Henkilökohtainen Profilointi")
    
    # KRIITTINEN KORJAUS: Varmista että käyttäjä on kirjautunut sisään
    if not st.session_state.authenticated or not st.session_state.user_info:
        st.error("🚨 Virhe: Sinun täytyy olla kirjautunut sisään suorittaaksesi onboardingin!")
        st.info("Palaa takaisin ja kirjaudu sisään ensin.")
        if st.button("🔙 Takaisin kirjautumiseen"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        return
    
    # KORJAUS: Käytä kirjautuneen käyttäjän tietoja
    current_user_email = st.session_state.user_info['email']
    current_user_id = st.session_state.user_info['id']
    current_user_name = st.session_state.user_info['name']
    
    # Progress tracking in session state (käyttäjäkohtainen)
    onboarding_key = f"onboarding_step_{current_user_email}"
    onboarding_data_key = f"onboarding_data_{current_user_email}"
    
    if onboarding_key not in st.session_state:
        st.session_state[onboarding_key] = 1
    if onboarding_data_key not in st.session_state:
        st.session_state[onboarding_data_key] = {
            'user_id': current_user_id,
            'email': current_user_email,
            'name': current_user_name
        }
    
    # Progress indicator
    progress_value = min(st.session_state[onboarding_key] / 7, 1.0)
    st.progress(progress_value)
    st.caption(f"Vaihe {st.session_state[onboarding_key]}/7 - {int(progress_value * 100)}% valmis")
    
    # Näytä käyttäjälle että onboarding on henkilökohtainen
    st.info(f"👤 Henkilökohtainen onboarding käyttäjälle: **{current_user_name}** ({current_user_email})")
    
    # Step navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        step_names = [
            "1️⃣ Perustiedot",
            "2️⃣ Taloustilanne", 
            "3️⃣ Taidot & Kokemus",
            "4️⃣ Tavoitteet",
            "5️⃣ CV-analyysi",
            "6️⃣ Personointi",
            "7️⃣ Viimeistely"
        ]
        current_step_name = step_names[st.session_state[onboarding_key] - 1]
        st.markdown(f"### {current_step_name}")
    
    # Display current step (päivitetään funktiokultsut)
    if st.session_state[onboarding_key] == 1:
        show_basic_info_step(current_user_email)
    elif st.session_state[onboarding_key] == 2:
        show_financial_status_step(current_user_email)
    elif st.session_state[onboarding_key] == 3:
        show_skills_experience_step(current_user_email)
    elif st.session_state[onboarding_key] == 4:
        show_goals_preferences_step(current_user_email)
    elif st.session_state[onboarding_key] == 5:
        show_cv_analysis_step(api, current_user_email)
    elif st.session_state[onboarding_key] == 6:
        show_personalization_step(api, current_user_email)
    elif st.session_state[onboarding_key] == 7:
        show_completion_step(api, current_user_email)
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state[onboarding_key] > 1:
            if st.button("⬅️ Edellinen", use_container_width=True):
                st.session_state[onboarding_key] -= 1
                st.rerun()
    
    with col3:
        if st.session_state[onboarding_key] < 7:
            if st.button("➡️ Seuraava", use_container_width=True):
                st.session_state[onboarding_key] += 1
                st.rerun()

def show_basic_info_step(user_email: str):
    """Step 1: Basic personal information."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>👤 Kerro itsestäsi</h3>
        <p>Aloitetaan perustilaedoilla henkilökohtaisen profiilin luomiseksi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("basic_info_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Sähköposti on lukittu kirjautuneen käyttäjän mukaan
            st.text_input(
                "Sähköposti (kirjautunut käyttäjä)", 
                value=user_email,
                disabled=True,
                help="Sähköposti on lukittu kirjautuneen käyttäjän mukaan"
            )
            name = st.text_input(
                "Nimi *", 
                value=st.session_state[onboarding_data_key].get('name', ''),
                placeholder="Etunimi Sukunimi"
            )
            age = st.number_input(
                "Ikä *", 
                min_value=18, 
                max_value=80, 
                value=st.session_state[onboarding_data_key].get('age', 30)
            )
        
        with col2:
            profession = st.text_input(
                "Ammatti/Työ *", 
                value=st.session_state[onboarding_data_key].get('profession', ''),
                placeholder="Ohjelmistokehittäjä"
            )
            location = st.text_input(
                "Asuinpaikka", 
                value=st.session_state[onboarding_data_key].get('location', ''),
                placeholder="Helsinki"
            )
            education_level = st.selectbox(
                "Koulutustaso", 
                ["Peruskoulu", "Lukio", "Ammattikoulu", "AMK", "Yliopisto", "Tohtori"],
                index=["Peruskoulu", "Lukio", "Ammattikoulu", "AMK", "Yliopisto", "Tohtori"].index(
                    st.session_state[onboarding_data_key].get('education_level', 'AMK')
                )
            )
        
        if st.form_submit_button("💾 Tallenna perustiedot", use_container_width=True):
            if name and profession:
                st.session_state[onboarding_data_key].update({
                    'name': name,
                    'email': user_email,  # Varmista että käytetään oikeaa sähköpostia
                    'age': age,
                    'profession': profession,
                    'location': location,
                    'education_level': education_level
                })
                st.success("✅ Perustiedot tallennettu!")
                time.sleep(1)
                st.session_state[f"onboarding_step_{user_email}"] = 2
                st.rerun()
            else:
                st.error("❌ Täytä kaikki pakolliset kentät (*)")

def show_financial_status_step(user_email: str):
    """Step 2: Current financial situation."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>💰 Taloustilanne</h3>
        <p>Kerro nykyisestä taloustilanteestasi henkilökohtaisen suunnitelman luomiseksi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("financial_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💵 Säästöt ja varat")
            current_savings = st.number_input(
                "Nykyiset säästöt (€) *", 
                min_value=0.0, 
                value=float(st.session_state[onboarding_data_key].get('current_savings', 5000)),
                step=100.0,
                help="Säästötili, sijoitukset ja muut varat yhteensä"
            )
            
            savings_goal = st.number_input(
                "Säästötavoite (€) *", 
                min_value=1000.0, 
                value=float(st.session_state[onboarding_data_key].get('savings_goal', 100000)),
                step=1000.0,
                help="Tavoite voi olla 100K€ tai oma valintasi"
            )
            
            debt_amount = st.number_input(
                "Velat yhteensä (€)", 
                min_value=0.0, 
                value=float(st.session_state[onboarding_data_key].get('debt_amount', 0)),
                step=100.0,
                help="Lainat, luotot ja muut velat"
            )
        
        with col2:
            st.subheader("📊 Kuukausittaiset rahavirrat")
            monthly_income = st.number_input(
                "Kuukausitulot brutto (€) *", 
                min_value=0.0, 
                value=float(st.session_state[onboarding_data_key].get('monthly_income', 3500)),
                step=50.0
            )
            
            monthly_expenses = st.number_input(
                "Kuukausimenot (€) *", 
                min_value=0.0, 
                value=float(st.session_state[onboarding_data_key].get('monthly_expenses', 2500)),
                step=50.0,
                help="Kaikki säännölliset kulut yhteensä"
            )
            
            risk_tolerance = st.selectbox(
                "Riskinsietokyky", 
                ["Konservatiivinen", "Maltillinen", "Aggressiivinen"],
                index=["Konservatiivinen", "Maltillinen", "Aggressiivinen"].index(
                    st.session_state[onboarding_data_key].get('risk_tolerance', 'Maltillinen')
                )
            )
        
        # Financial summary
        if monthly_income > 0 and monthly_expenses > 0:
            monthly_net = monthly_income - monthly_expenses
            savings_rate = (monthly_net / monthly_income) * 100
            
            st.subheader("📈 Talousanalyysi")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Kuukausisäästö", f"{monthly_net:,.0f}€")
            with col2:
                st.metric("Säästöaste", f"{savings_rate:.1f}%")
            with col3:
                if savings_goal > current_savings and monthly_net > 0:
                    months_to_goal = (savings_goal - current_savings) / monthly_net
                    st.metric("Kuukausia tavoitteeseen", f"{months_to_goal:.1f}")
                else:
                    st.metric("Tavoite", "Saavutettu! 🎉")
        
        if st.form_submit_button("💾 Tallenna taloustiedot", use_container_width=True):
            if monthly_income > 0 and monthly_expenses >= 0:
                st.session_state[onboarding_data_key].update({
                    'current_savings': current_savings,
                    'savings_goal': savings_goal,
                    'monthly_income': monthly_income,
                    'monthly_expenses': monthly_expenses,
                    'debt_amount': debt_amount,
                    'risk_tolerance': risk_tolerance
                })
                st.success("✅ Taloustiedot tallennettu!")
                time.sleep(1)
                st.session_state[f"onboarding_step_{user_email}"] = 3
                st.rerun()
            else:
                st.error("❌ Tarkista tulot ja menot")

def show_skills_experience_step(user_email: str):
    """Step 3: Skills and work experience."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>🎯 Taidot ja kokemus</h3>
        <p>Analysoidaan osaamisesi parhaan tulostrategian löytämiseksi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("skills_form", clear_on_submit=False):
        # Skills selection
        st.subheader("💼 Osaamisalueet")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tech_skills = st.multiselect(
                "Tekniset taidot",
                ["Ohjelmointi", "Web-kehitys", "Mobiiliapps", "Tietoturva", "DevOps", "AI/ML", "Tietokanta-hallinta"],
                default=st.session_state[onboarding_data_key].get('tech_skills', [])
            )
            
            creative_skills = st.multiselect(
                "Luovat taidot",
                ["Graafinen suunnittelu", "UI/UX", "Valokuvaus", "Videoediteing", "Kirjoittaminen", "Markkinointi"],
                default=st.session_state[onboarding_data_key].get('creative_skills', [])
            )
        
        with col2:
            business_skills = st.multiselect(
                "Liiketoimintataidot",
                ["Myynti", "Asiakaspalvelu", "Projektinhallinta", "Johtaminen", "Talous", "HR"],
                default=st.session_state[onboarding_data_key].get('business_skills', [])
            )
            
            language_skills = st.multiselect(
                "Kielitaidot",
                ["Englanti", "Ruotsi", "Saksa", "Ranska", "Espanja", "Venäjä", "Muut"],
                default=st.session_state[onboarding_data_key].get('language_skills', [])
            )
        
        # Experience
        st.subheader("📅 Työkokemus")
        
        col1, col2 = st.columns(2)
        
        with col1:
            work_experience_years = st.slider(
                "Työkokemusta (vuotta)", 
                0, 40, 
                st.session_state[onboarding_data_key].get('work_experience_years', 5)
            )
            
            time_availability_hours = st.slider(
                "Aikaa sivutöihin (tuntia/viikko)", 
                0, 40, 
                st.session_state[onboarding_data_key].get('time_availability_hours', 10)
            )
        
        with col2:
            current_employment = st.selectbox(
                "Työttilanne",
                ["Kokopäivätyö", "Osa-aikatyö", "Freelancer", "Yrittäjä", "Työtön", "Opiskelija"],
                index=["Kokopäivätyö", "Osa-aikatyö", "Freelancer", "Yrittäjä", "Työtön", "Opiskelija"].index(
                    st.session_state[onboarding_data_key].get('current_employment', 'Kokopäivätyö')
                )
            )
            
            freelance_experience = st.selectbox(
                "Freelance-kokemus",
                ["Ei kokemusta", "Vähän kokemusta", "Keskitasoa", "Paljon kokemusta", "Ammattilainen"],
                index=["Ei kokemusta", "Vähän kokemusta", "Keskitasoa", "Paljon kokemusta", "Ammattilainen"].index(
                    st.session_state[onboarding_data_key].get('freelance_experience', 'Ei kokemusta')
                )
            )
        
        if st.form_submit_button("💾 Tallenna osaamistiedot", use_container_width=True):
            # Combine all skills
            all_skills = tech_skills + creative_skills + business_skills + language_skills
            
            st.session_state[onboarding_data_key].update({
                'skills': all_skills,
                'tech_skills': tech_skills,
                'creative_skills': creative_skills,
                'business_skills': business_skills,
                'language_skills': language_skills,
                'work_experience_years': work_experience_years,
                'time_availability_hours': time_availability_hours,
                'current_employment': current_employment,
                'freelance_experience': freelance_experience
            })
            
            st.success("✅ Osaamistiedot tallennettu!")
            time.sleep(1)
            st.session_state[f"onboarding_step_{user_email}"] = 4
            st.rerun()

def show_goals_preferences_step(user_email: str):
    """Step 4: Financial goals and preferences."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>🎯 Tavoitteet ja mieltymykset</h3>
        <p>Määritellään henkilökohtaiset tavoitteet ja ansaintamenetelmät.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("goals_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Taloustavoitteet")
            financial_goals = st.multiselect(
                "Ensisijaiset tavoitteet",
                ["Säästäminen", "Velkojen maksu", "Sijoittaminen", "Hätävara", "Asunnon osto", "Eläke", "Lapset"],
                default=st.session_state[onboarding_data_key].get('financial_goals', ['Säästäminen'])
            )
            
            investment_experience = st.selectbox(
                "Sijoituskokemus",
                ["Aloittelija", "Perustiedot", "Keskitaso", "Kokenut", "Asiantuntija"],
                index=["Aloittelija", "Perustiedot", "Keskitaso", "Kokenut", "Asiantuntija"].index(
                    st.session_state[onboarding_data_key].get('investment_experience', 'Aloittelija')
                )
            )
            
            timeline_preference = st.selectbox(
                "Aikajänne tavoitteelle",
                ["Alle vuosi", "1-2 vuotta", "3-5 vuotta", "5-10 vuotta", "Yli 10 vuotta"],
                index=["Alle vuosi", "1-2 vuotta", "3-5 vuotta", "5-10 vuotta", "Yli 10 vuotta"].index(
                    st.session_state[onboarding_data_key].get('timeline_preference', '3-5 vuotta')
                )
            )
        
        with col2:
            st.subheader("💼 Ansaintamenetelmät")
            preferred_income_methods = st.multiselect(
                "Kiinnostavat tulonlähteet",
                ["Freelancing", "Sijoittaminen", "Oma yritys", "Sivutyö", "Passiivinen tulo", "Konsultointi", "Online-myynti"],
                default=st.session_state[onboarding_data_key].get('preferred_income_methods', ['Freelancing'])
            )
            
            work_style_preference = st.selectbox(
                "Työtyylimielymys",
                ["Etätyö", "Toimistotyö", "Sekamuoto", "Asiakastyö", "Itsenäinen työ"],
                index=["Etätyö", "Toimistotyö", "Sekamuoto", "Asiakastyö", "Itsenäinen työ"].index(
                    st.session_state[onboarding_data_key].get('work_style_preference', 'Etätyö')
                )
            )
            
            income_stability_preference = st.selectbox(
                "Tulojen vakausmielymys",
                ["Vakaat tulot", "Maltillista vaihtelua", "Korkea riski/tuotto"],
                index=["Vakaat tulot", "Maltillista vaihtelua", "Korkea riski/tuotto"].index(
                    st.session_state[onboarding_data_key].get('income_stability_preference', 'Maltillista vaihtelua')
                )
            )
        
        # Motivation and mindset
        st.subheader("🧠 Motivaatio ja mindset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            motivation_level = st.slider(
                "Motivaatiotaso (1-10)", 
                1, 10, 
                st.session_state[onboarding_data_key].get('motivation_level', 7)
            )
            
            learning_preference = st.selectbox(
                "Oppimistyyli",
                ["Lukeminen", "Videot", "Käytännön harjoittelu", "Mentorointl", "Kurssit"],
                index=["Lukeminen", "Videot", "Käytännön harjoittelu", "Mentorointl", "Kurssit"].index(
                    st.session_state[onboarding_data_key].get('learning_preference', 'Käytännön harjoittelu')
                )
            )
        
        with col2:
            commitment_level = st.slider(
                "Sitoutumistaso (1-10)", 
                1, 10, 
                st.session_state[onboarding_data_key].get('commitment_level', 8)
            )
            
            support_preference = st.selectbox(
                "Tuen tarve",
                ["Itsenäinen", "Vähän tukea", "Säännöllistä tukea", "Paljon tukea", "Jatkuvaa mentorointia"],
                index=["Itsenäinen", "Vähän tukea", "Säännöllistä tukea", "Paljon tukea", "Jatkuvaa mentorointia"].index(
                    st.session_state[onboarding_data_key].get('support_preference', 'Säännöllistä tukea')
                )
            )
        
        if st.form_submit_button("💾 Tallenna tavoitteet", use_container_width=True):
            st.session_state[onboarding_data_key].update({
                'financial_goals': financial_goals,
                'investment_experience': investment_experience,
                'timeline_preference': timeline_preference,
                'preferred_income_methods': preferred_income_methods,
                'work_style_preference': work_style_preference,
                'income_stability_preference': income_stability_preference,
                'motivation_level': motivation_level,
                'commitment_level': commitment_level,
                'learning_preference': learning_preference,
                'support_preference': support_preference
            })
            
            st.success("✅ Tavoitteet tallennettu!")
            time.sleep(1)
            st.session_state[f"onboarding_step_{user_email}"] = 5
            st.rerun()

def show_cv_analysis_step(api, user_email: str):
    """Step 5: CV upload and analysis."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>📄 CV-analyysi</h3>
        <p>Lataa CV:si saadaksesi henkilökohtaista analyysiä osaamisestasi ja tulomahdollisuuksista.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # CV Upload section
    st.subheader("📎 CV:n lataaminen")
    
    uploaded_file = st.file_uploader(
        "Valitse CV-tiedosto",
        type=['pdf', 'txt', 'doc', 'docx'],
        help="Tuetut formaatit: PDF, TXT, DOC, DOCX"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ Tiedosto ladattu: {uploaded_file.name}")
        st.info(f"📊 Koko: {uploaded_file.size} tavua")
        
        # Analyze button
        if st.button("🔍 Analysoi CV", use_container_width=True):
            with st.spinner("🤖 Analysoidaan CV:tä..."):
                try:
                    # This would integrate with the actual CV upload API
                    # For now, we'll simulate the analysis
                    cv_content = uploaded_file.read()
                    
                    # Mock analysis results (would come from API)
                    cv_analysis = {
                        "skills_detected": ["programming", "design", "marketing"],
                        "estimated_experience_years": 5,
                        "cv_quality_score": 85,
                        "recommended_income_streams": ["Freelance ohjelmointi", "UI/UX design", "Digitaalinen markkinointi"]
                    }
                    
                    # Store analysis results
                    st.session_state[onboarding_data_key]['cv_analysis'] = cv_analysis
                    st.session_state[onboarding_data_key]['cv_filename'] = uploaded_file.name
                    
                    # Display results
                    show_cv_analysis_results(cv_analysis)
                    
                except Exception as e:
                    st.error(f"❌ CV:n analysointi epäonnistui: {str(e)}")
    
    # Manual skills verification
    st.subheader("✏️ Taitojen vahvistus")
    st.write("Vahvista tai täydennä automaattisesti tunnistettuja taitoja:")
    
    if 'cv_analysis' in st.session_state[onboarding_data_key]:
        detected_skills = st.session_state[onboarding_data_key]['cv_analysis'].get('skills_detected', [])
        st.multiselect(
            "Tunnistetut taidot (voit muokata)",
            ["Ohjelmointi", "Suunnittelu", "Markkinointi", "Myynti", "Kirjoittaminen", "Käännöstyö", "Valokuvaus"],
            default=detected_skills,
            key="verified_skills"
        )
    
    # Continue button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("➡️ Jatka ilman CV:tä", use_container_width=True):
            st.session_state[f"onboarding_step_{user_email}"] = 6
            st.rerun()

def show_cv_analysis_results(cv_analysis):
    """Display CV analysis results."""
    st.subheader("📊 CV-analyysin tulokset")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tunnistetut taidot", len(cv_analysis["skills_detected"]))
    
    with col2:
        st.metric("Kokemusvuodet", f"{cv_analysis['estimated_experience_years']} v")
    
    with col3:
        st.metric("CV:n laatu", f"{cv_analysis['cv_quality_score']}/100")
    
    # Skills breakdown
    st.subheader("🎯 Tunnistetut osaamisalueet")
    skills_df = pd.DataFrame({
        'Taito': cv_analysis["skills_detected"],
        'Vahvuus': [85, 75, 65]  # Mock scores
    })
    
    fig = px.bar(skills_df, x='Taito', y='Vahvuus', 
                 title="Osaamisvahvuudet CV:n perusteella")
    st.plotly_chart(fig, use_container_width=True)
    
    # Income recommendations
    st.subheader("💰 Suositellut tulolähteet")
    for i, income_stream in enumerate(cv_analysis["recommended_income_streams"], 1):
        st.write(f"{i}. **{income_stream}**")

def show_personalization_step(api, user_email: str):
    """Step 6: AI personalization and preview."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>🤖 AI-personointi</h3>
        <p>Luodaan henkilökohtainen strategia tietojesi perusteella.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate personalization preview
    if st.button("🎯 Luo henkilökohtainen strategia", use_container_width=True):
        with st.spinner("🤖 AI analysoi profiiliasi..."):
            time.sleep(3)  # Simulate processing
            
            # Create personalized preview
            create_personalization_preview(onboarding_data_key)
    
    # If preview exists, show it
    if f"personalization_preview_{user_email}" in st.session_state:
        show_personalization_preview(onboarding_data_key)

def create_personalization_preview(onboarding_data_key: str):
    """Create personalized strategy preview."""
    data = st.session_state[onboarding_data_key]
    user_email = data.get('email')
    
    # Calculate personalized metrics
    monthly_net = data.get('monthly_income', 3500) - data.get('monthly_expenses', 2500)
    savings_rate = (monthly_net / data.get('monthly_income', 3500)) * 100
    
    # AI recommendations based on profile
    recommendations = []
    
    if monthly_net < 500:
        recommendations.append("🚨 Ensisijainen tavoite: Kasvata kuukausisäästöjä")
        recommendations.append("💡 Tulojen kasvattaminen on kriittistä")
    elif savings_rate < 20:
        recommendations.append("📈 Tavoittele yli 20% säästöastetta")
        recommendations.append("✂️ Optimoi menoja edelleen")
    else:
        recommendations.append("🎉 Erinomainen säästöaste!")
        recommendations.append("🚀 Keskity tulojen kasvattamiseen")
    
    # Skills-based recommendations
    skills = data.get('skills', [])
    if 'Ohjelmointi' in skills:
        recommendations.append("💻 Hyödynnä ohjelmointitaitoja freelancingissä")
    if 'Suunnittelu' in skills:
        recommendations.append("🎨 Design-palvelut voivat tuoda hyvää lisätuloa")
    
    # Weekly cycle preview
    weekly_targets = []
    base_target = max(300, monthly_net * 0.8)  # 80% of monthly net as base
    
    for week in range(1, 8):
        week_target = base_target * (1 + (week - 1) * 0.15)  # 15% increase per week
        weekly_targets.append({
            'week': week,
            'target': round(week_target, 0),
            'focus': f"Viikko {week} haasteet"
        })
    
    # Store personalization data
    st.session_state[f"personalization_preview_{user_email}"] = {
        'savings_rate': savings_rate,
        'monthly_net': monthly_net,
        'recommendations': recommendations,
        'weekly_targets': weekly_targets,
        'ai_coach_style': determine_ai_coach_style(data),
        'success_probability': calculate_success_probability(data)
    }

def show_personalization_preview(onboarding_data_key: str):
    """Show the personalized strategy preview."""
    data = st.session_state[onboarding_data_key]
    user_email = data.get('email')
    preview = st.session_state[f"personalization_preview_{user_email}"]
    
    st.subheader("📊 Henkilökohtainen strategia")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Säästöaste", f"{preview['savings_rate']:.1f}%")
    
    with col2:
        st.metric("Kuukausisäästö", f"{preview['monthly_net']:.0f}€")
    
    with col3:
        st.metric("AI-valmentaja", preview['ai_coach_style'])
    
    with col4:
        st.metric("Onnistumistodennäköisyys", f"{preview['success_probability']}%")
    
    # AI Recommendations
    st.subheader("🤖 AI:n suositukset")
    for rec in preview['recommendations']:
        st.write(f"• {rec}")
    
    # Weekly cycle preview
    st.subheader("📅 7-viikon sykli - esikatselu")
    
    weekly_df = pd.DataFrame(preview['weekly_targets'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weekly_df['week'],
        y=weekly_df['target'],
        mode='lines+markers',
        name='Viikkotavoite (€)',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Progressiivinen 7-viikon sykli",
        xaxis_title="Viikko",
        yaxis_title="Tavoite (€)",
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Preview table
    st.subheader("📋 Viikkotavoitteet")
    st.dataframe(weekly_df, use_container_width=True)

def determine_ai_coach_style(data):
    """Determine AI coach style based on user data."""
    motivation = data.get('motivation_level', 7)
    support_need = data.get('support_preference', 'Säännöllistä tukea')
    
    if motivation >= 8 and 'Itsenäinen' in support_need:
        return "Motivaattori"
    elif support_need in ['Paljon tukea', 'Jatkuvaa mentorointia']:
        return "Mentoroiva"
    else:
        return "Ohjaava"

def calculate_success_probability(data):
    """Calculate success probability based on user profile."""
    score = 50  # Base score
    
    # Add points for positive factors
    if data.get('motivation_level', 0) >= 7:
        score += 15
    if data.get('commitment_level', 0) >= 7:
        score += 15
    if data.get('work_experience_years', 0) >= 3:
        score += 10
    if len(data.get('skills', [])) >= 3:
        score += 10
    
    # Monthly net income factor
    monthly_net = data.get('monthly_income', 3500) - data.get('monthly_expenses', 2500)
    if monthly_net > 1000:
        score += 10
    elif monthly_net > 500:
        score += 5
    
    return min(95, score)

def show_completion_step(api, user_email: str):
    """Step 7: Complete onboarding and initialize systems."""
    onboarding_data_key = f"onboarding_data_{user_email}"
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h3>🎉 Viimeistely</h3>
        <p>Viimeistellään profiili ja aloitetaan henkilökohtainen säästömatka!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show complete profile summary
    show_profile_summary(onboarding_data_key)
    
    # Final confirmation and start
    st.subheader("🚀 Aloita Sentinel 100K matka")
    
    if st.button("✅ Viimeistele onboarding ja aloita!", use_container_width=True, type="primary"):
        complete_onboarding_process(api, onboarding_data_key)

def show_profile_summary(onboarding_data_key: str):
    """Show complete user profile summary."""
    data = st.session_state[onboarding_data_key]
    
    st.subheader("👤 Profiilisi yhteenveto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Perustiedot:**")
        st.write(f"• Nimi: {data.get('name', 'N/A')}")
        st.write(f"• Ikä: {data.get('age', 'N/A')}")
        st.write(f"• Ammatti: {data.get('profession', 'N/A')}")
        st.write(f"• Koulutus: {data.get('education_level', 'N/A')}")
        
        st.write("**Taloustilanne:**")
        st.write(f"• Säästöt: {data.get('current_savings', 0):,.0f}€")
        st.write(f"• Tavoite: {data.get('savings_goal', 100000):,.0f}€")
        st.write(f"• Kuukausitulot: {data.get('monthly_income', 0):,.0f}€")
        st.write(f"• Kuukausimenot: {data.get('monthly_expenses', 0):,.0f}€")
    
    with col2:
        st.write("**Osaaminen:**")
        skills = data.get('skills', [])
        if skills:
            for skill in skills[:5]:  # Show top 5 skills
                st.write(f"• {skill}")
        else:
            st.write("• Ei määriteltyjä taitoja")
        
        st.write("**Tavoitteet:**")
        financial_goals = data.get('financial_goals', [])
        if financial_goals:
            for goal in financial_goals[:3]:  # Show top 3 goals
                st.write(f"• {goal}")
        else:
            st.write("• Ei määriteltyjä tavoitteita")
        
        st.write("**Mieltymykset:**")
        st.write(f"• Riskinsietokyky: {data.get('risk_tolerance', 'N/A')}")
        st.write(f"• Aikaa sivutöihin: {data.get('time_availability_hours', 0)}h/viikko")

def complete_onboarding_process(api, onboarding_data_key: str):
    """Complete the onboarding process via API."""
    with st.spinner("🚀 Viimeistellään onboarding..."):
        try:
            # KORJAUS: Käytä oikeaa käyttäjätunnusta
            data = st.session_state[onboarding_data_key]
            user_email = data.get('email')
            user_id = data.get('user_id')
            
            if not user_email or not user_id:
                st.error("🚨 Virhe: Käyttäjätiedot puuttuvat!")
                return
            
            # Prepare complete onboarding data with user identification
            onboarding_payload = prepare_onboarding_payload(onboarding_data_key)
            
            # KRIITTINEN: Lisää käyttäjätunnistus payloadiin
            onboarding_payload.update({
                'user_id': user_id,
                'user_email': user_email,
                'is_authenticated_user': True
            })
            
            # Send to backend with user context
            complete_result = api.request("POST", "/api/v1/onboarding/complete", json=onboarding_payload)
            
            if complete_result:
                st.success("🎉 Onboarding suoritettu onnistuneesti!")
                
                # Show completion results
                show_completion_results(complete_result)
                
                # Mark onboarding as completed for this specific user
                st.session_state.onboarding_completed = True
                st.session_state[f"onboarding_completed_{user_email}"] = True
                
                # Clear this user's onboarding data
                if onboarding_data_key in st.session_state:
                    del st.session_state[onboarding_data_key]
                if f"onboarding_step_{user_email}" in st.session_state:
                    st.session_state[f"onboarding_step_{user_email}"] = 1
                
                time.sleep(3)
                st.rerun()
                
            else:
                st.error("❌ Onboardingin viimeistely epäonnistui")
                
        except Exception as e:
            st.error(f"❌ Virhe onboardingissa: {str(e)}")

def prepare_onboarding_payload(onboarding_data_key: str):
    """Prepare the complete onboarding payload for API."""
    data = st.session_state[onboarding_data_key]
    
    return {
        "name": data.get('name'),
        "email": data.get('email'),
        "age": data.get('age'),
        "profession": data.get('profession'),
        "current_savings": data.get('current_savings'),
        "savings_goal": data.get('savings_goal'),
        "monthly_income": data.get('monthly_income'),
        "monthly_expenses": data.get('monthly_expenses'),
        "skills": data.get('skills', []),
        "work_experience_years": data.get('work_experience_years'),
        "education_level": data.get('education_level'),
        "risk_tolerance": data.get('risk_tolerance'),
        "time_availability_hours": data.get('time_availability_hours'),
        "financial_goals": data.get('financial_goals', []),
        "debt_amount": data.get('debt_amount', 0),
        "investment_experience": data.get('investment_experience'),
        "preferred_income_methods": data.get('preferred_income_methods', [])
    }

def show_completion_results(result):
    """Show onboarding completion results."""
    st.subheader("✅ Onboarding valmis!")
    
    if "profile" in result:
        profile = result["profile"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Käyttäjä ID", result.get("user_id", "N/A"))
        
        with col2:
            st.metric("Profiilin täydellisyys", f"{result.get('onboarding_score', 0)}%")
        
        with col3:
            st.metric("Personointi", result.get("personalization_level", "N/A"))
        
        # Next steps
        if "next_steps" in result:
            st.subheader("📋 Seuraavat askelleet")
            for step in result["next_steps"]:
                st.write(f"• {step}")
        
        # Weekly cycle preview
        if "weekly_cycle_preview" in result:
            st.subheader("📅 Ensimmäinen viikko alkaa!")
            cycle_preview = result["weekly_cycle_preview"]
            if cycle_preview and "error" not in cycle_preview:
                st.json(cycle_preview)
    
    st.balloons() 