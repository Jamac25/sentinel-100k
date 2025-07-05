"""
Goals page for Personal Finance Agent Streamlit app.
Financial goal setting, tracking, and achievement management.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
import calendar

def show_goals_page(api):
    """Display comprehensive goals management page."""
    st.title("🎯 Tavoitteet")
    
    # Create tabs for different goal views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 100k€ päätavoite", "📊 Kaikki tavoitteet", "➕ Luo tavoite", "🎉 Saavutukset"
    ])
    
    with tab1:
        show_main_goal_tracking(api)
    
    with tab2:
        show_all_goals(api)
    
    with tab3:
        show_create_goal(api)
    
    with tab4:
        show_achievements(api)

def show_main_goal_tracking(api):
    """Display the main €100,000 savings goal tracking."""
    st.subheader("🏆 100 000€ säästötavoite")
    
    # Load goal data (this would come from the API)
    with st.spinner("Ladataan tavoitetietoja..."):
        try:
            # Get dashboard data for current savings calculation
            dashboard_data = api.get_dashboard_summary(period_days=365)
            
            # Mock data for the main goal - in real implementation this would come from goals API
            current_savings = 12500  # This would be calculated from actual user data
            target_amount = 100000
            progress_percentage = (current_savings / target_amount) * 100
            
            # Calculate monthly savings rate
            monthly_income = dashboard_data.get('total_income', 0) / 12 if dashboard_data else 0
            monthly_expenses = dashboard_data.get('total_expenses', 0) / 12 if dashboard_data else 0
            monthly_savings = monthly_income - monthly_expenses
            
            # Estimate time to goal
            if monthly_savings > 0:
                remaining_amount = target_amount - current_savings
                months_to_goal = remaining_amount / monthly_savings
                years_to_goal = months_to_goal / 12
                target_date = datetime.now() + timedelta(days=months_to_goal * 30)
            else:
                months_to_goal = float('inf')
                years_to_goal = float('inf')
                target_date = None
            
        except Exception as e:
            st.error(f"Virhe tavoitetietojen lataamisessa: {str(e)}")
            return
    
    # Main goal progress display
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    ">
        <h2 style="margin: 0; color: white;">🎯 Päätavoite: 100 000€</h2>
        <p style="margin: 0.5rem 0; opacity: 0.9;">Taloudellinen vapaus ja turvallisuus</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Nykyiset säästöt",
            f"€{current_savings:,.2f}",
            delta=f"€{monthly_savings:.2f}/kk" if monthly_savings > 0 else None
        )
    
    with col2:
        st.metric(
            "📈 Edistyminen",
            f"{progress_percentage:.1f}%",
            delta=f"{progress_percentage:.1f}% tavoitteesta"
        )
    
    with col3:
        if years_to_goal != float('inf'):
            st.metric(
                "⏰ Arvioitu aika",
                f"{years_to_goal:.1f} vuotta",
                delta=f"{months_to_goal:.0f} kuukautta"
            )
        else:
            st.metric(
                "⏰ Arvioitu aika",
                "∞",
                delta="Säästötahtia pitää nostaa"
            )
    
    with col4:
        remaining = target_amount - current_savings
        st.metric(
            "🎯 Jäljellä",
            f"€{remaining:,.2f}",
            delta=f"€{remaining/12:.0f}/kk keskimäärin" if remaining > 0 else "Tavoite saavutettu!"
        )
    
    # Progress bar
    st.subheader("📊 Edistymisen visualisointi")
    
    progress_bar_col1, progress_bar_col2 = st.columns([3, 1])
    
    with progress_bar_col1:
        # Custom progress bar
        progress_normalized = min(progress_percentage / 100, 1.0)
        st.progress(progress_normalized)
        
        # Milestone markers
        milestones = [10000, 25000, 50000, 75000, 100000]
        milestone_labels = ["10k€", "25k€", "50k€", "75k€", "100k€"]
        
        fig = go.Figure()
        
        # Progress bar
        fig.add_trace(go.Bar(
            x=[current_savings],
            y=['Edistyminen'],
            orientation='h',
            marker_color='#2ca02c',
            name='Saavutettu',
            text=f'€{current_savings:,.0f}',
            textposition='inside'
        ))
        
        # Remaining amount
        fig.add_trace(go.Bar(
            x=[target_amount - current_savings],
            y=['Edistyminen'],
            orientation='h',
            marker_color='#f0f0f0',
            name='Jäljellä',
            text=f'€{target_amount - current_savings:,.0f}',
            textposition='inside'
        ))
        
        # Add milestone markers
        for i, milestone in enumerate(milestones):
            color = '#2ca02c' if milestone <= current_savings else '#ff7f0e'
            fig.add_vline(x=milestone, line_dash="dash", line_color=color, 
                         annotation_text=milestone_labels[i])
        
        fig.update_layout(
            title="Säästötavoitteen edistyminen",
            xaxis_title="Summa (€)",
            barmode='stack',
            template='plotly_white',
            height=200,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with progress_bar_col2:
        # Goal status indicator
        if progress_percentage >= 100:
            st.success("🎉 TAVOITE SAAVUTETTU!")
        elif progress_percentage >= 75:
            st.success("🟢 Erinomaisesti!")
        elif progress_percentage >= 50:
            st.info("🟡 Hyvää vauhtia!")
        elif progress_percentage >= 25:
            st.warning("🟠 Jatka samaan malliin!")
        else:
            st.error("🔴 Tarvitaan lisää säästöjä!")
    
    # Savings projection
    st.subheader("📈 Säästöennuste")
    
    if monthly_savings > 0:
        # Create projection data
        months_range = range(0, min(int(months_to_goal) + 12, 120))  # Max 10 years
        projected_savings = [current_savings + (monthly_savings * month) for month in months_range]
        dates = [datetime.now() + timedelta(days=month * 30) for month in months_range]
        
        fig = px.line(
            x=dates,
            y=projected_savings,
            title="Säästöjen kehitysennuste nykyisellä tahdilla",
            labels={'x': 'Päivämäärä', 'y': 'Säästöt (€)'}
        )
        
        # Add target line
        fig.add_hline(y=target_amount, line_dash="dash", line_color="red", 
                     annotation_text="100k€ tavoite")
        
        # Add milestone lines
        for milestone in [25000, 50000, 75000]:
            if milestone > current_savings:
                fig.add_hline(y=milestone, line_dash="dot", line_color="orange", 
                             annotation_text=f"{milestone/1000:.0f}k€")
        
        fig.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Projection insights
        col1, col2 = st.columns(2)
        
        with col1:
            if target_date:
                st.info(f"📅 **Arvioitu saavutuspäivä:** {target_date.strftime('%B %Y')}")
            
            # Monthly target vs actual
            monthly_target_needed = remaining / max(months_to_goal, 1) if months_to_goal != float('inf') else 0
            if monthly_savings >= monthly_target_needed:
                st.success(f"✅ Säästötahti riittää! ({monthly_savings:.0f}€/kk vs {monthly_target_needed:.0f}€/kk)")
            else:
                shortfall = monthly_target_needed - monthly_savings
                st.warning(f"⚠️ Säästötahtia pitää nostaa {shortfall:.0f}€/kk")
        
        with col2:
            # Acceleration scenarios
            st.subheader("🚀 Kiihdytysskenaariot")
            
            scenarios = [
                ("Nykytahti", monthly_savings, months_to_goal),
                ("+€100/kk", monthly_savings + 100, remaining / (monthly_savings + 100) if monthly_savings + 100 > 0 else float('inf')),
                ("+€200/kk", monthly_savings + 200, remaining / (monthly_savings + 200) if monthly_savings + 200 > 0 else float('inf')),
                ("+€500/kk", monthly_savings + 500, remaining / (monthly_savings + 500) if monthly_savings + 500 > 0 else float('inf'))
            ]
            
            for scenario_name, monthly_rate, months in scenarios:
                if months != float('inf'):
                    years = months / 12
                    st.write(f"**{scenario_name}:** {years:.1f} vuotta")
                else:
                    st.write(f"**{scenario_name}:** ∞")
    else:
        st.warning("⚠️ Nykyisellä kulutustasolla säästäminen on haastavaa. Tarkista budjettisi!")

def show_all_goals(api):
    """Display all user goals."""
    st.subheader("📊 Kaikki tavoitteet")
    
    # Mock goals data - in real implementation this would come from goals API
    goals = [
        {
            "id": 1,
            "title": "100 000€ säästötavoite",
            "description": "Päätavoite taloudelliseen vapauteen",
            "target_amount": 100000,
            "current_amount": 12500,
            "target_date": "2030-12-31",
            "status": "active",
            "priority": "high"
        },
        {
            "id": 2,
            "title": "Hätävara",
            "description": "6 kuukauden elinkustannukset",
            "target_amount": 15000,
            "current_amount": 8500,
            "target_date": "2025-06-30",
            "status": "active",
            "priority": "high"
        },
        {
            "id": 3,
            "title": "Loma-matka",
            "description": "Japanin matka 2025",
            "target_amount": 3000,
            "current_amount": 1200,
            "target_date": "2025-08-01",
            "status": "active",
            "priority": "medium"
        }
    ]
    
    if goals:
        # Goals overview metrics
        total_target = sum(goal["target_amount"] for goal in goals)
        total_current = sum(goal["current_amount"] for goal in goals)
        overall_progress = (total_current / total_target) * 100 if total_target > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Tavoitteita yhteensä", len(goals))
        with col2:
            st.metric("💰 Tavoitesumma", f"€{total_target:,.0f}")
        with col3:
            st.metric("📈 Saavutettu", f"€{total_current:,.0f}")
        with col4:
            st.metric("📊 Kokonaisedistyminen", f"{overall_progress:.1f}%")
        
        # Goals list
        for goal in goals:
            progress = (goal["current_amount"] / goal["target_amount"]) * 100
            
            with st.expander(f"🎯 {goal['title']} - {progress:.1f}%"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Kuvaus:** {goal['description']}")
                    st.write(f"**Tavoitepäivä:** {goal['target_date']}")
                    
                    # Progress bar
                    st.progress(min(progress / 100, 1.0))
                    st.write(f"€{goal['current_amount']:,.0f} / €{goal['target_amount']:,.0f}")
                    
                    # Time to goal calculation
                    target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                    days_left = (target_date - datetime.now()).days
                    
                    if days_left > 0:
                        remaining_amount = goal['target_amount'] - goal['current_amount']
                        monthly_needed = remaining_amount / max(days_left / 30, 1)
                        st.write(f"**Tarvitaan:** €{monthly_needed:.0f}/kk ({days_left} päivää jäljellä)")
                    else:
                        st.write("**Tavoitepäivä on mennyt!**")
                
                with col2:
                    # Priority indicator
                    priority_colors = {
                        "high": "🔴 Korkea",
                        "medium": "🟡 Keskitaso", 
                        "low": "🟢 Matala"
                    }
                    st.write(f"**Prioriteetti:** {priority_colors.get(goal['priority'], goal['priority'])}")
                    
                    # Status
                    if progress >= 100:
                        st.success("✅ Saavutettu!")
                    elif progress >= 75:
                        st.success("🟢 Lähes valmis!")
                    elif progress >= 50:
                        st.info("🟡 Puolivälissä")
                    elif progress >= 25:
                        st.warning("🟠 Aloitettu")
                    else:
                        st.error("🔴 Alkuvaiheessa")
                    
                    # Action buttons
                    if st.button(f"📝 Muokkaa", key=f"edit_{goal['id']}"):
                        st.info("Muokkaustoiminto tulossa pian!")
                    
                    if st.button(f"💰 Lisää summa", key=f"add_{goal['id']}"):
                        st.info("Summan lisäystoiminto tulossa pian!")
    else:
        st.info("Ei tavoitteita asetettu. Luo ensimmäinen tavoitteesi!")

def show_create_goal(api):
    """Display goal creation interface."""
    st.subheader("➕ Luo uusi tavoite")
    
    with st.form("create_goal"):
        # Basic goal information
        col1, col2 = st.columns(2)
        
        with col1:
            goal_title = st.text_input(
                "🎯 Tavoitteen nimi *",
                placeholder="Esim. Uusi auto, Loma-matka, Hätävara"
            )
            
            goal_description = st.text_area(
                "📝 Kuvaus",
                placeholder="Kuvaile tavoitettasi..."
            )
            
            goal_type = st.selectbox(
                "📂 Tavoitteen tyyppi",
                ["Säästötavoite", "Velkojen maksu", "Investointi", "Kulutus", "Muu"]
            )
        
        with col2:
            target_amount = st.number_input(
                "💰 Tavoitesumma (€) *",
                min_value=1.0,
                max_value=1000000.0,
                value=5000.0,
                step=100.0
            )
            
            target_date = st.date_input(
                "📅 Tavoitepäivä *",
                value=date.today() + timedelta(days=365),
                min_value=date.today()
            )
            
            priority = st.selectbox(
                "⭐ Prioriteetti",
                ["Korkea", "Keskitaso", "Matala"]
            )
        
        # Advanced settings
        with st.expander("🔧 Lisäasetukset"):
            col1, col2 = st.columns(2)
            
            with col1:
                auto_track = st.checkbox(
                    "📊 Automaattinen seuranta",
                    value=True,
                    help="Seuraa automaattisesti edistymistä kategorioiden perusteella"
                )
                
                send_reminders = st.checkbox(
                    "🔔 Muistutukset",
                    value=True,
                    help="Lähetä säännöllisiä muistutuksia"
                )
            
            with col2:
                icon = st.selectbox(
                    "🎨 Ikoni",
                    ["🎯", "💰", "🏠", "🚗", "✈️", "🎓", "💍", "🏖️", "💻", "📱"]
                )
                
                color = st.color_picker(
                    "🎨 Väri",
                    value="#10B981"
                )
        
        # Milestone creation
        st.subheader("🏁 Välitavoitteet")
        
        create_milestones = st.checkbox(
            "Luo automaattiset välitavoitteet",
            value=True,
            help="Luo 25%, 50%, 75% välitavoitteet"
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Luo tavoite", type="primary", use_container_width=True)
        
        if submitted:
            if goal_title and target_amount > 0:
                # Calculate monthly target
                days_to_target = (target_date - date.today()).days
                monthly_target = target_amount / max(days_to_target / 30, 1) if days_to_target > 0 else 0
                
                # Display goal summary
                st.success("✅ Tavoite luotu onnistuneesti!")
                
                with st.expander("📋 Tavoitteen yhteenveto"):
                    st.write(f"**Nimi:** {goal_title}")
                    st.write(f"**Summa:** €{target_amount:,.2f}")
                    st.write(f"**Päivämäärä:** {target_date}")
                    st.write(f"**Kuukausittainen tavoite:** €{monthly_target:.2f}")
                    st.write(f"**Prioriteetti:** {priority}")
                    
                    if create_milestones:
                        st.write("**Välitavoitteet:**")
                        milestones = [0.25, 0.5, 0.75]
                        for milestone in milestones:
                            amount = target_amount * milestone
                            st.write(f"- {milestone*100:.0f}%: €{amount:,.2f}")
                
                st.info("🔄 Siirry 'Kaikki tavoitteet' -välilehdelle nähdäksesi uuden tavoitteesi!")
            else:
                st.error("❌ Täytä vaaditut kentät (nimi ja summa)")

def show_achievements(api):
    """Display achievements and milestones."""
    st.subheader("🎉 Saavutukset")
    
    # Mock achievements data
    achievements = [
        {
            "title": "🥇 Ensimmäinen tavoite",
            "description": "Loit ensimmäisen säästötavoitteesi",
            "date": "2024-01-15",
            "type": "milestone"
        },
        {
            "title": "💰 10k€ säästöjä",
            "description": "Saavutit 10 000€ säästöjen välitavoitteen",
            "date": "2024-11-20",
            "type": "amount"
        },
        {
            "title": "📊 100 transaktiota",
            "description": "Kirjasit 100 transaktiota järjestelmään",
            "date": "2024-10-05",
            "type": "activity"
        },
        {
            "title": "🔥 30 päivän putki",
            "description": "Säästit rahaa 30 päivää peräkkäin",
            "date": "2024-09-12",
            "type": "streak"
        }
    ]
    
    # Upcoming achievements
    upcoming = [
        {
            "title": "💎 25k€ säästöjä",
            "description": "Saavuta 25 000€ säästöjen välitavoite",
            "progress": 50,
            "requirement": "€25,000"
        },
        {
            "title": "📈 6 kuukautta käytössä",
            "description": "Käytä sovellusta 6 kuukautta",
            "progress": 75,
            "requirement": "180 päivää"
        },
        {
            "title": "🎯 Ensimmäinen tavoite saavutettu",
            "description": "Saavuta ensimmäinen asettamasi tavoite",
            "progress": 40,
            "requirement": "100% tavoitteesta"
        }
    ]
    
    # Display achieved
    if achievements:
        st.subheader("🏆 Saavutetut")
        
        for achievement in achievements:
            with st.expander(f"{achievement['title']} - {achievement['date']}"):
                st.write(achievement['description'])
                
                # Achievement type badge
                type_badges = {
                    "milestone": "🎯 Välitavoite",
                    "amount": "💰 Summa",
                    "activity": "📊 Aktiivisuus",
                    "streak": "🔥 Putki"
                }
                st.badge(type_badges.get(achievement['type'], achievement['type']))
    
    # Display upcoming
    if upcoming:
        st.subheader("🎯 Tulevat saavutukset")
        
        for achievement in upcoming:
            with st.expander(f"{achievement['title']} - {achievement['progress']}%"):
                st.write(achievement['description'])
                st.write(f"**Vaatimus:** {achievement['requirement']}")
                
                # Progress bar
                st.progress(achievement['progress'] / 100)
                st.write(f"Edistyminen: {achievement['progress']}%")
    
    # Achievement statistics
    st.subheader("📊 Saavutustilastot")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏆 Saavutuksia yhteensä", len(achievements))
    
    with col2:
        st.metric("🎯 Odottaa saavuttamista", len(upcoming))
    
    with col3:
        # Calculate achievement rate
        total_possible = len(achievements) + len(upcoming)
        achievement_rate = (len(achievements) / total_possible) * 100 if total_possible > 0 else 0
        st.metric("📈 Saavutusprosentti", f"{achievement_rate:.1f}%")
    
    with col4:
        # Latest achievement
        if achievements:
            latest = max(achievements, key=lambda x: x['date'])
            st.metric("🕒 Viimeisin saavutus", latest['date']) 