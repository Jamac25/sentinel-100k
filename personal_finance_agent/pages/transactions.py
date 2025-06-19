"""
Transactions page for Personal Finance Agent Streamlit app.
Comprehensive transaction management with filtering, editing, and AI categorization.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
import time

def show_transactions_page(api):
    """Display comprehensive transactions management page."""
    st.title("💳 Transaktiot")
    
    # Create tabs for different transaction views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Listaus", "➕ Uusi transaktio", "📊 Analytiikka", "🤖 AI-luokittelu"
    ])
    
    with tab1:
        show_transactions_list(api)
    
    with tab2:
        show_add_transaction(api)
    
    with tab3:
        show_transactions_analytics(api)
    
    with tab4:
        show_ai_categorization(api)

def show_transactions_list(api):
    """Display transactions list with advanced filtering."""
    st.subheader("📋 Transaktioiden listaus")
    
    # Filters section
    with st.expander("🔍 Suodattimet", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            st.markdown("**Päivämääräväli**")
            date_from = st.date_input(
                "Alkaen",
                value=date.today() - timedelta(days=30),
                key="tx_date_from"
            )
            date_to = st.date_input(
                "Päättyen",
                value=date.today(),
                key="tx_date_to"
            )
        
        with col2:
            # Amount range filter
            st.markdown("**Summaväli**")
            min_amount = st.number_input(
                "Vähimmäissumma (€)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                key="tx_min_amount"
            )
            max_amount = st.number_input(
                "Enimmäissumma (€)",
                min_value=0.0,
                value=10000.0,
                step=10.0,
                key="tx_max_amount"
            )
        
        with col3:
            # Category and type filters
            st.markdown("**Kategoria ja tyyppi**")
            
            # Load categories for filter
            categories = api.get_categories()
            category_options = ["Kaikki"] + [cat["name"] for cat in categories]
            selected_category = st.selectbox(
                "Kategoria",
                category_options,
                key="tx_category_filter"
            )
            
            transaction_type = st.selectbox(
                "Tyyppi",
                ["Kaikki", "Tulo", "Meno"],
                key="tx_type_filter"
            )
            
            # Search filter
            search_query = st.text_input(
                "🔍 Haku (kuvaus, kauppias)",
                placeholder="Esim. kauppa, kahvila...",
                key="tx_search"
            )
    
    # Apply filters and load transactions
    filters = {}
    if date_from:
        filters["date_from"] = date_from.isoformat()
    if date_to:
        filters["date_to"] = date_to.isoformat()
    if min_amount > 0:
        filters["min_amount"] = min_amount
    if max_amount < 10000:
        filters["max_amount"] = max_amount
    if selected_category != "Kaikki":
        # Find category ID
        category_id = next((cat["id"] for cat in categories if cat["name"] == selected_category), None)
        if category_id:
            filters["category_id"] = category_id
    if transaction_type != "Kaikki":
        filters["transaction_type"] = "income" if transaction_type == "Tulo" else "expense"
    if search_query:
        filters["search"] = search_query
    
    # Load transactions
    with st.spinner("Ladataan transaktioita..."):
        transactions = api.get_transactions(**filters)
    
    if not transactions:
        st.info("Ei transaktioita löytynyt annetuilla suodattimilla.")
        return
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_income = sum(abs(tx["amount"]) for tx in transactions if tx["amount"] < 0)
    total_expenses = sum(tx["amount"] for tx in transactions if tx["amount"] > 0)
    net_amount = total_income - total_expenses
    
    with col1:
        st.metric("💰 Tulot", f"€{total_income:.2f}")
    with col2:
        st.metric("💸 Menot", f"€{total_expenses:.2f}")
    with col3:
        st.metric("💵 Netto", f"€{net_amount:.2f}")
    with col4:
        st.metric("📊 Lukumäärä", len(transactions))
    
    # Transactions table
    st.subheader(f"Transaktiot ({len(transactions)} kpl)")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(transactions)
    
    # Format the dataframe for display
    if not df.empty:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.strftime("%d.%m.%Y")
        df["amount_formatted"] = df["amount"].apply(lambda x: f"€{x:.2f}")
        df["type_emoji"] = df["amount"].apply(lambda x: "💰" if x < 0 else "💸")
        
        # Select and rename columns for display
        display_columns = ["transaction_date", "type_emoji", "description", "amount_formatted"]
        
        # Add optional columns if they exist
        if "merchant_name" in df.columns:
            display_columns.append("merchant_name")
        if "category_name" in df.columns:
            display_columns.append("category_name")
        if "ml_confidence" in df.columns:
            display_columns.append("ml_confidence")
        
        display_df = df[display_columns].copy()
        
        # Rename columns
        column_names = ["Päivämäärä", "Tyyppi", "Kuvaus", "Summa"]
        if "merchant_name" in display_columns:
            column_names.append("Kauppias")
        if "category_name" in display_columns:
            column_names.append("Kategoria")
        if "ml_confidence" in display_columns:
            column_names.append("AI-varmuus")
        
        display_df.columns = column_names
        
        # Format ML confidence if present
        if "AI-varmuus" in display_df.columns:
            display_df["AI-varmuus"] = display_df["AI-varmuus"].apply(
                lambda x: f"{x:.1%}" if pd.notnull(x) else "N/A"
            )
        
        st.dataframe(display_df, use_container_width=True, height=400)

def show_add_transaction(api):
    """Show form for adding new transaction."""
    st.subheader("➕ Lisää uusi transaktio")
    
    # Load categories
    categories = api.get_categories()
    
    with st.form("add_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input(
                "Kuvaus *",
                placeholder="Esim. Ruokaostokset"
            )
            merchant_name = st.text_input(
                "Kauppias",
                placeholder="Esim. K-Market"
            )
            amount = st.number_input(
                "Summa (€) *",
                min_value=-999999.99,
                max_value=999999.99,
                value=0.0,
                step=0.01,
                help="Positiivinen = meno, negatiivinen = tulo"
            )
        
        with col2:
            transaction_date = st.date_input(
                "Päivämäärä *",
                value=date.today()
            )
            
            category_name = st.selectbox(
                "Kategoria",
                ["Automaattinen luokittelu"] + [cat["name"] for cat in categories],
                help="Valitse 'Automaattinen luokittelu' käyttääksesi AI:ta"
            )
            
            transaction_type = st.selectbox(
                "Tyyppi",
                ["Automaattinen", "Tulo", "Meno"],
                help="Automaattinen päättelee tyypin summan perusteella"
            )
        
        submitted = st.form_submit_button("💾 Lisää transaktio", use_container_width=True)
        
        if submitted:
            if not description or amount == 0:
                st.error("Täytä vähintään kuvaus ja summa")
            else:
                # Prepare transaction data
                tx_data = {
                    "description": description,
                    "merchant_name": merchant_name or None,
                    "amount": amount,
                    "transaction_date": transaction_date.isoformat(),
                    "type": None,
                    "status": "completed"
                }
                
                # Set category if not automatic
                if category_name != "Automaattinen luokittelu":
                    category_id = next(cat["id"] for cat in categories if cat["name"] == category_name)
                    tx_data["category_id"] = category_id
                
                # Set type if not automatic
                if transaction_type != "Automaattinen":
                    tx_data["type"] = "income" if transaction_type == "Tulo" else "expense"
                
                with st.spinner("Lisätään transaktio..."):
                    response = api.request("POST", "/transactions/", json=tx_data)
                
                if response:
                    st.success("✅ Transaktio lisätty onnistuneesti!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Transaktion lisääminen epäonnistui")

def show_transactions_analytics(api):
    """Show transaction analytics and insights."""
    st.subheader("📊 Transaktioanalytiikka")
    st.info("Yksityiskohtainen transaktioanalytiikka tulossa pian...")

def show_ai_categorization(api):
    """Show AI categorization tools and bulk operations."""
    st.subheader("🤖 AI-luokittelu")
    st.info("AI-luokittelu-työkalut tulossa pian...") 