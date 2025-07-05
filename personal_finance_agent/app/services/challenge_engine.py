"""
Sentinel Challenge Engine™ - Gamified Financial Challenges
Integrates with IdeaEngine, LearningEngine, and Watchdog for personalized challenges
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
from ..services.event_bus import EventType, publish_event
import logging
import json
import random
import asyncio
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ChallengeType(Enum):
    """Challenge types for different financial goals"""
    SAVINGS = "savings"
    INCOME = "income"
    SPENDING = "spending"
    INVESTMENT = "investment"
    DEBT = "debt"
    HABIT = "habit"

class ChallengeDifficulty(Enum):
    """Challenge difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class Challenge:
    """Challenge data structure"""
    id: str
    title: str
    description: str
    challenge_type: ChallengeType
    difficulty: ChallengeDifficulty
    duration_days: int
    target_amount: float
    reward_points: int
    requirements: List[str]
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    progress: float = 0.0
    completed: bool = False

class ChallengeEngine:
    """
    Sentinel Challenge Engine™ - Gamified Financial Challenges
    
    Features:
    - Personalized challenges based on user behavior
    - Integration with IdeaEngine for actionable tasks
    - LearningEngine integration for adaptive difficulty
    - Watchdog integration for real-time monitoring
    - Event-driven architecture for seamless integration
    """
    
    def __init__(self):
        self.active_challenges = {}  # user_id -> List[Challenge]
        self.challenge_history = {}  # user_id -> List[Challenge]
        self.user_progress = {}  # user_id -> Dict[str, Any]
        self.leaderboard = {}  # challenge_id -> List[Dict]
        
        # Challenge templates
        self.challenge_templates = {
            ChallengeType.SAVINGS: [
                {
                    "title": "30 päivän säästöhaaste",
                    "description": "Säästä 300€ 30 päivässä",
                    "duration_days": 30,
                    "target_amount": 300,
                    "reward_points": 100,
                    "requirements": ["daily_savings", "no_impulse_purchases"]
                },
                {
                    "title": "Viikkosäästöhaaste",
                    "description": "Säästä 50€ viikossa",
                    "duration_days": 7,
                    "target_amount": 50,
                    "reward_points": 25,
                    "requirements": ["weekly_savings", "budget_adherence"]
                }
            ],
            ChallengeType.INCOME: [
                {
                    "title": "Lisätulohaaste",
                    "description": "Ansaitse 200€ sivutuloilla",
                    "duration_days": 14,
                    "target_amount": 200,
                    "reward_points": 75,
                    "requirements": ["side_income", "skill_development"]
                }
            ],
            ChallengeType.SPENDING: [
                {
                    "title": "Kulujen leikkaamishaaste",
                    "description": "Leikkaa kuluja 20%",
                    "duration_days": 21,
                    "target_amount": 0.2,  # 20% reduction
                    "reward_points": 50,
                    "requirements": ["expense_reduction", "budget_optimization"]
                }
            ]
        }
    
    async def create_personalized_challenge(self, user_id: int, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create personalized challenge based on user behavior"""
        try:
            # Get user's current financial status
            current_status = await self._analyze_user_status(user_id)
            
            # Determine challenge type based on user needs
            challenge_type = self._determine_challenge_type(current_status, user_profile)
            
            # Select appropriate template
            template = self._select_challenge_template(challenge_type, current_status)
            
            # Customize challenge for user
            challenge = self._customize_challenge(template, user_id, current_status)
            
            # Store challenge
            if user_id not in self.active_challenges:
                self.active_challenges[user_id] = []
            
            self.active_challenges[user_id].append(challenge)
            
            # Publish event
            await publish_event(
                EventType.CHALLENGE_STARTED,
                user_id,
                {
                    "challenge_id": challenge.id,
                    "challenge_type": challenge.challenge_type.value,
                    "target_amount": challenge.target_amount,
                    "duration_days": challenge.duration_days
                },
                "challenge_engine"
            )
            
            return {
                "status": "success",
                "challenge": self._challenge_to_dict(challenge),
                "motivation_message": self._generate_motivation_message(challenge),
                "action_steps": self._generate_action_steps(challenge)
            }
            
        except Exception as e:
            logger.error(f"Failed to create personalized challenge: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _analyze_user_status(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's current financial status"""
        try:
            # This would integrate with existing services
            # For now, return mock data
            return {
                "savings_rate": 0.15,  # 15% savings rate
                "income_stability": 0.8,  # 80% stable
                "expense_volatility": 0.3,  # 30% volatile
                "debt_level": 0.2,  # 20% debt ratio
                "goal_progress": 0.25,  # 25% to 100k goal
                "risk_level": "moderate"
            }
        except Exception as e:
            logger.error(f"Failed to analyze user status: {e}")
            return {}
    
    def _determine_challenge_type(self, current_status: Dict[str, Any], user_profile: Dict[str, Any] = None) -> ChallengeType:
        """Determine best challenge type for user"""
        try:
            # Priority-based challenge selection
            if current_status.get("savings_rate", 0) < 0.2:
                return ChallengeType.SAVINGS
            elif current_status.get("income_stability", 0) < 0.7:
                return ChallengeType.INCOME
            elif current_status.get("expense_volatility", 0) > 0.4:
                return ChallengeType.SPENDING
            elif current_status.get("debt_level", 0) > 0.3:
                return ChallengeType.DEBT
            else:
                return ChallengeType.SAVINGS  # Default to savings
        except Exception as e:
            logger.error(f"Failed to determine challenge type: {e}")
            return ChallengeType.SAVINGS
    
    def _select_challenge_template(self, challenge_type: ChallengeType, current_status: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate challenge template"""
        try:
            templates = self.challenge_templates.get(challenge_type, [])
            if not templates:
                # Fallback template
                return {
                    "title": "Säästöhaaste",
                    "description": "Säästä 100€ tällä viikolla",
                    "duration_days": 7,
                    "target_amount": 100,
                    "reward_points": 50,
                    "requirements": ["daily_savings"]
                }
            
            # Select based on user's current level
            if current_status.get("risk_level") == "high":
                return templates[0]  # Easier challenge
            else:
                return random.choice(templates)
                
        except Exception as e:
            logger.error(f"Failed to select challenge template: {e}")
            return templates[0] if templates else {}
    
    def _customize_challenge(self, template: Dict[str, Any], user_id: int, current_status: Dict[str, Any]) -> Challenge:
        """Customize challenge for specific user"""
        try:
            challenge_id = f"challenge_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Adjust target based on user's current situation
            base_target = template.get("target_amount", 100)
            adjusted_target = self._adjust_target_for_user(base_target, current_status)
            
            # Determine difficulty
            difficulty = self._determine_difficulty(current_status)
            
            # Calculate duration
            duration_days = template.get("duration_days", 7)
            
            # Set dates
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            
            return Challenge(
                id=challenge_id,
                title=template.get("title", "Säästöhaaste"),
                description=template.get("description", "Säästä rahaa"),
                challenge_type=ChallengeType.SAVINGS,  # Default
                difficulty=difficulty,
                duration_days=duration_days,
                target_amount=adjusted_target,
                reward_points=template.get("reward_points", 50),
                requirements=template.get("requirements", []),
                start_date=start_date,
                end_date=end_date
            )
            
        except Exception as e:
            logger.error(f"Failed to customize challenge: {e}")
            raise
    
    def _adjust_target_for_user(self, base_target: float, current_status: Dict[str, Any]) -> float:
        """Adjust challenge target based on user's current situation"""
        try:
            # Adjust based on savings rate
            savings_rate = current_status.get("savings_rate", 0.1)
            if savings_rate < 0.1:
                return base_target * 0.7  # Easier target
            elif savings_rate > 0.3:
                return base_target * 1.3  # Harder target
            else:
                return base_target
        except Exception as e:
            logger.error(f"Failed to adjust target: {e}")
            return base_target
    
    def _determine_difficulty(self, current_status: Dict[str, Any]) -> ChallengeDifficulty:
        """Determine challenge difficulty"""
        try:
            risk_level = current_status.get("risk_level", "moderate")
            if risk_level == "low":
                return ChallengeDifficulty.BEGINNER
            elif risk_level == "moderate":
                return ChallengeDifficulty.INTERMEDIATE
            elif risk_level == "high":
                return ChallengeDifficulty.ADVANCED
            else:
                return ChallengeDifficulty.EXPERT
        except Exception as e:
            logger.error(f"Failed to determine difficulty: {e}")
            return ChallengeDifficulty.INTERMEDIATE
    
    async def update_challenge_progress(self, user_id: int, challenge_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update challenge progress"""
        try:
            if user_id not in self.active_challenges:
                return {"status": "error", "message": "No active challenges found"}
            
            # Find challenge
            challenge = None
            for c in self.active_challenges[user_id]:
                if c.id == challenge_id:
                    challenge = c
                    break
            
            if not challenge:
                return {"status": "error", "message": "Challenge not found"}
            
            # Update progress
            old_progress = challenge.progress
            challenge.progress = progress_data.get("progress", 0.0)
            
            # Check if completed
            if challenge.progress >= 1.0 and not challenge.completed:
                challenge.completed = True
                await self._handle_challenge_completion(user_id, challenge)
            
            # Publish progress event
            await publish_event(
                EventType.CHALLENGE_PROGRESS_UPDATED,
                user_id,
                {
                    "challenge_id": challenge_id,
                    "progress": challenge.progress,
                    "completed": challenge.completed
                },
                "challenge_engine"
            )
            
            return {
                "status": "success",
                "challenge": self._challenge_to_dict(challenge),
                "progress_increase": challenge.progress - old_progress
            }
            
        except Exception as e:
            logger.error(f"Failed to update challenge progress: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_challenge_completion(self, user_id: int, challenge: Challenge):
        """Handle challenge completion"""
        try:
            # Add to history
            if user_id not in self.challenge_history:
                self.challenge_history[user_id] = []
            self.challenge_history[user_id].append(challenge)
            
            # Remove from active
            self.active_challenges[user_id] = [c for c in self.active_challenges[user_id] if c.id != challenge.id]
            
            # Update leaderboard
            self._update_leaderboard(challenge)
            
            # Publish completion event
            await publish_event(
                EventType.CHALLENGE_COMPLETED,
                user_id,
                {
                    "challenge_id": challenge.id,
                    "reward_points": challenge.reward_points,
                    "challenge_type": challenge.challenge_type.value
                },
                "challenge_engine"
            )
            
            logger.info(f"Challenge {challenge.id} completed by user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle challenge completion: {e}")
    
    def _update_leaderboard(self, challenge: Challenge):
        """Update leaderboard with challenge completion"""
        try:
            if challenge.id not in self.leaderboard:
                self.leaderboard[challenge.id] = []
            
            self.leaderboard[challenge.id].append({
                "user_id": challenge.id.split("_")[1],  # Extract user_id from challenge_id
                "completion_date": datetime.now().isoformat(),
                "reward_points": challenge.reward_points,
                "difficulty": challenge.difficulty.value
            })
            
            # Sort by completion date
            self.leaderboard[challenge.id].sort(key=lambda x: x["completion_date"])
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard: {e}")
    
    def get_user_challenges(self, user_id: int) -> Dict[str, Any]:
        """Get user's active and completed challenges"""
        try:
            active_challenges = [
                self._challenge_to_dict(c) for c in self.active_challenges.get(user_id, [])
            ]
            
            completed_challenges = [
                self._challenge_to_dict(c) for c in self.challenge_history.get(user_id, [])
            ]
            
            return {
                "status": "success",
                "active_challenges": active_challenges,
                "completed_challenges": completed_challenges,
                "total_reward_points": sum(c.reward_points for c in self.challenge_history.get(user_id, [])),
                "completion_rate": len(completed_challenges) / max(len(completed_challenges) + len(active_challenges), 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user challenges: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_leaderboard(self, challenge_type: Optional[str] = None) -> Dict[str, Any]:
        """Get leaderboard for challenges"""
        try:
            if challenge_type:
                # Filter by challenge type
                filtered_leaderboard = {
                    k: v for k, v in self.leaderboard.items() 
                    if any(c.get("challenge_type") == challenge_type for c in v)
                }
            else:
                filtered_leaderboard = self.leaderboard
            
            return {
                "status": "success",
                "leaderboard": filtered_leaderboard,
                "total_participants": sum(len(participants) for participants in filtered_leaderboard.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return {"status": "error", "message": str(e)}
    
    def _challenge_to_dict(self, challenge: Challenge) -> Dict[str, Any]:
        """Convert challenge to dictionary"""
        return {
            "id": challenge.id,
            "title": challenge.title,
            "description": challenge.description,
            "challenge_type": challenge.challenge_type.value,
            "difficulty": challenge.difficulty.value,
            "duration_days": challenge.duration_days,
            "target_amount": challenge.target_amount,
            "reward_points": challenge.reward_points,
            "requirements": challenge.requirements,
            "start_date": challenge.start_date.isoformat(),
            "end_date": challenge.end_date.isoformat(),
            "is_active": challenge.is_active,
            "progress": challenge.progress,
            "completed": challenge.completed,
            "days_remaining": max(0, (challenge.end_date - datetime.now()).days)
        }
    
    def _generate_motivation_message(self, challenge: Challenge) -> str:
        """Generate motivational message for challenge"""
        messages = [
            f"🎯 {challenge.title} - Olet valmis tähän haasteeseen!",
            f"💪 {challenge.target_amount}€ tavoite on saavutettavissa {challenge.duration_days} päivässä",
            f"🏆 Saat {challenge.reward_points} pistettä kun suoritat haasteen",
            f"🚀 Tämä haaste vie sinua lähemmäs 100k€ tavoitetta!"
        ]
        return random.choice(messages)
    
    def _generate_action_steps(self, challenge: Challenge) -> List[str]:
        """Generate action steps for challenge"""
        if challenge.challenge_type == ChallengeType.SAVINGS:
            return [
                "Aseta päivittäinen säästötavoite",
                "Seuraa kulujasi tarkasti",
                "Leikkaa ylimääräisiä menoja",
                "Käytä säästöjä ensisijaisesti"
            ]
        elif challenge.challenge_type == ChallengeType.INCOME:
            return [
                "Etsi sivutulomahdollisuudet",
                "Käytä omaa osaamistasi",
                "Tarjoa palveluitasi verkossa",
                "Seuraa tulojasi päivittäin"
            ]
        else:
            return [
                "Aloita haaste nyt",
                "Seuraa edistymistäsi",
                "Pysy motivaationa",
                "Juhli saavutuksiasi"
            ]

# Global challenge engine instance
challenge_engine = ChallengeEngine() 