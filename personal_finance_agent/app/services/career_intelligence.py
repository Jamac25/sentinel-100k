"""
Sentinel Career Intelligence™ - Career Path Analysis and Income Optimization
Integrates with IncomeIntelligence, LearningEngine, and IdeaEngine for career growth
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.category import Category
from ..services.event_bus import EventType, publish_event
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
import json
import asyncio
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class CareerLevel(Enum):
    """Career development levels"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXPERT = "expert"
    LEADER = "leader"

class SkillCategory(Enum):
    """Skill categories for career development"""
    TECHNICAL = "technical"
    SOFT_SKILLS = "soft_skills"
    LEADERSHIP = "leadership"
    BUSINESS = "business"
    SPECIALIZED = "specialized"

@dataclass
class CareerOpportunity:
    """Career opportunity data structure"""
    id: str
    title: str
    description: str
    salary_range: Tuple[float, float]
    required_skills: List[str]
    skill_gaps: List[str]
    learning_path: List[str]
    time_to_qualify: int  # months
    confidence_score: float
    priority: str  # high, medium, low

@dataclass
class SkillGap:
    """Skill gap analysis data structure"""
    skill_name: str
    current_level: float  # 0-100
    required_level: float  # 0-100
    gap_size: float
    learning_resources: List[str]
    estimated_time: int  # weeks
    priority: str

class CareerIntelligence:
    """
    Sentinel Career Intelligence™ - Career Path Analysis
    
    Features:
    - Career path analysis and income growth optimization
    - Skill gap analysis and learning recommendations
    - Salary negotiation suggestions based on market data
    - Side hustle opportunities based on expertise
    - Career-specific savings and investment strategies
    """
    
    def __init__(self):
        self.career_profiles = {}  # user_id -> Dict
        self.skill_assessments = {}  # user_id -> Dict
        self.opportunity_history = {}  # user_id -> List[Dict]
        self.learning_paths = {}  # user_id -> List[Dict]
        
        # Career development data
        self.career_levels = {
            CareerLevel.ENTRY: {"min_salary": 2500, "max_salary": 3500, "years_exp": 0},
            CareerLevel.JUNIOR: {"min_salary": 3500, "max_salary": 4500, "years_exp": 2},
            CareerLevel.MID: {"min_salary": 4500, "max_salary": 6000, "years_exp": 5},
            CareerLevel.SENIOR: {"min_salary": 6000, "max_salary": 8000, "years_exp": 8},
            CareerLevel.EXPERT: {"min_salary": 8000, "max_salary": 12000, "years_exp": 12},
            CareerLevel.LEADER: {"min_salary": 12000, "max_salary": 20000, "years_exp": 15}
        }
        
        # Skill categories and market demand
        self.skill_market_data = {
            SkillCategory.TECHNICAL: {
                "demand_score": 0.9,
                "salary_premium": 0.2,
                "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes"]
            },
            SkillCategory.SOFT_SKILLS: {
                "demand_score": 0.8,
                "salary_premium": 0.15,
                "skills": ["Communication", "Problem Solving", "Teamwork", "Time Management", "Adaptability"]
            },
            SkillCategory.LEADERSHIP: {
                "demand_score": 0.85,
                "salary_premium": 0.25,
                "skills": ["Project Management", "Team Leadership", "Strategic Thinking", "Decision Making"]
            },
            SkillCategory.BUSINESS: {
                "demand_score": 0.75,
                "salary_premium": 0.18,
                "skills": ["Business Analysis", "Financial Modeling", "Market Research", "Strategy"]
            },
            SkillCategory.SPECIALIZED: {
                "demand_score": 0.95,
                "salary_premium": 0.3,
                "skills": ["AI/ML", "Data Science", "Cybersecurity", "Blockchain", "Cloud Architecture"]
            }
        }
    
    async def analyze_career_growth(self, user_id: int, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze user's career growth potential and opportunities"""
        try:
            # Get user's current career status
            current_status = await self._analyze_current_career_status(user_id, user_profile)
            
            # Analyze skill gaps
            skill_gaps = await self._analyze_skill_gaps(user_id, current_status)
            
            # Identify career opportunities
            opportunities = await self._identify_career_opportunities(user_id, current_status, skill_gaps)
            
            # Generate learning path
            learning_path = await self._generate_learning_path(user_id, skill_gaps, opportunities)
            
            # Calculate income growth potential
            income_potential = await self._calculate_income_potential(user_id, opportunities, current_status)
            
            # Store analysis
            analysis_record = {
                "timestamp": datetime.now().isoformat(),
                "current_status": current_status,
                "skill_gaps": [self._skill_gap_to_dict(gap) for gap in skill_gaps],
                "opportunities": [self._opportunity_to_dict(opp) for opp in opportunities],
                "income_potential": income_potential
            }
            
            if user_id not in self.opportunity_history:
                self.opportunity_history[user_id] = []
            self.opportunity_history[user_id].append(analysis_record)
            
            # Publish career analysis event
            await publish_event(
                EventType.CAREER_OPPORTUNITY_DETECTED,
                user_id,
                {
                    "opportunities_count": len(opportunities),
                    "income_potential": income_potential.get("total_potential", 0),
                    "skill_gaps_count": len(skill_gaps)
                },
                "career_intelligence"
            )
            
            return {
                "status": "success",
                "current_status": current_status,
                "skill_gaps": [self._skill_gap_to_dict(gap) for gap in skill_gaps],
                "opportunities": [self._opportunity_to_dict(opp) for opp in opportunities],
                "learning_path": learning_path,
                "income_potential": income_potential,
                "recommendations": self._generate_career_recommendations(opportunities, skill_gaps)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze career growth: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _analyze_current_career_status(self, user_id: int, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze user's current career status"""
        try:
            # This would integrate with existing services
            # For now, return mock data based on user profile
            if user_profile:
                current_salary = user_profile.get("current_salary", 4000)
                years_experience = user_profile.get("years_experience", 3)
                current_role = user_profile.get("current_role", "Software Developer")
            else:
                current_salary = 4000
                years_experience = 3
                current_role = "Software Developer"
            
            # Determine career level
            career_level = self._determine_career_level(current_salary, years_experience)
            
            # Calculate market position
            market_position = self._calculate_market_position(current_salary, career_level)
            
            # Analyze income growth
            income_growth = self._analyze_income_growth(user_id)
            
            return {
                "current_salary": current_salary,
                "years_experience": years_experience,
                "current_role": current_role,
                "career_level": career_level.value,
                "market_position": market_position,
                "income_growth_rate": income_growth.get("growth_rate", 0.05),
                "salary_percentile": market_position.get("percentile", 50),
                "promotion_readiness": self._calculate_promotion_readiness(career_level, years_experience)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze career status: {e}")
            return {}
    
    def _determine_career_level(self, salary: float, years_experience: int) -> CareerLevel:
        """Determine career level based on salary and experience"""
        try:
            if years_experience < 1:
                return CareerLevel.ENTRY
            elif years_experience < 3:
                return CareerLevel.JUNIOR
            elif years_experience < 7:
                return CareerLevel.MID
            elif years_experience < 10:
                return CareerLevel.SENIOR
            elif years_experience < 15:
                return CareerLevel.EXPERT
            else:
                return CareerLevel.LEADER
        except Exception as e:
            logger.error(f"Failed to determine career level: {e}")
            return CareerLevel.MID
    
    def _calculate_market_position(self, salary: float, career_level: CareerLevel) -> Dict[str, Any]:
        """Calculate market position and salary percentile"""
        try:
            level_data = self.career_levels[career_level]
            min_salary = level_data["min_salary"]
            max_salary = level_data["max_salary"]
            
            if salary < min_salary:
                percentile = 25
                position = "below_market"
            elif salary > max_salary:
                percentile = 90
                position = "above_market"
            else:
                # Calculate percentile within range
                range_size = max_salary - min_salary
                position_in_range = salary - min_salary
                percentile = 25 + (position_in_range / range_size) * 65
                position = "market_rate"
            
            return {
                "percentile": percentile,
                "position": position,
                "market_min": min_salary,
                "market_max": max_salary,
                "gap_to_next_level": max_salary - salary
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate market position: {e}")
            return {"percentile": 50, "position": "unknown"}
    
    def _analyze_income_growth(self, user_id: int) -> Dict[str, Any]:
        """Analyze income growth over time"""
        try:
            # This would analyze actual transaction data
            # For now, return mock data
            return {
                "growth_rate": 0.08,  # 8% annual growth
                "growth_consistency": 0.7,
                "last_raise": "6 months ago",
                "next_expected_raise": "6 months"
            }
        except Exception as e:
            logger.error(f"Failed to analyze income growth: {e}")
            return {"growth_rate": 0.05}
    
    def _calculate_promotion_readiness(self, career_level: CareerLevel, years_experience: int) -> float:
        """Calculate promotion readiness score"""
        try:
            level_data = self.career_levels[career_level]
            required_years = level_data["years_exp"]
            
            if years_experience >= required_years:
                readiness = min(1.0, (years_experience - required_years) / 2 + 0.8)
            else:
                readiness = max(0.1, years_experience / required_years * 0.7)
            
            return readiness
            
        except Exception as e:
            logger.error(f"Failed to calculate promotion readiness: {e}")
            return 0.5
    
    async def _analyze_skill_gaps(self, user_id: int, current_status: Dict[str, Any]) -> List[SkillGap]:
        """Analyze skill gaps for career advancement"""
        try:
            skill_gaps = []
            current_role = current_status.get("current_role", "Software Developer")
            career_level = current_status.get("career_level", "mid")
            
            # Get required skills for next level
            next_level_skills = self._get_required_skills_for_level(career_level, current_role)
            
            # Assess current skills (mock assessment)
            current_skills = self._assess_current_skills(user_id, current_role)
            
            # Identify gaps
            for skill_name, required_level in next_level_skills.items():
                current_level = current_skills.get(skill_name, 30)  # Default low level
                gap_size = max(0, required_level - current_level)
                
                if gap_size > 10:  # Significant gap
                    skill_gap = SkillGap(
                        skill_name=skill_name,
                        current_level=current_level,
                        required_level=required_level,
                        gap_size=gap_size,
                        learning_resources=self._get_learning_resources(skill_name),
                        estimated_time=self._estimate_learning_time(gap_size),
                        priority=self._determine_skill_priority(skill_name, gap_size)
                    )
                    skill_gaps.append(skill_gap)
            
            # Sort by priority and gap size
            skill_gaps.sort(key=lambda x: (x.priority == "high", x.gap_size), reverse=True)
            
            return skill_gaps
            
        except Exception as e:
            logger.error(f"Failed to analyze skill gaps: {e}")
            return []
    
    def _get_required_skills_for_level(self, career_level: str, role: str) -> Dict[str, float]:
        """Get required skills for career advancement"""
        try:
            # Mock skill requirements based on role and level
            if "developer" in role.lower():
                if career_level == "junior":
                    return {
                        "Python": 70,
                        "JavaScript": 60,
                        "Git": 80,
                        "Problem Solving": 65,
                        "Communication": 60
                    }
                elif career_level == "mid":
                    return {
                        "Python": 85,
                        "JavaScript": 80,
                        "React": 75,
                        "System Design": 70,
                        "Leadership": 60,
                        "Architecture": 65
                    }
                elif career_level == "senior":
                    return {
                        "System Design": 85,
                        "Architecture": 80,
                        "Leadership": 75,
                        "Project Management": 70,
                        "Mentoring": 75,
                        "Business Acumen": 65
                    }
            
            # Default skills for any role
            return {
                "Communication": 75,
                "Leadership": 70,
                "Problem Solving": 80,
                "Business Acumen": 65
            }
            
        except Exception as e:
            logger.error(f"Failed to get required skills: {e}")
            return {}
    
    def _assess_current_skills(self, user_id: int, role: str) -> Dict[str, float]:
        """Assess user's current skill levels"""
        try:
            # This would integrate with learning assessments
            # For now, return mock assessment
            if "developer" in role.lower():
                return {
                    "Python": 75,
                    "JavaScript": 60,
                    "Git": 80,
                    "React": 50,
                    "System Design": 40,
                    "Leadership": 45,
                    "Communication": 70,
                    "Problem Solving": 75
                }
            else:
                return {
                    "Communication": 70,
                    "Leadership": 50,
                    "Problem Solving": 75,
                    "Business Acumen": 60
                }
                
        except Exception as e:
            logger.error(f"Failed to assess current skills: {e}")
            return {}
    
    def _get_learning_resources(self, skill_name: str) -> List[str]:
        """Get learning resources for skill development"""
        try:
            resources = {
                "Python": [
                    "Python for Everybody (Coursera)",
                    "Real Python Tutorials",
                    "Python Crash Course Book"
                ],
                "JavaScript": [
                    "JavaScript.info",
                    "Eloquent JavaScript Book",
                    "MDN Web Docs"
                ],
                "React": [
                    "React Official Tutorial",
                    "Full Stack Open Course",
                    "React Patterns Book"
                ],
                "Leadership": [
                    "The Leadership Challenge Book",
                    "Harvard Business Review Articles",
                    "Leadership Workshops"
                ],
                "Communication": [
                    "Toastmasters International",
                    "Crucial Conversations Book",
                    "Public Speaking Courses"
                ]
            }
            
            return resources.get(skill_name, [
                f"Online courses for {skill_name}",
                f"Books about {skill_name}",
                f"Practice projects in {skill_name}"
            ])
            
        except Exception as e:
            logger.error(f"Failed to get learning resources: {e}")
            return ["Online courses", "Books", "Practice projects"]
    
    def _estimate_learning_time(self, gap_size: float) -> int:
        """Estimate learning time in weeks"""
        try:
            # Rough estimation: 2-4 weeks per 10 points of gap
            weeks_per_10_points = 3
            return max(2, int(gap_size / 10 * weeks_per_10_points))
        except Exception as e:
            logger.error(f"Failed to estimate learning time: {e}")
            return 4
    
    def _determine_skill_priority(self, skill_name: str, gap_size: float) -> str:
        """Determine skill priority for learning"""
        try:
            # High priority for large gaps or critical skills
            critical_skills = ["Communication", "Leadership", "Problem Solving"]
            
            if skill_name in critical_skills or gap_size > 30:
                return "high"
            elif gap_size > 20:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Failed to determine skill priority: {e}")
            return "medium"
    
    async def _identify_career_opportunities(self, user_id: int, current_status: Dict[str, Any], 
                                           skill_gaps: List[SkillGap]) -> List[CareerOpportunity]:
        """Identify career opportunities based on current status and skills"""
        try:
            opportunities = []
            current_role = current_status.get("current_role", "Software Developer")
            current_salary = current_status.get("current_salary", 4000)
            
            # Generate opportunities based on role and skills
            if "developer" in current_role.lower():
                opportunities.extend([
                    self._create_opportunity("Senior Developer", current_salary * 1.3, skill_gaps),
                    self._create_opportunity("Tech Lead", current_salary * 1.5, skill_gaps),
                    self._create_opportunity("Software Architect", current_salary * 1.4, skill_gaps),
                    self._create_opportunity("DevOps Engineer", current_salary * 1.25, skill_gaps)
                ])
            else:
                opportunities.extend([
                    self._create_opportunity("Senior Specialist", current_salary * 1.3, skill_gaps),
                    self._create_opportunity("Team Lead", current_salary * 1.4, skill_gaps),
                    self._create_opportunity("Manager", current_salary * 1.5, skill_gaps)
                ])
            
            # Add side hustle opportunities
            side_hustles = self._identify_side_hustle_opportunities(current_role, skill_gaps)
            opportunities.extend(side_hustles)
            
            # Sort by potential and feasibility
            opportunities.sort(key=lambda x: (x.confidence_score, x.salary_range[1]), reverse=True)
            
            return opportunities[:5]  # Return top 5 opportunities
            
        except Exception as e:
            logger.error(f"Failed to identify opportunities: {e}")
            return []
    
    def _create_opportunity(self, title: str, target_salary: float, 
                           skill_gaps: List[SkillGap]) -> CareerOpportunity:
        """Create career opportunity"""
        try:
            opportunity_id = f"opp_{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
            
            # Determine required skills and gaps
            required_skills = self._get_skills_for_role(title)
            relevant_gaps = [gap for gap in skill_gaps if gap.skill_name in required_skills]
            
            # Calculate confidence score
            confidence_score = self._calculate_opportunity_confidence(relevant_gaps, target_salary)
            
            # Generate learning path
            learning_path = self._generate_learning_path_for_opportunity(title, relevant_gaps)
            
            # Estimate time to qualify
            time_to_qualify = max(3, sum(gap.estimated_time for gap in relevant_gaps) // 4)  # Convert weeks to months
            
            return CareerOpportunity(
                id=opportunity_id,
                title=title,
                description=f"Advance to {title} role with {target_salary:.0f}€ salary potential",
                salary_range=(target_salary * 0.9, target_salary * 1.1),
                required_skills=required_skills,
                skill_gaps=[gap.skill_name for gap in relevant_gaps],
                learning_path=learning_path,
                time_to_qualify=time_to_qualify,
                confidence_score=confidence_score,
                priority="high" if confidence_score > 0.7 else "medium"
            )
            
        except Exception as e:
            logger.error(f"Failed to create opportunity: {e}")
            raise
    
    def _get_skills_for_role(self, role: str) -> List[str]:
        """Get required skills for specific role"""
        try:
            skills_map = {
                "Senior Developer": ["Python", "JavaScript", "System Design", "Leadership"],
                "Tech Lead": ["Leadership", "System Design", "Architecture", "Mentoring"],
                "Software Architect": ["Architecture", "System Design", "Business Acumen", "Leadership"],
                "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Python"],
                "Senior Specialist": ["Problem Solving", "Communication", "Leadership"],
                "Team Lead": ["Leadership", "Communication", "Project Management"],
                "Manager": ["Leadership", "Business Acumen", "Communication", "Strategic Thinking"]
            }
            
            return skills_map.get(role, ["Communication", "Problem Solving"])
            
        except Exception as e:
            logger.error(f"Failed to get skills for role: {e}")
            return ["Communication", "Problem Solving"]
    
    def _calculate_opportunity_confidence(self, skill_gaps: List[SkillGap], target_salary: float) -> float:
        """Calculate confidence score for opportunity"""
        try:
            if not skill_gaps:
                return 0.9  # High confidence if no gaps
            
            # Calculate based on gap sizes and learning time
            total_gap = sum(gap.gap_size for gap in skill_gaps)
            total_time = sum(gap.estimated_time for gap in skill_gaps)
            
            # Normalize to 0-1 scale
            gap_factor = max(0, 1 - total_gap / 100)
            time_factor = max(0, 1 - total_time / 52)  # 52 weeks = 1 year
            
            confidence = (gap_factor + time_factor) / 2
            
            return min(max(confidence, 0.1), 0.95)
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence: {e}")
            return 0.5
    
    def _generate_learning_path_for_opportunity(self, role: str, skill_gaps: List[SkillGap]) -> List[str]:
        """Generate learning path for opportunity"""
        try:
            learning_path = []
            
            # Sort gaps by priority and time
            sorted_gaps = sorted(skill_gaps, key=lambda x: (x.priority == "high", x.estimated_time))
            
            for gap in sorted_gaps:
                learning_path.append(f"Develop {gap.skill_name} skills ({gap.estimated_time} weeks)")
            
            # Add role-specific learning
            if "Lead" in role or "Manager" in role:
                learning_path.append("Take leadership training (8 weeks)")
                learning_path.append("Practice team management (ongoing)")
            
            if "Architect" in role:
                learning_path.append("Study system design patterns (6 weeks)")
                learning_path.append("Work on architecture projects (ongoing)")
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Failed to generate learning path: {e}")
            return ["Focus on skill development", "Gain relevant experience"]
    
    def _identify_side_hustle_opportunities(self, current_role: str, skill_gaps: List[SkillGap]) -> List[CareerOpportunity]:
        """Identify side hustle opportunities"""
        try:
            side_hustles = []
            
            # Freelance opportunities
            if "developer" in current_role.lower():
                side_hustles.append(self._create_opportunity(
                    "Freelance Developer", 2000, skill_gaps
                ))
                side_hustles.append(self._create_opportunity(
                    "Technical Consultant", 3000, skill_gaps
                ))
            
            # Teaching opportunities
            side_hustles.append(self._create_opportunity(
                "Online Instructor", 1500, skill_gaps
            ))
            
            # Content creation
            side_hustles.append(self._create_opportunity(
                "Technical Writer", 1000, skill_gaps
            ))
            
            return side_hustles
            
        except Exception as e:
            logger.error(f"Failed to identify side hustles: {e}")
            return []
    
    async def _generate_learning_path(self, user_id: int, skill_gaps: List[SkillGap], 
                                    opportunities: List[CareerOpportunity]) -> Dict[str, Any]:
        """Generate comprehensive learning path"""
        try:
            # Prioritize skills based on opportunities
            priority_skills = []
            for opp in opportunities:
                priority_skills.extend(opp.skill_gaps)
            
            # Remove duplicates and sort by frequency
            skill_priority = {}
            for skill in priority_skills:
                skill_priority[skill] = skill_priority.get(skill, 0) + 1
            
            # Create learning timeline
            timeline = []
            current_week = 0
            
            for skill, priority in sorted(skill_priority.items(), key=lambda x: x[1], reverse=True):
                gap = next((g for g in skill_gaps if g.skill_name == skill), None)
                if gap:
                    timeline.append({
                        "week": current_week + 1,
                        "skill": skill,
                        "duration": gap.estimated_time,
                        "resources": gap.learning_resources[:2],  # Top 2 resources
                        "priority": "high" if priority > 1 else "medium"
                    })
                    current_week += gap.estimated_time
            
            return {
                "timeline": timeline,
                "total_duration_weeks": current_week,
                "priority_skills": list(skill_priority.keys())[:5],
                "estimated_completion": (datetime.now() + timedelta(weeks=current_week)).strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            logger.error(f"Failed to generate learning path: {e}")
            return {"timeline": [], "total_duration_weeks": 0}
    
    async def _calculate_income_potential(self, user_id: int, opportunities: List[CareerOpportunity], 
                                        current_status: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate income growth potential"""
        try:
            current_salary = current_status.get("current_salary", 4000)
            
            # Calculate potential from opportunities
            opportunity_potential = 0
            for opp in opportunities:
                avg_salary = (opp.salary_range[0] + opp.salary_range[1]) / 2
                potential = avg_salary - current_salary
                opportunity_potential = max(opportunity_potential, potential)
            
            # Calculate side hustle potential
            side_hustle_potential = 500  # Monthly side income potential
            
            # Calculate total potential
            total_potential = opportunity_potential + side_hustle_potential
            
            return {
                "current_salary": current_salary,
                "opportunity_potential": opportunity_potential,
                "side_hustle_potential": side_hustle_potential,
                "total_potential": total_potential,
                "growth_percentage": (total_potential / current_salary) * 100,
                "time_to_achieve": "6-12 months"
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate income potential: {e}")
            return {"total_potential": 0}
    
    def _generate_career_recommendations(self, opportunities: List[CareerOpportunity], 
                                       skill_gaps: List[SkillGap]) -> List[str]:
        """Generate career recommendations"""
        try:
            recommendations = []
            
            if opportunities:
                top_opportunity = opportunities[0]
                recommendations.append(f"Focus on {top_opportunity.title} role - {top_opportunity.time_to_qualify} months to qualify")
            
            high_priority_gaps = [gap for gap in skill_gaps if gap.priority == "high"]
            if high_priority_gaps:
                top_gap = high_priority_gaps[0]
                recommendations.append(f"Prioritize {top_gap.skill_name} development - {top_gap.estimated_time} weeks to improve")
            
            recommendations.extend([
                "Network with professionals in your target role",
                "Seek mentorship from senior colleagues",
                "Take on stretch assignments at work",
                "Build a portfolio of relevant projects"
            ])
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Focus on skill development", "Network actively", "Seek mentorship"]
    
    def _skill_gap_to_dict(self, gap: SkillGap) -> Dict[str, Any]:
        """Convert skill gap to dictionary"""
        return {
            "skill_name": gap.skill_name,
            "current_level": gap.current_level,
            "required_level": gap.required_level,
            "gap_size": gap.gap_size,
            "learning_resources": gap.learning_resources,
            "estimated_time": gap.estimated_time,
            "priority": gap.priority
        }
    
    def _opportunity_to_dict(self, opp: CareerOpportunity) -> Dict[str, Any]:
        """Convert opportunity to dictionary"""
        return {
            "id": opp.id,
            "title": opp.title,
            "description": opp.description,
            "salary_range": opp.salary_range,
            "required_skills": opp.required_skills,
            "skill_gaps": opp.skill_gaps,
            "learning_path": opp.learning_path,
            "time_to_qualify": opp.time_to_qualify,
            "confidence_score": opp.confidence_score,
            "priority": opp.priority
        }
    
    def get_career_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's career analysis history"""
        try:
            history = self.opportunity_history.get(user_id, [])
            return {
                "status": "success",
                "history": history,
                "total_analyses": len(history)
            }
        except Exception as e:
            logger.error(f"Failed to get career history: {e}")
            return {"status": "error", "message": str(e)}

# Global career intelligence instance
career_intelligence = CareerIntelligence() 