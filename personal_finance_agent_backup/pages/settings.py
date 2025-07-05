"""
Settings page for Personal Finance Agent Streamlit app.
User preferences, configuration, and account management.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

def show_settings_page(api):
    """Display comprehensive settings page."""
    st.title("⚙️ Asetukset")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Käyttäjäprofiili", "🤖 AI-asetukset", "🔔 Ilmoitukset", "🔒 Yksityisyys", "📊 Tietojen hallinta"
    ])
    
    with tab1:
        show_user_profile(api)
    
    with tab2:
        show_ai_settings(api)
    
    with tab3:
        show_notification_settings(api)
    
    with tab4:
        show_privacy_settings(api)
    
    with tab5:
        show_data_management(api)

def show_user_profile(api):
    """Display user profile settings."""
    st.subheader("👤 Käyttäjäprofiili")
    
    # Current user info (mock data)
    user_info = {
        "name": "Demo Käyttäjä",
        "email": "demo@example.com",
        "created_at": "2024-01-15",
        "timezone": "Europe/Helsinki",
        "currency": "EUR",
        "language": "fi"
    }
    
    # Profile information
    with st.form("profile_form"):
        st.subheader("📝 Perustiedot")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nimi",
                value=user_info.get("name", ""),
                help="Näkyy sovelluksen tervehdyksissä"
            )
            
            email = st.text_input(
                "Sähköposti",
                value=user_info.get("email", ""),
                help="Käytetään kirjautumiseen ja ilmoituksiin"
            )
            
            timezone = st.selectbox(
                "Aikavyöhyke",
                ["Europe/Helsinki", "Europe/Stockholm", "Europe/Oslo", "UTC"],
                index=0,
                help="Vaikuttaa päivämäärien näyttöön"
            )
        
        with col2:
            currency = st.selectbox(
                "Valuutta",
                ["EUR", "USD", "SEK", "NOK"],
                index=0,
                help="Päävaluutta summien näyttöön"
            )
            
            language = st.selectbox(
                "Kieli",
                ["Suomi", "English", "Svenska"],
                index=0,
                help="Käyttöliittymän kieli"
            )
            
            date_format = st.selectbox(
                "Päivämääräformaatti",
                ["dd.mm.yyyy", "yyyy-mm-dd", "mm/dd/yyyy"],
                index=0,
                help="Miten päivämäärät näytetään"
            )
        
        # Account status
        st.subheader("📊 Tilin tiedot")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📅 Käyttäjä alkaen", user_info.get("created_at", ""))
        
        with col2:
            # Calculate days since registration
            created_date = datetime.strptime(user_info.get("created_at", "2024-01-15"), "%Y-%m-%d")
            days_active = (datetime.now() - created_date).days
            st.metric("🗓️ Päiviä aktiivinen", days_active)
        
        with col3:
            st.metric("📊 Tilin tila", "✅ Aktiivinen")
        
        # Save button
        if st.form_submit_button("💾 Tallenna muutokset", type="primary", use_container_width=True):
            st.success("✅ Profiilin tiedot päivitetty!")
    
    # Password change section
    st.subheader("🔐 Salasanan vaihto")
    
    with st.form("password_form"):
        current_password = st.text_input(
            "Nykyinen salasana",
            type="password"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_password = st.text_input(
                "Uusi salasana",
                type="password",
                help="Vähintään 8 merkkiä, isoja ja pieniä kirjaimia sekä numeroita"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Vahvista uusi salasana",
                type="password"
            )
        
        if st.form_submit_button("🔐 Vaihda salasana", type="secondary"):
            if new_password and confirm_password:
                if new_password == confirm_password:
                    if len(new_password) >= 8:
                        st.success("✅ Salasana vaihdettu onnistuneesti!")
                    else:
                        st.error("❌ Salasanan tulee olla vähintään 8 merkkiä pitkä")
                else:
                    st.error("❌ Salasanat eivät täsmää")
            else:
                st.error("❌ Täytä kaikki kentät")

def show_ai_settings(api):
    """Display AI and ML settings."""
    st.subheader("🤖 AI-asetukset")
    
    # AI Service Configuration
    st.subheader("🔧 AI-palvelun asetukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ai_service = st.selectbox(
            "AI-palvelu",
            ["Paikallinen (ilmainen)", "OpenAI GPT (maksullinen)"],
            index=0,
            help="Valitse käytettävä AI-palvelu suosituksille"
        )
        
        if ai_service == "OpenAI GPT (maksullinen)":
            api_key = st.text_input(
                "OpenAI API-avain",
                type="password",
                help="Tarvitaan OpenAI:n palveluiden käyttöön"
            )
    
    with col2:
        auto_categorization = st.checkbox(
            "🏷️ Automaattinen luokittelu",
            value=True,
            help="Luokittele transaktiot automaattisesti AI:n avulla"
        )
        
        learn_from_corrections = st.checkbox(
            "📚 Opi korjauksista",
            value=True,
            help="Paranna AI:ta käyttäjän korjausten perusteella"
        )
    
    # ML Model Settings
    st.subheader("🧠 Koneoppimisasetukset")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence_threshold = st.slider(
            "🎯 Luottamusraja (%)",
            min_value=50,
            max_value=95,
            value=60,
            help="Vain tämän rajan ylittävät AI-ehdotukset hyväksytään automaattisesti"
        )
    
    with col2:
        retrain_frequency = st.selectbox(
            "🔄 Uudelleenkoulutus",
            ["Päivittäin", "Viikoittain", "Kuukausittain", "Manuaalisesti"],
            index=1,
            help="Kuinka usein AI-malli koulutetaan uudelleen"
        )
    
    with col3:
        model_complexity = st.selectbox(
            "⚙️ Mallin monimutkaisuus",
            ["Yksinkertainen (nopea)", "Keskitaso", "Monimutkainen (tarkka)"],
            index=1,
            help="Tasapaino nopeuden ja tarkkuuden välillä"
        )
    
    # AI Insights Settings
    st.subheader("💡 AI-oivallusten asetukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        insights_frequency = st.selectbox(
            "📊 Oivallusten tiheys",
            ["Päivittäin", "Viikoittain", "Kuukausittain"],
            index=1,
            help="Kuinka usein AI luo uusia oivalluksia"
        )
        
        personalized_tips = st.checkbox(
            "🎯 Henkilökohtaiset vinkit",
            value=True,
            help="Saa henkilökohtaisia säästövinkkejä kulutuskäyttäytymisen perusteella"
        )
    
    with col2:
        spending_alerts = st.checkbox(
            "⚠️ Kulutushälytykset",
            value=True,
            help="Varoita epätavallisesta kulutuksesta"
        )
        
        goal_recommendations = st.checkbox(
            "🎯 Tavoitesuositukset",
            value=True,
            help="Saa ehdotuksia uusista säästötavoitteista"
        )
    
    # Model Performance Display
    st.subheader("📈 Mallin suorituskyky")
    
    # Mock performance data
    performance_data = {
        "accuracy": 85.2,
        "last_trained": "2024-12-18",
        "training_samples": 1247,
        "predictions_made": 89,
        "user_corrections": 7
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Tarkkuus", f"{performance_data['accuracy']:.1f}%")
    
    with col2:
        st.metric("📚 Opetusesimerkkejä", performance_data['training_samples'])
    
    with col3:
        st.metric("🔮 Ennusteita tehty", performance_data['predictions_made'])
    
    with col4:
        st.metric("✏️ Käyttäjän korjauksia", performance_data['user_corrections'])
    
    # Manual retrain button
    if st.button("🔄 Kouluta malli uudelleen", type="secondary"):
        with st.spinner("Koulutetaan mallia uudelleen..."):
            st.success("✅ Malli koulutettu uudelleen onnistuneesti!")
    
    # Save AI settings
    if st.button("💾 Tallenna AI-asetukset", type="primary"):
        st.success("✅ AI-asetukset tallennettu!")

def show_notification_settings(api):
    """Display notification preferences."""
    st.subheader("🔔 Ilmoitusasetukset")
    
    # Email notifications
    st.subheader("📧 Sähköposti-ilmoitukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_weekly_summary = st.checkbox(
            "📊 Viikoittainen yhteenveto",
            value=True,
            help="Saa viikoittaisen raportin taloudellisesta tilanteesta"
        )
        
        email_goal_progress = st.checkbox(
            "🎯 Tavoitteiden edistyminen",
            value=True,
            help="Ilmoitukset tavoitteiden saavuttamisesta"
        )
        
        email_spending_alerts = st.checkbox(
            "⚠️ Kulutushälytykset",
            value=False,
            help="Varoitukset epätavallisesta kulutuksesta"
        )
    
    with col2:
        email_ai_insights = st.checkbox(
            "💡 AI-oivallukset",
            value=True,
            help="Uudet AI:n tuottamat oivallukset ja suositukset"
        )
        
        email_system_updates = st.checkbox(
            "🔄 Järjestelmäpäivitykset",
            value=False,
            help="Tiedotteet uusista ominaisuuksista"
        )
        
        email_security = st.checkbox(
            "🔒 Turvallisuusilmoitukset",
            value=True,
            help="Tärkeät turvallisuuteen liittyvät ilmoitukset"
        )
    
    # In-app notifications
    st.subheader("📱 Sovelluksen sisäiset ilmoitukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        app_transaction_processed = st.checkbox(
            "✅ Transaktio käsitelty",
            value=True,
            help="Ilmoitus kun dokumentti on käsitelty"
        )
        
        app_goal_milestone = st.checkbox(
            "🏆 Välitavoite saavutettu",
            value=True,
            help="Ilmoitus välitavoitteiden saavuttamisesta"
        )
    
    with col2:
        app_budget_warning = st.checkbox(
            "💸 Budjetti ylittymässä",
            value=True,
            help="Varoitus budjetin ylittymisestä"
        )
        
        app_savings_reminder = st.checkbox(
            "💰 Säästömuistutus",
            value=False,
            help="Päivittäinen muistutus säästämisestä"
        )
    
    # Notification frequency
    st.subheader("⏰ Ilmoitusten tiheys")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        summary_frequency = st.selectbox(
            "📊 Yhteenvedot",
            ["Päivittäin", "Viikoittain", "Kuukausittain", "Ei koskaan"],
            index=1
        )
    
    with col2:
        insights_frequency = st.selectbox(
            "💡 AI-oivallukset",
            ["Päivittäin", "Viikoittain", "Kuukausittain", "Ei koskaan"],
            index=1
        )
    
    with col3:
        reminder_time = st.time_input(
            "⏰ Muistutusten aika",
            value=datetime.strptime("18:00", "%H:%M").time(),
            help="Milloin päivittäiset muistutukset lähetetään"
        )
    
    # Telegram bot settings
    st.subheader("🤖 Telegram-botti")
    
    telegram_enabled = st.checkbox(
        "📱 Käytä Telegram-bottia",
        value=False,
        help="Saa ilmoituksia ja voi hallita taloutta Telegram-botin kautta"
    )
    
    if telegram_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            telegram_chat_id = st.text_input(
                "Chat ID",
                help="Telegram-chatin tunniste (saatavilla botin kautta)"
            )
        
        with col2:
            telegram_notifications = st.multiselect(
                "Telegram-ilmoitukset",
                ["Viikoittainen yhteenveto", "Tavoitteet", "Kulutushälytykset", "AI-oivallukset"],
                default=["Viikoittainen yhteenveto", "Tavoitteet"]
            )
    
    # Save notification settings
    if st.button("💾 Tallenna ilmoitusasetukset", type="primary"):
        st.success("✅ Ilmoitusasetukset tallennettu!")

def show_privacy_settings(api):
    """Display privacy and security settings."""
    st.subheader("🔒 Yksityisyys ja tietoturva")
    
    # Privacy overview
    st.markdown("""
    ### 🛡️ Yksityisyysperiaatteet
    
    Personal Finance Agent on suunniteltu **privacy-by-design** -periaatteella:
    - 🏠 **Paikallinen käsittely**: OCR ja ML-mallit toimivat laitteellasi
    - 🔒 **Salattu tallennus**: Kaikki tiedot salataan tietokannassa
    - 🚫 **Ei myydä tietoja**: Emme koskaan myy tai jaa tietojasi
    - 🔍 **Läpinäkyvyys**: Näet aina mitä tietoja kerätään
    """)
    
    # Data processing preferences
    st.subheader("📊 Tietojenkäsittelyn asetukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        local_processing = st.checkbox(
            "🏠 Suosi paikallista käsittelyä",
            value=True,
            help="Käsittele tiedot mahdollisuuksien mukaan paikallisesti"
        )
        
        anonymous_analytics = st.checkbox(
            "📈 Anonyymi analytiikka",
            value=True,
            help="Auta parantamaan sovellusta nimettömillä käyttötiedoilla"
        )
        
        cloud_backup = st.checkbox(
            "☁️ Pilvivarmuuskopiot",
            value=False,
            help="Tallenna salatut varmuuskopiot pilveen"
        )
    
    with col2:
        ai_improvement = st.checkbox(
            "🤖 AI:n parantaminen",
            value=True,
            help="Käytä tietojasi AI-mallien parantamiseen (anonyyminä)"
        )
        
        usage_statistics = st.checkbox(
            "📊 Käyttötilastot",
            value=True,
            help="Kerää nimettömiä käyttötilastoja sovelluksen parantamiseksi"
        )
        
        crash_reports = st.checkbox(
            "🐛 Virheraportointi",
            value=True,
            help="Lähetä automaattisesti virheraportteja kehittäjille"
        )
    
    # Data retention settings
    st.subheader("🗄️ Tietojen säilytys")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        transaction_retention = st.selectbox(
            "💳 Transaktiotiedot",
            ["1 vuosi", "2 vuotta", "5 vuotta", "Ikuisesti"],
            index=2,
            help="Kuinka kauan transaktiotietoja säilytetään"
        )
    
    with col2:
        document_retention = st.selectbox(
            "📄 Dokumentit",
            ["3 kuukautta", "6 kuukautta", "1 vuosi", "2 vuotta"],
            index=2,
            help="Kuinka kauan ladattuja dokumentteja säilytetään"
        )
    
    with col3:
        log_retention = st.selectbox(
            "📝 Lokitiedot",
            ["1 kuukausi", "3 kuukautta", "6 kuukautta", "1 vuosi"],
            index=1,
            help="Kuinka kauan järjestelmälokeja säilytetään"
        )
    
    # Security settings
    st.subheader("🔐 Turvallisuusasetukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        two_factor_auth = st.checkbox(
            "🔐 Kaksivaiheinen tunnistautuminen",
            value=False,
            help="Lisää turvallisuuskerros kirjautumiseen"
        )
        
        if two_factor_auth:
            st.info("📱 Skannaa QR-koodi tunnistautumissovelluksella")
            # Here would be QR code generation
    
    with col2:
        auto_logout = st.selectbox(
            "⏰ Automaattinen uloskirjautuminen",
            ["15 minuuttia", "30 minuuttia", "1 tunti", "4 tuntia", "Ei koskaan"],
            index=2,
            help="Kirjaudu ulos automaattisesti toimettomuuden jälkeen"
        )
        
        login_notifications = st.checkbox(
            "📧 Kirjautumismuistutukset",
            value=True,
            help="Lähetä sähköposti uusista kirjautumisista"
        )
    
    # Privacy dashboard
    st.subheader("📊 Yksityisyyden hallintapaneeli")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Tallennettuja dokumentteja", "23")
    
    with col2:
        st.metric("💳 Transaktioita", "1,247")
    
    with col3:
        st.metric("🤖 AI-ennusteita", "89")
    
    with col4:
        st.metric("📊 Tietojen koko", "12.3 MB")
    
    # Save privacy settings
    if st.button("💾 Tallenna yksityisyysasetukset", type="primary"):
        st.success("✅ Yksityisyysasetukset tallennettu!")

def show_data_management(api):
    """Display data management and export options."""
    st.subheader("📊 Tietojen hallinta")
    
    # Data export section
    st.subheader("📤 Tietojen vienti")
    
    st.markdown("""
    Voit viedä kaikki tietosi useissa formaateissa. Tämä on hyödyllistä varmuuskopioiden tekemiseen 
    tai tietojen siirtämiseen toiseen palveluun.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "📋 Viennin formaatti",
            ["CSV (Excel-yhteensopiva)", "JSON (tekninen)", "PDF (raportti)", "ZIP (kaikki tiedostot)"],
            help="Valitse sopiva formaatti käyttötarkoituksesi mukaan"
        )
        
        export_data_types = st.multiselect(
            "📊 Vietävät tiedot",
            ["Transaktiot", "Kategoriat", "Tavoitteet", "Dokumentit", "Asetukset", "AI-mallin tiedot"],
            default=["Transaktiot", "Kategoriat", "Tavoitteet"],
            help="Valitse mitä tietoja haluat viedä"
        )
    
    with col2:
        export_date_range = st.selectbox(
            "📅 Aikaväli",
            ["Viimeiset 30 päivää", "Viimeiset 90 päivää", "Viimeiset 12 kuukautta", "Kaikki tiedot"],
            index=3,
            help="Rajaa vietävien tietojen aikaväliä"
        )
        
        include_sensitive = st.checkbox(
            "🔒 Sisällytä arkaluonteiset tiedot",
            value=False,
            help="Sisällytä salasanat, API-avaimet ym. (ei suositella)"
        )
    
    # Export buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Vie transaktiot", type="secondary", use_container_width=True):
            st.success("✅ Transaktiot viety onnistuneesti!")
            st.download_button(
                "💾 Lataa tiedosto",
                data="mock_transactions.csv",
                file_name=f"transaktiot_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🎯 Vie tavoitteet", type="secondary", use_container_width=True):
            st.success("✅ Tavoitteet viety onnistuneesti!")
    
    with col3:
        if st.button("📤 Vie kaikki tiedot", type="primary", use_container_width=True):
            with st.spinner("Viedään tietoja..."):
                st.success("✅ Kaikki tiedot viety onnistuneesti!")
    
    # Data import section
    st.subheader("📥 Tietojen tuonti")
    
    st.markdown("""
    Voit tuoda tietoja muista järjestelmistä. Tuetut formaatit:
    - **CSV**: Pankkien tiliotteet, muiden sovellusten viennit
    - **JSON**: Tekninen formaatti tietojen siirtoon
    - **OFX/QIF**: Pankkien standardiformaatit
    """)
    
    uploaded_file = st.file_uploader(
        "Valitse tuotava tiedosto",
        type=['csv', 'json', 'ofx', 'qif'],
        help="Tuetut formaatit: CSV, JSON, OFX, QIF"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            import_type = st.selectbox(
                "📊 Tietojen tyyppi",
                ["Transaktiot", "Kategoriat", "Tavoitteet", "Automaattinen tunnistus"],
                index=3
            )
        
        with col2:
            duplicate_handling = st.selectbox(
                "🔄 Duplikaattien käsittely",
                ["Ohita duplikaatit", "Päivitä olemassa olevat", "Luo uudet versiot"],
                index=0
            )
        
        if st.button("📥 Tuo tiedot", type="primary"):
            with st.spinner("Tuodaan tietoja..."):
                st.success("✅ Tiedot tuotu onnistuneesti!")
                st.info("🔍 Tarkista tuodut tiedot transaktiot-sivulta")
    
    # Data cleanup section
    st.subheader("🧹 Tietojen siivous")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🗑️ Poista vanhat tiedot**")
        
        cleanup_options = st.multiselect(
            "Poistettavat tiedot",
            ["Yli 2 vuotta vanhat transaktiot", "Käsitellyt dokumentit", "Vanhat lokitiedot", "AI-mallin välimuisti"],
            help="Valitse mitä vanhoja tietoja haluat poistaa"
        )
        
        if st.button("🗑️ Siivoa tiedot", type="secondary"):
            if cleanup_options:
                with st.spinner("Siivotaan tietoja..."):
                    st.success(f"✅ Poistettu: {', '.join(cleanup_options)}")
            else:
                st.warning("Valitse poistettavat tiedot")
    
    with col2:
        st.markdown("**🔄 Optimoi tietokanta**")
        
        st.write("Tietokannan optimointi parantaa suorituskykyä ja vapauttaa tilaa.")
        
        if st.button("⚡ Optimoi tietokanta", type="secondary"):
            with st.spinner("Optimoidaan tietokantaa..."):
                st.success("✅ Tietokanta optimoitu!")
                st.info("💾 Vapautettu 2.3 MB tilaa")
    
    # Account deletion
    st.subheader("⚠️ Tilin poistaminen")
    
    st.error("""
    **Varoitus**: Tilin poistaminen on peruuttamaton toimenpide. 
    Kaikki tietosi poistetaan pysyvästi eikä niitä voida palauttaa.
    """)
    
    with st.expander("🚨 Poista tili pysyvästi"):
        st.markdown("""
        Ennen tilin poistamista:
        1. 📤 Vie kaikki tärkeät tiedot
        2. 🔍 Tarkista että et tarvitse tietoja
        3. ✅ Vahvista että haluat poistaa tilin
        """)
        
        confirm_deletion = st.text_input(
            "Kirjoita 'POISTA TILI' vahvistaaksesi",
            help="Tämä varmistaa että haluat todella poistaa tilin"
        )
        
        if confirm_deletion == "POISTA TILI":
            if st.button("🗑️ POISTA TILI PYSYVÄSTI", type="primary"):
                st.error("❌ Tilin poisto ei ole vielä käytössä. Ota yhteyttä tukeen.")
        else:
            st.button("🗑️ POISTA TILI PYSYVÄSTI", disabled=True)
    
    # Save data management settings
    if st.button("💾 Tallenna tiedonhallinta-asetukset", type="primary"):
        st.success("✅ Tiedonhallinta-asetukset tallennettu!") 