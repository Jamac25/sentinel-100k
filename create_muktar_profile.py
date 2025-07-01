#!/usr/bin/env python3
"""
Create Muktar's profile in Sentinel 100K backend database.
Initializes user with real financial data and personalized settings.
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime

# Add the personal_finance_agent to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'personal_finance_agent'))

from app.models import User, AgentState, Goal, GoalType, GoalStatus, Transaction, Category
from app.db.base import Base
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_muktar_profile():
    """Create Muktar's complete profile in the database."""
    
    print("🚀 Creating Muktar's Profile in Sentinel 100K")
    print("=" * 50)
    
    # Create database connection
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if Muktar already exists
        existing_user = db.query(User).filter(User.username == "muktar").first()
        if existing_user:
            print("❌ Muktar already exists in database!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            return existing_user.id
        
        # Create Muktar's user profile
        muktar = User(
            username="muktar",
            email="muktar@terveystalo.fi",
            hashed_password=hash_password("sentinel123"),  # Default password
            full_name="Muktar",
            language="fi",
            timezone="Europe/Helsinki",
            preferred_currency="EUR",
            
            # Financial profile from onboarding
            current_savings=220.0,  # Current savings
            savings_goal=100000.0,  # 100K goal
            monthly_income=4700.0,  # Total monthly income
            
            # Income breakdown
            primary_job_income=3200.0,    # Terveystalo salary
            business_income=1500.0,       # Own business
            other_income=0.0,
            
            # Expense breakdown (per month)
            housing_costs=1720.0,         # 1500 rent + 220 utilities
            food_costs=500.0,             # Food budget
            transport_costs=200.0,        # Transport
            entertainment_costs=150.0,    # Entertainment + clothing
            family_support=500.0,         # Support to children in Somalia
            other_expenses=0.0,
            
            # Personal information
            profession="Healthcare Professional & Entrepreneur",
            workplace="Terveystalo + Own Business",
            family_info="Supports children in Somalia with €500/month",
            financial_goals="Achieve €100,000 savings while maintaining family support. Focus on long-term financial security and children's future."
        )
        
        db.add(muktar)
        db.flush()  # Get the user ID
        
        print(f"✅ Created user profile for Muktar (ID: {muktar.id})")
        print(f"   📧 Email: {muktar.email}")
        print(f"   💰 Monthly income: €{muktar.monthly_income:,.0f}")
        print(f"   💸 Monthly expenses: €{muktar.total_monthly_expenses:,.0f}")
        print(f"   💳 Monthly savings: €{muktar.monthly_savings_potential:,.0f}")
        print(f"   📊 Savings rate: {muktar.savings_rate_percentage:.1f}%")
        print(f"   🎯 Months to 100K goal: {muktar.months_to_goal:.0f} months")
        
        # Create personalized Agent State
        agent_state = AgentState(
            user_id=muktar.id,
            mood_score=75.0,  # High because of excellent savings rate
            energy_level=85.0,  # High energy due to dual income
            stress_level=30.0,  # Some stress due to family responsibilities
            confidence_level=80.0,  # High confidence due to good financial management
            
            # Context for AI responses
            last_financial_health_score=85.0,  # Excellent financial health
            days_since_goal_progress=0,
            consecutive_budget_adherence_days=30,
            recent_positive_actions=5,
            recent_concerning_actions=0,
            
            # Response style for Finnish user with family responsibilities
            response_style="encouraging",
            message_tone="friendly",
            
            # User preferences tailored to Muktar
            user_preferences={
                "communication_style": "supportive",
                "language": "finnish",
                "notification_frequency": "moderate",
                "advice_type": "family_focused",
                "cultural_context": "somalia_finland",
                "priority_goals": ["family_support", "long_term_savings", "business_growth"],
                "recognition_topics": ["family_responsibility", "dual_income", "excellent_savings_rate"]
            }
        )
        
        db.add(agent_state)
        print("✅ Created personalized Agent State")
        
        # Create the main savings goal
        main_goal = Goal(
            title="Saavuta €100,000 säästöt",
            description="Päätavoite taloudellisen turvallisuuden ja vapauden rakentamiseksi, samalla kun tuen lapsia Somaliassa",
            goal_type=GoalType.SAVINGS,
            target_amount=100000.0,
            current_amount=220.0,  # Current savings
            monthly_target=1630.0,  # Realistic monthly savings
            user_id=muktar.id,
            status=GoalStatus.ACTIVE,
            start_date=datetime.now(),  # Set start date
            icon="🎯",
            color="#10B981"
        )
        
        db.add(main_goal)
        print("✅ Created main savings goal (€100,000)")
        
        # Create sample transactions based on Muktar's profile
        sample_transactions = [
            # Income transactions
            {
                "description": "Terveystalo palkka",
                "amount": 3200.0,
                "category": "Palkka",
                "is_income": True
            },
            {
                "description": "Oma yritys - asiakkaita",
                "amount": 1500.0,
                "category": "Yritystoiminta",
                "is_income": True
            },
            # Expense transactions
            {
                "description": "Vuokra",
                "amount": 1500.0,
                "category": "Asuminen",
                "is_income": False
            },
            {
                "description": "Sähkö ja vesi",
                "amount": 220.0,
                "category": "Asuminen",
                "is_income": False
            },
            {
                "description": "Ruokaostokset - K-Market",
                "amount": 500.0,
                "category": "Ruoka ja juoma",
                "is_income": False
            },
            {
                "description": "HSL-kuukausilippu",
                "amount": 200.0,
                "category": "Kuljetus",
                "is_income": False
            },
            {
                "description": "Tuki lapsille Somaliassa",
                "amount": 500.0,
                "category": "Perheen tuki",
                "is_income": False
            },
            {
                "description": "Vapaa-aika ja vaatteet",
                "amount": 150.0,
                "category": "Vapaa-aika",
                "is_income": False
            }
        ]
        
        print("✅ Creating sample transactions...")
        for i, trans_data in enumerate(sample_transactions, 1):
            # Create transaction
            transaction = Transaction(
                description=trans_data["description"],
                amount=trans_data["amount"],
                transaction_date=datetime.now(),
                user_id=muktar.id,
                is_income=trans_data["is_income"],
                processing_notes=f"Kuukausittainen {'tulo' if trans_data['is_income'] else 'meno'}"
            )
            db.add(transaction)
            print(f"   {i}. {trans_data['description']}: €{trans_data['amount']:,.0f}")
        
        # Commit all changes
        db.commit()
        
        print("\n🎉 MUKTAR'S PROFILE CREATED SUCCESSFULLY!")
        print("=" * 50)
        print(f"👤 Username: muktar")
        print(f"🔑 Password: sentinel123")
        print(f"💰 Total Monthly Income: €{muktar.monthly_income:,.0f}")
        print(f"💸 Total Monthly Expenses: €{muktar.total_monthly_expenses:,.0f}")
        print(f"💳 Monthly Savings: €{muktar.monthly_savings_potential:,.0f}")
        print(f"📊 Savings Rate: {muktar.savings_rate_percentage:.1f}%")
        print(f"🎯 Time to €100K Goal: {muktar.months_to_goal:.0f} months ({muktar.months_to_goal/12:.1f} years)")
        print(f"🌍 Family Support: €500/month to children in Somalia")
        print(f"🏥 Primary Job: Terveystalo (€3,200/month)")
        print(f"💼 Business Income: €1,500/month")
        print("\n✅ Ready for Sentinel 100K backend integration!")
        
        return muktar.id
        
    except Exception as e:
        print(f"❌ Error creating Muktar's profile: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_muktar_profile() 