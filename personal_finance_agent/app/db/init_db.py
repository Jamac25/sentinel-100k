"""
Database initialization functions.
Creates tables and populates with default data.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ..core.config import settings
from .base import Base
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is imported from .base

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    try:
        # Import all models to ensure they are registered
        from ..models import Category, Goal, GoalType, GoalStatus, User, AgentState
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default categories
        init_default_categories()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def init_default_categories():
    """Initialize default Finnish categories"""
    try:
        db = SessionLocal()
        
        # Check if categories already exist
        from ..models.category import Category
        existing_categories = db.query(Category).count()
        
        if existing_categories == 0:
            # Default Finnish categories
            default_categories = [
                {"name": "Ruoka ja juoma", "type": "expense", "color": "#FF6B6B"},
                {"name": "Kuljetus", "type": "expense", "color": "#4ECDC4"},
                {"name": "Asuminen", "type": "expense", "color": "#45B7D1"},
                {"name": "Vapaa-aika", "type": "expense", "color": "#96CEB4"},
                {"name": "Terveys", "type": "expense", "color": "#FFEAA7"},
                {"name": "Vaatteet", "type": "expense", "color": "#DDA0DD"},
                {"name": "Teknologia", "type": "expense", "color": "#98D8C8"},
                {"name": "Koulutus", "type": "expense", "color": "#F7DC6F"},
                {"name": "Sijoitukset", "type": "expense", "color": "#BB8FCE"},
                {"name": "Vakuutukset", "type": "expense", "color": "#85C1E9"},
                {"name": "Palkka", "type": "income", "color": "#82E0AA"},
                {"name": "Freelance", "type": "income", "color": "#F8C471"},
                {"name": "Sijoitukset", "type": "income", "color": "#85C1E9"},
                {"name": "Myynti", "type": "income", "color": "#F1948A"},
                {"name": "Lahjat", "type": "income", "color": "#D7BDE2"},
                {"name": "Korot", "type": "income", "color": "#A9DFBF"},
                {"name": "Palkkiot", "type": "income", "color": "#F9E79F"},
                {"name": "Rentoutus", "type": "income", "color": "#AED6F1"},
                {"name": "Muut tulot", "type": "income", "color": "#D5A6BD"},
                {"name": "Luottokortti", "type": "liability", "color": "#E74C3C"},
                {"name": "Laina", "type": "liability", "color": "#C0392B"},
                {"name": "Laskut", "type": "liability", "color": "#E67E22"}
            ]
            
            # Remove duplicate 'Sijoitukset' category
            default_categories = [cat for cat in default_categories if not (cat['name'] == 'Sijoitukset' and cat['type'] == 'income')]

            for cat_data in default_categories:
                # Convert 'type' to 'is_income'
                cat_data['is_income'] = cat_data.pop('type') == 'income'
                category = Category(**cat_data)
                db.add(category)
            
            db.commit()
            logger.info(f"Initialized {len(default_categories)} default categories")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error initializing default categories: {e}")
        if db:
            db.rollback()
            db.close()

def create_default_categories(db):
    """Create default expense and income categories."""
    logger.info("Creating default categories...")
    
    # Default expense categories
    expense_categories = [
        {"name": "Groceries", "description": "Food and grocery shopping", "is_essential": True, "color": "#10B981", "icon": "🛒", "keywords": "market,grocery,food,supermarket,k-market,s-market,lidl,prisma"},
        {"name": "Rent", "description": "Housing rent and utilities", "is_essential": True, "color": "#3B82F6", "icon": "🏠", "keywords": "rent,housing,apartment,utilities,electricity,water,heating"},
        {"name": "Transportation", "description": "Public transport, fuel, parking", "is_essential": True, "color": "#F59E0B", "icon": "🚗", "keywords": "bus,train,metro,fuel,parking,taxi,uber,transport"},
        {"name": "Healthcare", "description": "Medical expenses and pharmacy", "is_essential": True, "color": "#EF4444", "icon": "🏥", "keywords": "doctor,pharmacy,medicine,hospital,healthcare,medical"},
        {"name": "Dining Out", "description": "Restaurants and takeout", "is_essential": False, "color": "#8B5CF6", "icon": "🍽️", "keywords": "restaurant,cafe,takeout,delivery,food,dining"},
        {"name": "Entertainment", "description": "Movies, games, hobbies", "is_essential": False, "color": "#EC4899", "icon": "🎬", "keywords": "movie,game,hobby,entertainment,cinema,theatre,spotify,netflix"},
        {"name": "Shopping", "description": "Clothing and personal items", "is_essential": False, "color": "#6366F1", "icon": "🛍️", "keywords": "clothes,clothing,shoes,fashion,shopping,personal"},
        {"name": "Education", "description": "Courses, books, learning", "is_essential": False, "color": "#059669", "icon": "📚", "keywords": "course,book,education,learning,school,university"},
        {"name": "Subscriptions", "description": "Monthly subscriptions and services", "is_essential": False, "color": "#DC2626", "icon": "📱", "keywords": "subscription,service,monthly,netflix,spotify,phone,internet"},
        {"name": "Insurance", "description": "Insurance premiums", "is_essential": True, "color": "#1F2937", "icon": "🛡️", "keywords": "insurance,premium,life,health,car,home"},
        {"name": "Savings", "description": "Money saved or invested", "is_essential": True, "color": "#047857", "icon": "💰", "keywords": "savings,investment,invest,save,deposit"},
        {"name": "Gifts", "description": "Gifts and donations", "is_essential": False, "color": "#BE185D", "icon": "🎁", "keywords": "gift,present,donation,charity,birthday"},
        {"name": "Travel", "description": "Travel and vacation expenses", "is_essential": False, "color": "#0891B2", "icon": "✈️", "keywords": "travel,vacation,holiday,flight,hotel,trip"},
        {"name": "Personal Care", "description": "Haircut, cosmetics, hygiene", "is_essential": True, "color": "#7C2D12", "icon": "💄", "keywords": "haircut,cosmetics,hygiene,personal,care,beauty,salon"},
        {"name": "Other", "description": "Miscellaneous expenses", "is_essential": False, "color": "#6B7280", "icon": "❓", "keywords": "other,misc,miscellaneous,unknown"},
    ]
    
    # Default income categories
    income_categories = [
        {"name": "Salary", "description": "Primary employment income", "is_income": True, "is_essential": True, "color": "#10B981", "icon": "💼", "keywords": "salary,wage,employment,work,job,payroll"},
        {"name": "Freelance", "description": "Freelance and contract work", "is_income": True, "is_essential": False, "color": "#8B5CF6", "icon": "💻", "keywords": "freelance,contract,consulting,gig,project"},
        {"name": "Investment", "description": "Investment returns and dividends", "is_income": True, "is_essential": False, "color": "#F59E0B", "icon": "📈", "keywords": "investment,dividend,return,stock,crypto,interest"},
        {"name": "Business", "description": "Business income", "is_income": True, "is_essential": False, "color": "#3B82F6", "icon": "🏢", "keywords": "business,revenue,sales,profit,company"},
        {"name": "Gift Received", "description": "Money received as gifts", "is_income": True, "is_essential": False, "color": "#EC4899", "icon": "🎁", "keywords": "gift,received,present,money,birthday"},
        {"name": "Refund", "description": "Refunds and cashbacks", "is_income": True, "is_essential": False, "color": "#059669", "icon": "↩️", "keywords": "refund,cashback,return,reimburse"},
        {"name": "Other Income", "description": "Other sources of income", "is_income": True, "is_essential": False, "color": "#6B7280", "icon": "💡", "keywords": "other,income,bonus,miscellaneous"},
    ]
    
    # Create categories
    for cat_data in expense_categories + income_categories:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    db.commit()
    logger.info(f"Created {len(expense_categories)} expense and {len(income_categories)} income categories.")


def create_default_goal(user_id: int, db):
    """Create the default €100,000 savings goal for a new user."""
    logger.info(f"Creating default goal for user {user_id}...")
    
    # Check if user already has a primary goal
    existing_goal = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.goal_type == GoalType.SAVINGS,
        Goal.target_amount == 100000.0
    ).first()
    
    if not existing_goal:
        goal = Goal(
            title="Save €100,000",
            description="Primary savings goal to build financial security and freedom",
            goal_type=GoalType.SAVINGS,
            target_amount=100000.0,
            current_amount=0.0,
            monthly_target=2000.0,  # Suggested monthly target
            user_id=user_id,
            status=GoalStatus.ACTIVE,
            icon="🎯",
            color="#10B981"
        )
        db.add(goal)
        
        # Create milestones
        milestones = [
            {"title": "First €1,000", "percentage": 1.0, "icon": "🌱"},
            {"title": "€5,000 Emergency Fund", "percentage": 5.0, "icon": "🛡️"},
            {"title": "€10,000 Milestone", "percentage": 10.0, "icon": "💪"},
            {"title": "Quarter Way There", "percentage": 25.0, "icon": "⭐"},
            {"title": "Halfway Point", "percentage": 50.0, "icon": "🎉"},
            {"title": "Three Quarters", "percentage": 75.0, "icon": "🚀"},
            {"title": "Almost There", "percentage": 90.0, "icon": "🏆"},
        ]
        
        for milestone_data in milestones:
            milestone = goal.create_milestone(
                title=milestone_data["title"],
                percentage=milestone_data["percentage"]
            )
            milestone.icon = milestone_data["icon"]
            db.add(milestone)
        
        db.commit()
        logger.info(f"Created default goal and {len(milestones)} milestones for user {user_id}.")


def initialize_agent_state(user_id: int, db):
    """Initialize agent state for a new user."""
    logger.info(f"Initializing agent state for user {user_id}...")
    
    existing_state = db.query(AgentState).filter(AgentState.user_id == user_id).first()
    if not existing_state:
        agent_state = AgentState(
            user_id=user_id,
            mood_score=60.0,  # Start optimistic
            energy_level=80.0,
            stress_level=20.0,
            confidence_level=75.0,
            user_preferences={
                "communication_style": "friendly",
                "notification_frequency": "moderate",
                "advice_type": "balanced"
            }
        )
        db.add(agent_state)
        db.commit()
        logger.info(f"Initialized agent state for user {user_id}.")


def setup_new_user(user_id: int):
    """Set up default data for a new user."""
    logger.info(f"Setting up new user {user_id}...")
    
    db = SessionLocal()
    try:
        create_default_goal(user_id, db)
        initialize_agent_state(user_id, db)
        logger.info(f"New user {user_id} setup completed.")
    except Exception as e:
        logger.error(f"Error setting up new user {user_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Can be run directly to initialize database
    init_db() 