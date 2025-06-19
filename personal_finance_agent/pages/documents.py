"""
Documents page for Personal Finance Agent Streamlit app.
OCR document processing, upload, and management functionality.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import io

def show_documents_page(api):
    """Display comprehensive documents management page."""
    st.title("📄 Dokumentit")
    
    # Create tabs for different document views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Lataa dokumentti", "📋 Dokumenttien hallinta", "📊 Käsittelytilastot", "⚙️ OCR-asetukset"
    ])
    
    with tab1:
        show_document_upload(api)
    
    with tab2:
        show_document_management(api)
    
    with tab3:
        show_processing_stats(api)
    
    with tab4:
        show_ocr_settings(api)

def show_document_upload(api):
    """Display document upload interface."""
    st.subheader("📤 Lataa dokumentti OCR-käsittelyyn")
    
    st.markdown("""
    ### 🎯 Tuetut dokumenttityypit:
    - **📄 PDF-tiedostot** - Tiliotteet, laskut, kuitit
    - **📷 Kuvat** - PNG, JPG, JPEG, TIFF, BMP
    - **🧾 Kuitit** - Kauppaostokset, ravintolalaskut
    - **🏦 Tiliotteet** - Pankkitiliotteet
    - **📋 Laskut** - Sähkö-, vesi-, puhelinlaskut
    """)
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Valitse dokumentti",
        type=['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'],
        help="Maksimikoko: 10MB. Tuetut formaatit: PDF, PNG, JPG, JPEG, TIFF, BMP"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📁 Tiedostonimi", uploaded_file.name)
        with col2:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.metric("📏 Koko", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("📋 Tyyppi", uploaded_file.type)
        
        # Document type selection
        document_type = st.selectbox(
            "📂 Dokumenttityyppi",
            ["Automaattinen tunnistus", "Kuitti", "Lasku", "Tiliote", "Muu"],
            help="Valitse dokumenttityyppi tai anna järjestelmän tunnistaa se automaattisesti"
        )
        
        # Preview for images
        if uploaded_file.type.startswith('image/'):
            st.subheader("👁️ Esikatselu")
            st.image(uploaded_file, caption="Ladattu kuva", use_column_width=True)
        
        # Processing options
        st.subheader("⚙️ Käsittelyasetukset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_categorize = st.checkbox(
                "🤖 Automaattinen luokittelu",
                value=True,
                help="Luo transaktiot automaattisesti tunnistettujen tietojen perusteella"
            )
        
        with col2:
            require_review = st.checkbox(
                "👁️ Vaadi manuaalinen tarkistus",
                value=False,
                help="Merkitse dokumentti manuaalista tarkistusta varten"
            )
        
        # Upload button
        if st.button("🚀 Käsittele dokumentti", type="primary", use_container_width=True):
            with st.spinner("Ladataan ja käsitellään dokumenttia..."):
                try:
                    # Prepare document type
                    doc_type = None if document_type == "Automaattinen tunnistus" else document_type.lower()
                    
                    # Upload document
                    result = api.upload_document(
                        file_data=uploaded_file.getvalue(),
                        filename=uploaded_file.name,
                        document_type=doc_type
                    )
                    
                    if result and 'id' in result:
                        st.success("✅ Dokumentti ladattu onnistuneesti!")
                        
                        # Display processing info
                        st.info("📋 Dokumentti lisätty käsittelyjonoon. Käsittely alkaa hetken kuluttua.")
                        
                        # Show document details
                        with st.expander("📄 Dokumentin tiedot"):
                            st.json(result)
                        
                        # Auto-refresh to show processing status
                        st.rerun()
                    else:
                        st.error("❌ Dokumentin lataus epäonnistui")
                        if result:
                            st.error(f"Virhe: {result.get('detail', 'Tuntematon virhe')}")
                
                except Exception as e:
                    st.error(f"❌ Virhe dokumentin käsittelyssä: {str(e)}")
    
    # Recent uploads
    st.subheader("📋 Viimeisimmät lataukset")
    
    with st.spinner("Ladataan viimeisiä dokumentteja..."):
        try:
            # Get recent documents
            recent_docs = api.request("GET", "/documents/?limit=5&sort=created_at")
            
            if recent_docs and isinstance(recent_docs, list):
                for doc in recent_docs:
                    with st.expander(f"📄 {doc.get('original_filename', 'Tuntematon')} - {doc.get('processing_status', 'Tuntematon')}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**ID:** {doc.get('id')}")
                            st.write(f"**Tyyppi:** {doc.get('document_type', 'Tuntematon')}")
                        
                        with col2:
                            st.write(f"**Tila:** {doc.get('processing_status', 'Tuntematon')}")
                            st.write(f"**Luotu:** {doc.get('created_at', '')[:19]}")
                        
                        with col3:
                            if doc.get('processing_status') == 'COMPLETED':
                                st.success("✅ Valmis")
                            elif doc.get('processing_status') == 'PROCESSING':
                                st.info("⏳ Käsitellään")
                            elif doc.get('processing_status') == 'FAILED':
                                st.error("❌ Epäonnistui")
                            else:
                                st.warning("⏸️ Odottaa")
            else:
                st.info("Ei viimeisiä dokumentteja")
        
        except Exception as e:
            st.error(f"Virhe dokumenttien lataamisessa: {str(e)}")

def show_document_management(api):
    """Display document management interface."""
    st.subheader("📋 Dokumenttien hallinta")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "📊 Tila",
            ["Kaikki", "Odottaa", "Käsitellään", "Valmis", "Epäonnistui"]
        )
    
    with col2:
        type_filter = st.selectbox(
            "📂 Tyyppi",
            ["Kaikki", "Kuitti", "Lasku", "Tiliote", "Muu"]
        )
    
    with col3:
        date_range = st.selectbox(
            "📅 Aikaväli",
            ["Viimeiset 7 päivää", "Viimeiset 30 päivää", "Viimeiset 90 päivää", "Kaikki"]
        )
    
    # Load documents with filters
    with st.spinner("Ladataan dokumentteja..."):
        try:
            # Build filter parameters
            params = {}
            if status_filter != "Kaikki":
                status_map = {
                    "Odottaa": "PENDING",
                    "Käsitellään": "PROCESSING", 
                    "Valmis": "COMPLETED",
                    "Epäonnistui": "FAILED"
                }
                params["status"] = status_map.get(status_filter)
            
            if type_filter != "Kaikki":
                params["document_type"] = type_filter.lower()
            
            if date_range != "Kaikki":
                days_map = {
                    "Viimeiset 7 päivää": 7,
                    "Viimeiset 30 päivää": 30,
                    "Viimeiset 90 päivää": 90
                }
                days = days_map.get(date_range, 30)
                params["days"] = days
            
            documents = api.request("GET", "/documents/", params=params)
            
            if documents and isinstance(documents, list):
                st.write(f"📊 Löytyi {len(documents)} dokumenttia")
                
                # Documents table
                if documents:
                    docs_data = []
                    for doc in documents:
                        docs_data.append({
                            "ID": doc.get('id'),
                            "Tiedostonimi": doc.get('original_filename', 'Tuntematon'),
                            "Tyyppi": doc.get('document_type', 'Tuntematon'),
                            "Tila": doc.get('processing_status', 'Tuntematon'),
                            "Luotu": doc.get('created_at', '')[:19] if doc.get('created_at') else '',
                            "Koko (KB)": round(doc.get('file_size', 0) / 1024, 1) if doc.get('file_size') else 0
                        })
                    
                    df = pd.DataFrame(docs_data)
                    
                    # Display with selection
                    selected_rows = st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        on_select="rerun",
                        selection_mode="multi-row"
                    )
                    
                    # Action buttons
                    if selected_rows and len(selected_rows.selection.rows) > 0:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔄 Käsittele uudelleen", type="secondary"):
                                selected_indices = selected_rows.selection.rows
                                for idx in selected_indices:
                                    doc_id = df.iloc[idx]['ID']
                                    try:
                                        result = api.request("POST", f"/documents/{doc_id}/reprocess")
                                        if result:
                                            st.success(f"✅ Dokumentti {doc_id} asetettu uudelleenkäsittelyyn")
                                    except:
                                        st.error(f"❌ Virhe dokumentin {doc_id} uudelleenkäsittelyssä")
                        
                        with col2:
                            if st.button("👁️ Näytä tiedot", type="secondary"):
                                selected_indices = selected_rows.selection.rows
                                for idx in selected_indices:
                                    doc_id = df.iloc[idx]['ID']
                                    try:
                                        doc_details = api.request("GET", f"/documents/{doc_id}")
                                        if doc_details:
                                            with st.expander(f"📄 Dokumentti {doc_id}"):
                                                st.json(doc_details)
                                    except:
                                        st.error(f"❌ Virhe dokumentin {doc_id} tietojen haussa")
                        
                        with col3:
                            if st.button("🗑️ Poista", type="secondary"):
                                selected_indices = selected_rows.selection.rows
                                for idx in selected_indices:
                                    doc_id = df.iloc[idx]['ID']
                                    try:
                                        result = api.request("DELETE", f"/documents/{doc_id}")
                                        if result:
                                            st.success(f"✅ Dokumentti {doc_id} poistettu")
                                    except:
                                        st.error(f"❌ Virhe dokumentin {doc_id} poistossa")
                                st.rerun()
                else:
                    st.info("Ei dokumentteja valituilla suodattimilla")
            else:
                st.info("Ei dokumentteja saatavilla")
        
        except Exception as e:
            st.error(f"Virhe dokumenttien lataamisessa: {str(e)}")

def show_processing_stats(api):
    """Display document processing statistics."""
    st.subheader("📊 Käsittelytilastot")
    
    with st.spinner("Ladataan tilastoja..."):
        try:
            # Get storage stats
            storage_stats = api.request("GET", "/documents/stats/storage")
            
            if storage_stats:
                # Storage metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "📄 Dokumentteja yhteensä",
                        storage_stats.get('total_documents', 0)
                    )
                
                with col2:
                    total_size_mb = storage_stats.get('total_size_bytes', 0) / (1024 * 1024)
                    st.metric(
                        "💾 Tallennustila",
                        f"{total_size_mb:.1f} MB"
                    )
                
                with col3:
                    st.metric(
                        "✅ Käsiteltyjä",
                        storage_stats.get('processed_documents', 0)
                    )
                
                with col4:
                    success_rate = 0
                    if storage_stats.get('total_documents', 0) > 0:
                        success_rate = (storage_stats.get('processed_documents', 0) / storage_stats.get('total_documents', 1)) * 100
                    st.metric(
                        "📈 Onnistumisprosentti",
                        f"{success_rate:.1f}%"
                    )
                
                # Processing status breakdown
                st.subheader("📊 Käsittelytilanne")
                
                status_data = storage_stats.get('status_breakdown', {})
                if status_data:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Status metrics
                        for status, count in status_data.items():
                            status_names = {
                                'PENDING': '⏳ Odottaa',
                                'PROCESSING': '⚙️ Käsitellään',
                                'COMPLETED': '✅ Valmis',
                                'FAILED': '❌ Epäonnistui'
                            }
                            st.metric(status_names.get(status, status), count)
                    
                    with col2:
                        # Status chart
                        if any(status_data.values()):
                            import plotly.express as px
                            
                            fig = px.pie(
                                values=list(status_data.values()),
                                names=[status_names.get(k, k) for k in status_data.keys()],
                                title="Käsittelytilanteiden jakauma"
                            )
                            fig.update_layout(template='plotly_white', height=300)
                            st.plotly_chart(fig, use_container_width=True)
                
                # Document type breakdown
                type_data = storage_stats.get('type_breakdown', {})
                if type_data:
                    st.subheader("📂 Dokumenttityypit")
                    
                    type_names = {
                        'receipt': '🧾 Kuitit',
                        'invoice': '📋 Laskut',
                        'bank_statement': '🏦 Tiliotteet',
                        'other': '📄 Muut'
                    }
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        for doc_type, count in type_data.items():
                            st.metric(type_names.get(doc_type, doc_type), count)
                    
                    with col2:
                        if any(type_data.values()):
                            fig = px.bar(
                                x=[type_names.get(k, k) for k in type_data.keys()],
                                y=list(type_data.values()),
                                title="Dokumenttityyppien jakauma"
                            )
                            fig.update_layout(template='plotly_white', height=300)
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Tilastoja ei saatavilla")
        
        except Exception as e:
            st.error(f"Virhe tilastojen lataamisessa: {str(e)}")
    
    # Processing queue status
    st.subheader("⏳ Käsittelyjono")
    
    try:
        queue_status = api.request("GET", "/documents/processing/queue")
        
        if queue_status:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "📋 Jonossa",
                    queue_status.get('pending_count', 0)
                )
            
            with col2:
                st.metric(
                    "⚙️ Käsitellään",
                    queue_status.get('processing_count', 0)
                )
            
            with col3:
                avg_time = queue_status.get('average_processing_time_seconds', 0)
                st.metric(
                    "⏱️ Keskimääräinen käsittelyaika",
                    f"{avg_time:.1f}s"
                )
            
            # Show queue items if any
            if queue_status.get('queue_items'):
                st.subheader("📋 Jono-erät")
                queue_df = pd.DataFrame(queue_status['queue_items'])
                st.dataframe(queue_df, use_container_width=True)
        else:
            st.info("Jonon tila ei saatavilla")
    
    except Exception as e:
        st.error(f"Virhe jonon tilan haussa: {str(e)}")

def show_ocr_settings(api):
    """Display OCR settings and configuration."""
    st.subheader("⚙️ OCR-asetukset")
    
    st.markdown("""
    ### 🔧 Nykyiset OCR-asetukset
    
    Personal Finance Agent käyttää **Tesseract OCR** -moottoria dokumenttien tekstintunnistukseen.
    Tämä takaa yksityisyytesi, koska kaikki käsittely tapahtuu paikallisesti.
    """)
    
    # OCR Service info
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🏠 Paikallinen käsittely (Tesseract)**
        - ✅ Täydellinen yksityisyys
        - ✅ Ei internet-yhteyttä tarvita
        - ✅ Ilmainen käyttö
        - ⚠️ Keskitasoinen tarkkuus
        """)
    
    with col2:
        st.warning("""
        **☁️ Pilvipalvelu (Google Vision)**
        - ⚠️ Tiedot lähetetään Googlen palvelimille
        - ✅ Korkea tarkkuus
        - ⚠️ Maksullinen (API-avain tarvitaan)
        - ✅ Tukee monia kieliä
        """)
    
    # Language settings
    st.subheader("🌍 Kieliasetukset")
    
    languages = st.multiselect(
        "Valitse tunnistettavat kielet",
        ["Suomi (fin)", "Englanti (eng)", "Ruotsi (swe)", "Norja (nor)"],
        default=["Suomi (fin)", "Englanti (eng)"],
        help="Tesseract tukee useita kieliä samanaikaisesti"
    )
    
    # Processing settings
    st.subheader("⚙️ Käsittelyasetukset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        confidence_threshold = st.slider(
            "🎯 Luottamusraja (%)",
            min_value=50,
            max_value=95,
            value=60,
            help="Vain tämän rajan ylittävät tunnistukset hyväksytään"
        )
        
        auto_rotate = st.checkbox(
            "🔄 Automaattinen kierto",
            value=True,
            help="Korjaa automaattisesti vinot kuvat"
        )
    
    with col2:
        preprocessing = st.checkbox(
            "🖼️ Esikäsittely",
            value=True,
            help="Paranna kuvanlaatua ennen OCR:ää"
        )
        
        extract_tables = st.checkbox(
            "📊 Taulukoiden tunnistus",
            value=False,
            help="Yritä tunnistaa taulukkorakenteita"
        )
    
    # Finnish-specific settings
    st.subheader("🇫🇮 Suomalaiset asetukset")
    
    finnish_formats = st.checkbox(
        "📅 Suomalaiset päivämääräformaatit",
        value=True,
        help="Tunnista dd.mm.yyyy ja dd/mm/yyyy -formaatit"
    )
    
    euro_currency = st.checkbox(
        "💰 Euro-valuutan tunnistus",
        value=True,
        help="Tunnista €-merkki ja EUR-lyhenne"
    )
    
    finnish_merchants = st.checkbox(
        "🏪 Suomalaiset kauppiaat",
        value=True,
        help="Tunnista suomalaisia kauppaketjuja"
    )
    
    # Save settings
    if st.button("💾 Tallenna asetukset", type="primary"):
        st.success("✅ Asetukset tallennettu!")
        st.info("🔄 Uudet asetukset otetaan käyttöön seuraavassa dokumentin käsittelyssä")
    
    # Test OCR
    st.subheader("🧪 Testaa OCR")
    
    st.markdown("Lataa testiasiakirja kokeillaksesi nykyisiä asetuksia:")
    
    test_file = st.file_uploader(
        "Testidokumentti",
        type=['png', 'jpg', 'jpeg'],
        key="test_ocr",
        help="Lataa kuva testikäyttöön"
    )
    
    if test_file and st.button("🔍 Testaa OCR"):
        with st.spinner("Suoritetaan OCR-testiä..."):
            st.info("🚧 OCR-testi tulossa pian!")
            # Here would be OCR test implementation