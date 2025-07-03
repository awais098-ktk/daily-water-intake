"""
Activity-based hydration calculator
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ActivityHydrationCalculator:
    """Calculate hydration recommendations based on activity data"""
    
    # Base hydration recommendations (ml per kg of body weight)
    BASE_HYDRATION_PER_KG = 35  # ml per kg
    DEFAULT_WEIGHT_KG = 70  # Default weight if not provided
    
    # Activity multipliers
    ACTIVITY_MULTIPLIERS = {
        'sedentary': 1.0,
        'low': 1.1,
        'moderate': 1.3,
        'high': 1.5
    }
    
    # Additional hydration for exercise (ml per minute of activity)
    EXERCISE_HYDRATION_PER_MINUTE = {
        'light': 3,    # Light exercise (walking, yoga)
        'moderate': 5, # Moderate exercise (jogging, cycling)
        'intense': 8   # Intense exercise (running, HIIT)
    }
    
    def __init__(self, user_weight_kg: Optional[float] = None):
        """
        Initialize the calculator
        
        Args:
            user_weight_kg: User's weight in kg. If None, uses default weight.
        """
        self.user_weight_kg = user_weight_kg or self.DEFAULT_WEIGHT_KG
    
    def calculate_base_hydration(self) -> int:
        """Calculate base daily hydration need in ml"""
        return int(self.user_weight_kg * self.BASE_HYDRATION_PER_KG)
    
    def calculate_activity_bonus(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional hydration needed based on activity
        
        Args:
            activity_data: Dictionary containing activity metrics
            
        Returns:
            Dictionary with bonus calculation details
        """
        if not activity_data:
            return {
                'bonus_ml': 0,
                'reasoning': 'No activity data available',
                'activity_level': 'unknown'
            }
        
        steps = activity_data.get('steps', 0)
        active_minutes = activity_data.get('active_minutes', 0)
        calories_burned = activity_data.get('calories_burned', 0)
        exercise_sessions = activity_data.get('exercise_sessions', [])
        
        # Determine activity level
        activity_level = self._determine_activity_level(steps, active_minutes)
        
        # Calculate base activity bonus
        base_hydration = self.calculate_base_hydration()
        activity_multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level, 1.0)
        activity_bonus = int((base_hydration * activity_multiplier) - base_hydration)
        
        # Add exercise-specific bonus
        exercise_bonus = self._calculate_exercise_bonus(exercise_sessions, active_minutes)
        
        # Add calorie-based bonus (additional 1ml per 10 calories above 2000)
        calorie_bonus = max(0, (calories_burned - 2000) // 10) if calories_burned > 2000 else 0
        
        total_bonus = activity_bonus + exercise_bonus + calorie_bonus
        
        # Generate reasoning
        reasoning_parts = []
        if activity_bonus > 0:
            reasoning_parts.append(f"Activity level ({activity_level}): +{activity_bonus}ml")
        if exercise_bonus > 0:
            reasoning_parts.append(f"Exercise sessions: +{exercise_bonus}ml")
        if calorie_bonus > 0:
            reasoning_parts.append(f"High calorie burn: +{calorie_bonus}ml")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No additional hydration needed"
        
        return {
            'bonus_ml': total_bonus,
            'reasoning': reasoning,
            'activity_level': activity_level,
            'breakdown': {
                'activity_bonus': activity_bonus,
                'exercise_bonus': exercise_bonus,
                'calorie_bonus': calorie_bonus
            }
        }
    
    def calculate_total_recommendation(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate total daily hydration recommendation
        
        Args:
            activity_data: Dictionary containing activity metrics
            
        Returns:
            Dictionary with complete recommendation details
        """
        base_hydration = self.calculate_base_hydration()
        activity_calculation = self.calculate_activity_bonus(activity_data)
        total_recommendation = base_hydration + activity_calculation['bonus_ml']
        
        return {
            'base_recommendation': base_hydration,
            'activity_bonus': activity_calculation['bonus_ml'],
            'total_recommendation': total_recommendation,
            'reasoning': f"Base hydration ({base_hydration}ml) + Activity bonus ({activity_calculation['bonus_ml']}ml). {activity_calculation['reasoning']}",
            'activity_level': activity_calculation['activity_level'],
            'breakdown': activity_calculation.get('breakdown', {})
        }
    
    def _determine_activity_level(self, steps: int, active_minutes: int) -> str:
        """Determine activity level based on steps and active minutes"""
        if steps >= 12000 or active_minutes >= 60:
            return 'high'
        elif steps >= 8000 or active_minutes >= 30:
            return 'moderate'
        elif steps >= 4000 or active_minutes >= 15:
            return 'low'
        else:
            return 'sedentary'
    
    def _calculate_exercise_bonus(self, exercise_sessions: list, active_minutes: int) -> int:
        """Calculate additional hydration for specific exercise sessions"""
        if not exercise_sessions:
            # Fallback: estimate based on active minutes
            if active_minutes >= 60:
                return active_minutes * self.EXERCISE_HYDRATION_PER_MINUTE['moderate']
            elif active_minutes >= 30:
                return active_minutes * self.EXERCISE_HYDRATION_PER_MINUTE['light']
            else:
                return 0
        
        total_bonus = 0
        for session in exercise_sessions:
            duration = session.get('duration_minutes', 0)
            intensity = self._determine_exercise_intensity(session)
            bonus_per_minute = self.EXERCISE_HYDRATION_PER_MINUTE.get(intensity, 3)
            total_bonus += duration * bonus_per_minute
        
        return total_bonus
    
    def _determine_exercise_intensity(self, exercise_session: Dict[str, Any]) -> str:
        """Determine exercise intensity from session data"""
        name = exercise_session.get('name', '').lower()
        calories_per_minute = exercise_session.get('calories', 0) / max(exercise_session.get('duration_minutes', 1), 1)
        
        # Intensity based on exercise name
        high_intensity_activities = ['running', 'hiit', 'crossfit', 'boxing', 'spinning']
        moderate_intensity_activities = ['cycling', 'jogging', 'swimming', 'tennis', 'basketball']
        
        if any(activity in name for activity in high_intensity_activities) or calories_per_minute > 8:
            return 'intense'
        elif any(activity in name for activity in moderate_intensity_activities) or calories_per_minute > 5:
            return 'moderate'
        else:
            return 'light'
    
    def get_hydration_tips(self, activity_data: Dict[str, Any]) -> list:
        """Get personalized hydration tips based on activity"""
        tips = []
        
        if not activity_data:
            tips.append("Connect a fitness tracker to get personalized hydration recommendations!")
            return tips
        
        steps = activity_data.get('steps', 0)
        active_minutes = activity_data.get('active_minutes', 0)
        exercise_sessions = activity_data.get('exercise_sessions', [])
        
        # Step-based tips
        if steps >= 10000:
            tips.append("Great job on reaching 10,000+ steps! Remember to hydrate throughout your active day.")
        elif steps >= 5000:
            tips.append("You're moderately active today. Keep sipping water regularly.")
        else:
            tips.append("Low activity day - perfect time to focus on consistent hydration.")
        
        # Exercise-based tips
        if exercise_sessions:
            tips.append("You exercised today! Drink extra water before, during, and after workouts.")
            if any('running' in session.get('name', '').lower() for session in exercise_sessions):
                tips.append("Running detected: Aim to drink 150-250ml every 15-20 minutes during long runs.")
        
        # Active minutes tips
        if active_minutes >= 60:
            tips.append("High activity day! Consider electrolyte replacement if you're sweating heavily.")
        
        return tips[:3]  # Limit to 3 tips
