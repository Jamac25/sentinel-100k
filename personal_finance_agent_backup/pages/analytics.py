"""
Analytics page for Personal Finance Agent Streamlit app.
Advanced financial analytics, insights, and forecasting.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import numpy as np
from typing import Dict, Any, List, Optional
import calendar

def show_analytics_page(api):
    """Display comprehensive analytics page with advanced insights."""
    st.title("📈 Analytiikka")
    
    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Yleiskatsaus", "📈 Trendit", "🔍 Syväanalyysi", "🔮 Ennusteet", "🤖 AI-oivallukset"
    ])
    
    with tab1:
        show_overview_analytics(api)
    
    with tab2:
        show_trends_analytics(api)
    
    with tab3:
        show_deep_analytics(api)
    
    with tab4:
        show_forecasting_analytics(api)
    
    with tab5:
        show_ai_insights(api)

def show_overview_analytics(api):
    """Display financial overview analytics."""
    st.subheader("📊 Taloudellinen yleiskatsaus")
    
    # Time period selector
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Aikajakso",
            ["30 päivää", "90 päivää", "6 kuukautta", "12 kuukautta"],
            index=1
        )
    
    with col2:
        comparison = st.selectbox(
            "Vertailu",
            ["Edellinen jakso", "Viime vuosi", "Ei vertailua"],
            index=0
        )
    
    # Convert period to days
    period_days = {"30 päivää": 30, "90 päivää": 90, "6 kuukautta": 180, "12 kuukautta": 365}[period]
    
    # Load data
    with st.spinner("Ladataan analytiikkatietoja..."):
        dashboard_data = api.get_dashboard_summary(period_days=period_days)
        transactions = api.get_transactions()
    
    if not dashboard_data:
        st.error("Analytiikkatietojen lataaminen epäonnistui")
        return
    
    # Key metrics with comparison
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Kokonaistulot",
            f"€{dashboard_data.get('total_income', 0):.2f}",
            delta=f"€{dashboard_data.get('income_change', 0):.2f}" if comparison != "Ei vertailua" else None
        )
    
    with col2:
        st.metric(
            "💸 Kokonaismenot",
            f"€{dashboard_data.get('total_expenses', 0):.2f}",
            delta=f"€{dashboard_data.get('expense_change', 0):.2f}" if comparison != "Ei vertailua" else None
        )
    
    with col3:
        net_amount = dashboard_data.get('net_amount', 0)
        st.metric(
            "💵 Nettosäästö",
            f"€{net_amount:.2f}",
            delta=f"€{dashboard_data.get('savings_change', 0):.2f}" if comparison != "Ei vertailua" else None
        )
    
    with col4:
        avg_transaction = dashboard_data.get('total_expenses', 0) / max(dashboard_data.get('transaction_count', 1), 1)
        st.metric(
            "📊 Keskimääräinen meno",
            f"€{avg_transaction:.2f}",
            delta=f"€{dashboard_data.get('avg_change', 0):.2f}" if comparison != "Ei vertailua" else None
        )
    
    # Spending breakdown charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥧 Menot kategorioittain")
        categories_data = dashboard_data.get('top_categories', [])
        
        if categories_data:
            df_categories = pd.DataFrame(categories_data)
            
            fig = px.pie(
                df_categories,
                values='amount',
                names='name',
                title="Kategoriaryhmittely",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(template='plotly_white', height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ei kategoriatietoja saatavilla")
    
    with col2:
        st.subheader("📈 Kuukausittainen kehitys")
        monthly_data = dashboard_data.get('monthly_trends', [])
        
        if monthly_data:
            df_monthly = pd.DataFrame(monthly_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_monthly['month_name'],
                y=df_monthly['income'],
                name='Tulot',
                marker_color='#2ca02c',
                opacity=0.8
            ))
            fig.add_trace(go.Bar(
                x=df_monthly['month_name'],
                y=df_monthly['expenses'],
                name='Menot',
                marker_color='#d62728',
                opacity=0.8
            ))
            
            fig.update_layout(
                title="Tulot vs Menot kuukausittain",
                xaxis_title="Kuukausi",
                yaxis_title="Summa (€)",
                barmode='group',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ei riittävästi tietoja kuukausittaisille trendeille")

def show_trends_analytics(api):
    """Display trend analysis."""
    st.subheader("📈 Trendien analyysi")
    
    # Load transaction data
    with st.spinner("Analysoidaan trendejä..."):
        transactions = api.get_transactions()
    
    if not transactions:
        st.info("Ei transaktioita analysoitavaksi")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['month'] = df['transaction_date'].dt.to_period('M')
    df['weekday'] = df['transaction_date'].dt.day_name()
    df['hour'] = df['transaction_date'].dt.hour
    
    # Weekly spending pattern
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Viikoittainen kulutus")
        
        weekday_spending = df[df['amount'] > 0].groupby('weekday')['amount'].sum().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])
        
        # Translate weekdays to Finnish
        finnish_weekdays = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai', 'Lauantai', 'Sunnuntai']
        
        fig = px.bar(
            x=finnish_weekdays,
            y=weekday_spending.values,
            title="Kulutus viikonpäivittäin",
            labels={'x': 'Viikonpäivä', 'y': 'Summa (€)'},
            color=weekday_spending.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⏰ Päivittäinen kulutusrytmi")
        
        if 'hour' in df.columns:
            hourly_spending = df[df['amount'] > 0].groupby('hour')['amount'].sum()
            
            fig = px.line(
                x=hourly_spending.index,
                y=hourly_spending.values,
                title="Kulutus kellonajan mukaan",
                labels={'x': 'Tunnit', 'y': 'Summa (€)'},
                markers=True
            )
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Kellonaikatietoja ei saatavilla")
    
    # Monthly trend analysis
    st.subheader("📊 Kuukausittaiset trendit")
    
    monthly_summary = df.groupby('month').agg({
        'amount': ['sum', 'count', 'mean']
    }).round(2)
    
    monthly_summary.columns = ['Kokonaissumma', 'Transaktioiden määrä', 'Keskiarvo']
    monthly_summary.index = monthly_summary.index.astype(str)
    
    # Calculate month-over-month changes
    monthly_summary['Muutos%'] = monthly_summary['Kokonaissumma'].pct_change() * 100
    monthly_summary = monthly_summary.fillna(0)
    
    st.dataframe(monthly_summary, use_container_width=True)
    
    # Spending velocity analysis
    st.subheader("🚀 Kulutusnopeuden analyysi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average days between transactions
        df_sorted = df.sort_values('transaction_date')
        time_diffs = df_sorted['transaction_date'].diff().dt.days.dropna()
        avg_days_between = time_diffs.mean()
        
        st.metric(
            "📅 Keskimääräinen väli transaktioiden välillä",
            f"{avg_days_between:.1f} päivää"
        )
    
    with col2:
        # Spending acceleration/deceleration
        recent_30_days = df[df['transaction_date'] >= (datetime.now() - timedelta(days=30))]
        previous_30_days = df[
            (df['transaction_date'] >= (datetime.now() - timedelta(days=60))) &
            (df['transaction_date'] < (datetime.now() - timedelta(days=30)))
        ]
        
        recent_spending = recent_30_days[recent_30_days['amount'] > 0]['amount'].sum()
        previous_spending = previous_30_days[previous_30_days['amount'] > 0]['amount'].sum()
        
        spending_change = ((recent_spending - previous_spending) / max(previous_spending, 1)) * 100
        
        st.metric(
            "📈 Kulutuksen muutos (30 pv)",
            f"{spending_change:+.1f}%",
            delta=f"€{recent_spending - previous_spending:+.2f}"
        )

def show_deep_analytics(api):
    """Display deep financial analysis."""
    st.subheader("🔍 Syväanalyysi")
    
    # Load data
    with st.spinner("Suoritetaan syväanalyysiä..."):
        transactions = api.get_transactions()
        categories = api.get_categories(include_stats=True)
    
    if not transactions:
        st.info("Ei transaktioita analysoitavaksi")
        return
    
    df = pd.DataFrame(transactions)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Category efficiency analysis
    st.subheader("📊 Kategorioiden tehokkuusanalyysi")
    
    if categories:
        category_stats = []
        for cat in categories:
            cat_transactions = [t for t in transactions if t.get('category_id') == cat['id']]
            if cat_transactions:
                total_amount = sum(t['amount'] for t in cat_transactions if t['amount'] > 0)
                transaction_count = len(cat_transactions)
                avg_amount = total_amount / transaction_count if transaction_count > 0 else 0
                
                category_stats.append({
                    'Kategoria': cat['name'],
                    'Kokonaissumma': total_amount,
                    'Transaktioita': transaction_count,
                    'Keskiarvo': avg_amount,
                    'Osuus kokonaismenoista': (total_amount / df[df['amount'] > 0]['amount'].sum()) * 100
                })
        
        if category_stats:
            cat_df = pd.DataFrame(category_stats).sort_values('Kokonaissumma', ascending=False)
            
            # Display top categories table
            st.dataframe(
                cat_df.round(2),
                use_container_width=True,
                column_config={
                    "Kokonaissumma": st.column_config.NumberColumn(format="€%.2f"),
                    "Keskiarvo": st.column_config.NumberColumn(format="€%.2f"),
                    "Osuus kokonaismenoista": st.column_config.NumberColumn(format="%.1f%%")
                }
            )
            
            # Category efficiency scatter plot
            fig = px.scatter(
                cat_df,
                x='Transaktioita',
                y='Keskiarvo',
                size='Kokonaissumma',
                hover_name='Kategoria',
                title="Kategorioiden tehokkuus (koko = kokonaissumma)",
                labels={'Transaktioita': 'Transaktioiden määrä', 'Keskiarvo': 'Keskimääräinen summa (€)'}
            )
            fig.update_layout(template='plotly_white', height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # Spending pattern analysis
    st.subheader("🎯 Kulutuskäyttäytymisen analyysi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction size distribution
        expenses = df[df['amount'] > 0]['amount']
        
        fig = px.histogram(
            expenses,
            nbins=20,
            title="Transaktioiden kokojakauma",
            labels={'value': 'Summa (€)', 'count': 'Lukumäärä'}
        )
        fig.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.write("**Tilastotiedot:**")
        st.write(f"- Mediaani: €{expenses.median():.2f}")
        st.write(f"- Keskiarvo: €{expenses.mean():.2f}")
        st.write(f"- Keskihajonta: €{expenses.std():.2f}")
        st.write(f"- Suurin transaktio: €{expenses.max():.2f}")
    
    with col2:
        # Spending concentration analysis
        expenses_sorted = expenses.sort_values(ascending=False)
        cumulative_pct = (expenses_sorted.cumsum() / expenses_sorted.sum()) * 100
        transaction_pct = (np.arange(1, len(expenses_sorted) + 1) / len(expenses_sorted)) * 100
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=transaction_pct,
            y=cumulative_pct,
            mode='lines',
            name='Kumulatiivinen kulutus',
            line=dict(color='blue', width=2)
        ))
        
        # Add 80/20 reference line
        fig.add_trace(go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode='lines',
            name='Täydellinen tasajakauma',
            line=dict(color='red', dash='dash'),
            opacity=0.5
        ))
        
        fig.update_layout(
            title="Kulutuksen keskittyminen (Pareto-analyysi)",
            xaxis_title="Transaktioiden osuus (%)",
            yaxis_title="Kumulatiivinen kulutus (%)",
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Pareto insights
        top_20_pct_transactions = int(len(expenses_sorted) * 0.2)
        top_20_spending = expenses_sorted.head(top_20_pct_transactions).sum()
        total_spending = expenses_sorted.sum()
        concentration_ratio = (top_20_spending / total_spending) * 100
        
        st.write("**Pareto-analyysi:**")
        st.write(f"- Top 20% transaktioista muodostaa {concentration_ratio:.1f}% kokonaiskulutuksesta")
        if concentration_ratio > 80:
            st.write("- ⚠️ Kulutus on erittäin keskittynyttä")
        elif concentration_ratio > 60:
            st.write("- ⚡ Kulutus on melko keskittynyttä")
        else:
            st.write("- ✅ Kulutus on tasaisesti jakautunutta")

def show_forecasting_analytics(api):
    """Display forecasting and predictive analytics."""
    st.subheader("🔮 Ennusteet ja projektiot")
    
    # Load historical data
    with st.spinner("Luodaan ennusteita..."):
        transactions = api.get_transactions()
    
    if not transactions:
        st.info("Ei riittävästi historiatietoja ennusteille")
        return
    
    df = pd.DataFrame(transactions)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Monthly spending forecast
    st.subheader("📈 Kuukausittainen kulutuennuste")
    
    # Group by month
    monthly_expenses = df[df['amount'] > 0].groupby(df['transaction_date'].dt.to_period('M'))['amount'].sum()
    
    if len(monthly_expenses) >= 3:
        # Simple moving average forecast
        forecast_months = 3
        recent_months = monthly_expenses.tail(3).mean()
        
        # Create forecast data
        last_month = monthly_expenses.index[-1]
        forecast_periods = []
        forecast_values = []
        
        for i in range(1, forecast_months + 1):
            next_month = last_month + i
            forecast_periods.append(next_month)
            # Simple trend-adjusted forecast
            trend = (monthly_expenses.tail(3).iloc[-1] - monthly_expenses.tail(3).iloc[0]) / 2
            forecast_values.append(recent_months + (trend * i))
        
        # Plot historical and forecast
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=[str(p) for p in monthly_expenses.index],
            y=monthly_expenses.values,
            mode='lines+markers',
            name='Historiallinen kulutus',
            line=dict(color='blue', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=[str(p) for p in forecast_periods],
            y=forecast_values,
            mode='lines+markers',
            name='Ennuste',
            line=dict(color='red', dash='dash', width=2)
        ))
        
        fig.update_layout(
            title="Kuukausittainen kulutuennuste",
            xaxis_title="Kuukausi",
            yaxis_title="Kulutus (€)",
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Forecast summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🎯 Seuraavan kuukauden ennuste",
                f"€{forecast_values[0]:.2f}"
            )
        
        with col2:
            st.metric(
                "📊 3 kuukauden keskiarvo",
                f"€{sum(forecast_values)/len(forecast_values):.2f}"
            )
        
        with col3:
            current_month_spending = monthly_expenses.iloc[-1]
            change_pct = ((forecast_values[0] - current_month_spending) / current_month_spending) * 100
            st.metric(
                "📈 Ennustettu muutos",
                f"{change_pct:+.1f}%"
            )
    else:
        st.info("Tarvitaan vähintään 3 kuukauden historiatietoja ennusteille")
    
    # Goal achievement projection
    st.subheader("🎯 Tavoitteiden saavuttamisennuste")
    
    # Calculate current savings rate
    recent_transactions = df[df['transaction_date'] >= (datetime.now() - timedelta(days=90))]
    if not recent_transactions.empty:
        monthly_income = recent_transactions[recent_transactions['amount'] < 0]['amount'].sum() / -3  # Negative amounts are income
        monthly_expenses = recent_transactions[recent_transactions['amount'] > 0]['amount'].sum() / 3
        monthly_savings = monthly_income - monthly_expenses
        
        if monthly_savings > 0:
            # Project to €100,000 goal
            target_amount = 100000
            current_savings = 0  # This would come from user's actual savings balance
            
            months_to_goal = (target_amount - current_savings) / monthly_savings
            years_to_goal = months_to_goal / 12
            target_date = datetime.now() + timedelta(days=months_to_goal * 30)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "💰 Kuukausittainen säästö",
                    f"€{monthly_savings:.2f}"
                )
            
            with col2:
                st.metric(
                    "⏰ Arvioitu aika tavoitteeseen",
                    f"{years_to_goal:.1f} vuotta"
                )
            
            with col3:
                st.metric(
                    "📅 Tavoitepäivä",
                    target_date.strftime("%m/%Y")
                )
            
            # Savings projection chart
            months_range = range(int(months_to_goal) + 1)
            projected_savings = [current_savings + (monthly_savings * month) for month in months_range]
            
            fig = px.line(
                x=months_range,
                y=projected_savings,
                title="Säästöjen kehitysennuste 100k€ tavoitteeseen",
                labels={'x': 'Kuukaudet tästä hetkestä', 'y': 'Säästöt (€)'}
            )
            
            # Add target line
            fig.add_hline(y=target_amount, line_dash="dash", line_color="red", 
                         annotation_text="100k€ tavoite")
            
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Nykyisellä kulutustasolla säästäminen on haastavaa. Harkitse budjettien tarkistamista.")

def show_ai_insights(api):
    """Display AI-powered insights and recommendations."""
    st.subheader("🤖 AI-pohjaiset oivallukset")
    
    # Load smart insights from API
    with st.spinner("AI analysoi taloudellista tilannettasi..."):
        try:
            # This would call the smart insights endpoint
            insights_response = api.request("GET", "/dashboard/insights/smart")
            insights = insights_response.get('insights', []) if insights_response else []
        except:
            insights = []
    
    if insights:
        st.success(f"🎯 AI löysi {len(insights)} oivallusta taloudellisesta tilanteestasi:")
        
        for i, insight in enumerate(insights, 1):
            with st.expander(f"💡 Oivallus {i}: {insight.get('title', 'Tuntematon')}"):
                insight_type = insight.get('type', 'general')
                
                # Different styling based on insight type
                if insight_type == 'achievement':
                    st.success(insight.get('message', ''))
                elif insight_type == 'alert':
                    st.warning(insight.get('message', ''))
                elif insight_type == 'spending_pattern':
                    st.info(insight.get('message', ''))
                else:
                    st.write(insight.get('message', ''))
                
                # Show recommendation if available
                if 'recommendation' in insight:
                    st.markdown(f"**💡 Suositus:** {insight['recommendation']}")
                
                # Show additional data if available
                if 'amount' in insight:
                    st.metric("Summa", f"€{insight['amount']:.2f}")
                if 'count' in insight:
                    st.metric("Lukumäärä", insight['count'])
                if 'progress' in insight:
                    st.progress(insight['progress'] / 100)
    else:
        st.info("AI-oivalluksia ei ole tällä hetkellä saatavilla. Lisää transaktioita saadaksesi henkilökohtaisia suosituksia.")
    
    # Manual AI analysis section
    st.subheader("🔍 Kysy AI:lta")
    
    user_question = st.text_input(
        "Kysy kysymys taloudellisesta tilanteestasi:",
        placeholder="Esim. 'Mihin kulutan eniten rahaa?' tai 'Miten voisin säästää enemmän?'"
    )
    
    if st.button("🤖 Analysoi", type="primary"):
        if user_question:
            with st.spinner("AI miettii vastaustasi..."):
                # This would integrate with an LLM service
                st.info("🚧 AI-chat-ominaisuus tulossa pian! Tällä hetkellä voit tarkastella automaattisia oivalluksia yllä.")
        else:
            st.warning("Kirjoita kysymys ensin.")
    
    # Savings optimization suggestions
    st.subheader("💡 Säästöoptimoinnin ehdotukset")
    
    optimization_tips = [
        {
            "title": "🏪 Kauppaostokset",
            "tip": "Suunnittele ostokset etukäteen ja tee ostoslista. Vältä nälkäisenä kauppaan menoa.",
            "potential_savings": "10-15%"
        },
        {
            "title": "☕ Kahvila- ja ravintolakulut",
            "tip": "Valmista kahvi kotona ja vie eväät töihin. Rajoita ulkona syömistä 1-2 kertaan viikossa.",
            "potential_savings": "20-30%"
        },
        {
            "title": "🚗 Liikenne",
            "tip": "Harkitse julkisten kulkuneuvojen käyttöä tai kimppakyytejä. Yhdistä useita asiointeja samaan matkaan.",
            "potential_savings": "15-25%"
        },
        {
            "title": "📱 Tilaukset ja jäsenyydet",
            "tip": "Käy läpi kaikki kuukausittaiset tilaukset. Peruuta käyttämättömät palvelut.",
            "potential_savings": "5-10%"
        },
        {
            "title": "⚡ Energia",
            "tip": "Alenna lämmitystä 1-2 astetta ja sammuta valot käyttämättömissä huoneissa.",
            "potential_savings": "8-12%"
        }
    ]
    
    for tip in optimization_tips:
        with st.expander(f"{tip['title']} - Säästöpotentiaali: {tip['potential_savings']}"):
            st.write(tip['tip'])
            st.success(f"💰 Arvioitu säästö: {tip['potential_savings']} kuukausittaisista kuluista") 