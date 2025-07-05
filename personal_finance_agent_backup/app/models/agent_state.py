"""
AgentState model for the agent's personality and emotional state.
Implements the "Tamagotchi-like" personality system.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime
from app.db.base import Base


class AgentMood(PyEnum):
    """Agent emotional states."""
    EUPHORIC = "euphoric"       # 90-100: Exceptional progress
    HAPPY = "happy"             # 70-89: Good progress
    NORMAL = "normal"           # 40-69: Steady progress
    CONCERNED = "concerned"     # 20-39: Some issues
    ANXIOUS = "anxious"         # 10-19: Major concerns
    DISTRESSED = "distressed"   # 0-9: Critical situation


class AgentPersonality(PyEnum):
    """Agent personality traits."""
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"
    MOTIVATIONAL = "motivational"
    STRICT = "strict"
    FRIENDLY = "friendly"


class AgentState(Base):
    """
    AgentState model for storing the agent's current emotional and personality state.
    Implements the emotional engagement system that responds to user's financial behavior.
    """
    __tablename__ = "agent_states"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core emotional state
    mood_score = Column(Float, nullable=False, default=50.0)  # 0-100 scale
    current_mood = Column(Enum(AgentMood), default=AgentMood.NORMAL, index=True)
    personality_type = Column(Enum(AgentPersonality), default=AgentPersonality.ENCOURAGING)
    
    # Detailed state information
    energy_level = Column(Float, default=75.0)  # 0-100, affects response enthusiasm
    stress_level = Column(Float, default=25.0)  # 0-100, affects message tone
    confidence_level = Column(Float, default=70.0)  # 0-100, affects advice certainty
    
    # Context for mood calculation
    last_financial_health_score = Column(Float, nullable=True)
    days_since_goal_progress = Column(Integer, default=0)
    consecutive_budget_adherence_days = Column(Integer, default=0)
    recent_positive_actions = Column(Integer, default=0)  # Count of recent positive actions
    recent_concerning_actions = Column(Integer, default=0)  # Count of concerning actions
    
    # Behavioral state
    last_interaction_type = Column(String, nullable=True)  # Type of last user interaction
    response_style = Column(String, default="balanced")  # current, encouraging, strict, analytical
    message_tone = Column(String, default="friendly")  # friendly, professional, casual
    
    # Achievement and gamification state
    current_streak_type = Column(String, nullable=True)  # What kind of streak user is on
    current_streak_days = Column(Integer, default=0)
    total_achievements_unlocked = Column(Integer, default=0)
    last_achievement = Column(String, nullable=True)
    
    # Agent memory and learning
    user_preferences = Column(JSON, nullable=True)  # Learned user preferences
    successful_advice_patterns = Column(JSON, nullable=True)  # What advice worked
    communication_preferences = Column(JSON, nullable=True)  # How user likes to be communicated with
    
    # State change tracking
    mood_history = Column(JSON, nullable=True)  # Recent mood score history
    last_mood_change = Column(DateTime(timezone=True), nullable=True)
    mood_change_reason = Column(String, nullable=True)  # What triggered last mood change
    
    # Activation and intervention flags
    needs_user_attention = Column(Boolean, default=False)  # Should prompt user interaction
    intervention_required = Column(Boolean, default=False)  # Critical situation requiring action
    celebration_pending = Column(Boolean, default=False)  # Positive achievement to celebrate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_calculation = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="agent_state")
    
    def __repr__(self):
        return f"<AgentState(id={self.id}, user_id={self.user_id}, mood={self.current_mood}, score={self.mood_score})>"
    
    @property
    def mood_emoji(self):
        """Get emoji representation of current mood."""
        mood_emojis = {
            AgentMood.EUPHORIC: "🎉",
            AgentMood.HAPPY: "😊",
            AgentMood.NORMAL: "😐",
            AgentMood.CONCERNED: "😟",
            AgentMood.ANXIOUS: "😰",
            AgentMood.DISTRESSED: "😱"
        }
        return mood_emojis.get(self.current_mood, "😐")
    
    @property
    def is_happy(self):
        """Check if agent is in a positive mood."""
        return self.current_mood in [AgentMood.HAPPY, AgentMood.EUPHORIC]
    
    @property
    def is_concerned(self):
        """Check if agent is worried about user's finances."""
        return self.current_mood in [AgentMood.CONCERNED, AgentMood.ANXIOUS, AgentMood.DISTRESSED]
    
    @property
    def needs_intervention(self):
        """Check if agent thinks intervention is needed."""
        return self.intervention_required or self.current_mood == AgentMood.DISTRESSED
    
    def update_mood_score(self, new_score: float, reason: str = None):
        """Update mood score and recalculate emotional state."""
        # Clamp score to valid range
        new_score = max(0.0, min(100.0, new_score))
        
        # Track mood history
        if not self.mood_history:
            self.mood_history = []
        
        self.mood_history.append({
            "timestamp": datetime.now().isoformat(),
            "score": self.mood_score,
            "new_score": new_score,
            "reason": reason
        })
        
        # Keep only last 30 mood changes
        if len(self.mood_history) > 30:
            self.mood_history = self.mood_history[-30:]
        
        self.mood_score = new_score
        self.last_mood_change = func.now()
        if reason:
            self.mood_change_reason = reason
        
        # Update mood enum based on score
        self._update_mood_enum()
        self._update_behavioral_flags()
        self.last_calculation = func.now()
    
    def _update_mood_enum(self):
        """Update mood enum based on current score."""
        if self.mood_score >= 90:
            self.current_mood = AgentMood.EUPHORIC
        elif self.mood_score >= 70:
            self.current_mood = AgentMood.HAPPY
        elif self.mood_score >= 40:
            self.current_mood = AgentMood.NORMAL
        elif self.mood_score >= 20:
            self.current_mood = AgentMood.CONCERNED
        elif self.mood_score >= 10:
            self.current_mood = AgentMood.ANXIOUS
        else:
            self.current_mood = AgentMood.DISTRESSED
    
    def _update_behavioral_flags(self):
        """Update behavioral flags based on current state."""
        # Reset flags
        self.needs_user_attention = False
        self.intervention_required = False
        self.celebration_pending = False
        
        # Set flags based on mood and context
        if self.current_mood == AgentMood.DISTRESSED:
            self.intervention_required = True
            self.needs_user_attention = True
        elif self.current_mood == AgentMood.ANXIOUS:
            self.needs_user_attention = True
        elif self.current_mood == AgentMood.EUPHORIC:
            self.celebration_pending = True
    
    def get_personality_response_style(self):
        """Get response style based on personality and mood."""
        if self.personality_type == AgentPersonality.ENCOURAGING:
            if self.is_happy:
                return "enthusiastic"
            elif self.is_concerned:
                return "supportive"
            else:
                return "encouraging"
        elif self.personality_type == AgentPersonality.ANALYTICAL:
            return "data_driven"
        elif self.personality_type == AgentPersonality.MOTIVATIONAL:
            return "inspiring"
        elif self.personality_type == AgentPersonality.STRICT:
            if self.is_concerned:
                return "firm"
            else:
                return "direct"
        else:  # FRIENDLY
            return "casual"
    
    def record_user_interaction(self, interaction_type: str, was_positive: bool):
        """Record user interaction and adjust state accordingly."""
        self.last_interaction_type = interaction_type
        
        if was_positive:
            self.recent_positive_actions += 1
            # Slight mood boost for positive interactions
            self.update_mood_score(min(self.mood_score + 2, 100), f"Positive interaction: {interaction_type}")
        else:
            # Don't penalize user for seeking help or asking questions
            pass
    
    def update_streak(self, streak_type: str, days: int):
        """Update current achievement streak."""
        self.current_streak_type = streak_type
        self.current_streak_days = days
        
        # Mood boost for maintaining streaks
        if days > 0 and days % 7 == 0:  # Weekly milestone
            boost = min(days / 7 * 3, 15)  # Up to 15 point boost
            self.update_mood_score(min(self.mood_score + boost, 100), f"Maintained {streak_type} streak for {days} days") 