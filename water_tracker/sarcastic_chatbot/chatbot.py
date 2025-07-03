"""
Sarcastic Chatbot Core Logic

This module contains the main chatbot class that handles sarcastic responses
and integrates with the water intake tracking system.
"""

import re
import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SarcasticChatbot:
    """
    A sarcastic chatbot that provides humorous feedback about water intake habits.
    """
    
    def __init__(self):
        """Initialize the sarcastic chatbot with personality responses."""
        self.personality_responses = {
            'greeting': [
                "Oh look, someone remembered they need water to survive! How revolutionary.",
                "Well, well, well... if it isn't my favorite dehydrated human.",
                "Back for more hydration wisdom? I'm shocked.",
                "Let me guess, you're here because you suddenly realized you're not a cactus?",
                "Welcome back! Ready to pretend you'll actually drink water today?"
            ],
            'no_water': [
                "Did you forget water exists, or are you just seeing how long you can go without it?",
                "Zero milliliters? Wow, you're really pushing the limits of human survival.",
                "Are you still waiting for a miracle, or is water just too mainstream for you today?",
                "I see you've chosen the 'human raisin' lifestyle. Bold choice.",
                "Let me guess, you're photosynthesizing now? Because that's the only explanation."
            ],
            'low_intake': [
                "You've had only {intake} ml? You're really testing the limits of human endurance, huh?",
                "Well, {intake} ml is... a start, I guess. But hey, you're only {remaining} ml away from not feeling like a raisin!",
                "Congratulations! You've consumed {intake} ml. That's almost enough to keep a houseplant alive.",
                "Oh wow, {intake} ml! At this rate, you'll reach your goal sometime next century.",
                "I'm impressed. {intake} ml is more than I expected from someone who clearly thinks water is optional."
            ],
            'moderate_intake': [
                "You're at {intake} ml. Not terrible, but let's not throw a parade just yet.",
                "Half way there with {intake} ml! Only {remaining} ml to go. You can do it... probably.",
                "Look at you, drinking {intake} ml like a responsible adult. I'm almost proud.",
                "You've managed {intake} ml so far. Keep this up and you might actually survive the day.",
                "Progress! {intake} ml down, {remaining} ml to go. Try not to celebrate too early."
            ],
            'near_goal': [
                "You're almost there! Just {remaining} ml more, or are you planning on turning into a raisin at the last minute?",
                "So close with {intake} ml! Just {remaining} ml left. Don't choke now.",
                "You've had {intake} ml. The finish line is in sight! Try not to trip over your own success.",
                "Almost at your goal! {remaining} ml to go. I believe in you... sort of.",
                "You're {remaining} ml away from proving you're not completely hopeless at hydration."
            ],
            'goal_reached': [
                "Congrats! You've managed to drink {intake} ml today. I guess you're not a dehydrated zombie anymore.",
                "Well, look who actually reached their goal! {intake} ml. I'm genuinely surprised.",
                "You did it! {intake} ml. Now you can join the ranks of properly hydrated humans.",
                "Achievement unlocked: Basic Human Survival! {intake} ml consumed.",
                "Wow, {intake} ml! You've officially proven you can keep yourself alive. Impressive."
            ],
            'over_goal': [
                "Whoa there, overachiever! {intake} ml is {excess} ml over your goal. Trying to become a fish?",
                "You've had {intake} ml. That's {excess} ml more than needed. Are you preparing for a drought?",
                "Impressive! {intake} ml is way over your goal. At least we know you won't shrivel up today.",
                "You've consumed {intake} ml. That's {excess} ml extra. Someone's really committed to not being a raisin.",
                "Look at you, drinking {intake} ml! That's {excess} ml over your goal. Show off."
            ],
            'reminder': [
                "Still haven't had any water? Great job testing the limits of human survival. You're at {intake} ml, keep it up!",
                "Reminder: Water exists and you need it. Currently at {intake} ml. Revolutionary concept, I know.",
                "Hey there, desert dweller! You're at {intake} ml. Time to drink something before you turn into jerky.",
                "Just checking in on my favorite dehydrated human. {intake} ml so far. Impressive dedication to dryness.",
                "Water break time! You're at {intake} ml. I know, I know, drinking water is so mainstream."
            ],
            'encouragement': [
                "Come on, you can do better than {intake} ml. I believe in you... barely.",
                "You're at {intake} ml. Not great, but I've seen worse. Barely.",
                "Let's try to get past {intake} ml, shall we? Baby steps.",
                "You've had {intake} ml. Time to step up your game, don't you think?",
                "Current status: {intake} ml. Let's aim higher, or at least aim for survival."
            ],
            'help': [
                "Need help? Just tell me how much water you drank, like '500 ml' or 'I drank 2 glasses'.",
                "You can say things like 'I had 300ml' or 'drank 1 liter'. It's not rocket science.",
                "Tell me your water intake in ml, liters, cups, or glasses. Even you can handle that.",
                "Just say how much you drank. Examples: '250ml', '1 cup', '2 glasses'. Simple enough?",
                "Report your water intake or ask for your status. I'll try to keep the sarcasm to a minimum... not really."
            ],
            'error': [
                "I can't understand what you're trying to tell me. Try using actual words next time.",
                "That doesn't make sense. Are you dehydrated? Because that would explain a lot.",
                "I'm sorry, I don't speak 'confused human'. Try again with clearer instructions.",
                "Error detected: Your input. Please try again with something that makes sense.",
                "I'm a chatbot, not a mind reader. Be more specific, please."
            ]
        }
        
        # Patterns for extracting water intake from user input
        self.intake_patterns = [
            r'(\d+)\s*ml',
            r'(\d+)\s*milliliters?',
            r'(\d+)\s*liters?',
            r'(\d+)\s*l\b',
            r'(\d+)\s*cups?',
            r'(\d+)\s*glasses?',
            r'(\d+)\s*bottles?',
            r'(\d+)\s*oz',
            r'(\d+)\s*ounces?'
        ]
        
        # Conversion factors to ml
        self.conversions = {
            'ml': 1,
            'milliliter': 1,
            'milliliters': 1,
            'liter': 1000,
            'liters': 1000,
            'l': 1000,
            'cup': 240,
            'cups': 240,
            'glass': 250,
            'glasses': 250,
            'bottle': 500,
            'bottles': 500,
            'oz': 30,
            'ounce': 30,
            'ounces': 30
        }

    def extract_water_intake(self, text: str) -> Optional[int]:
        """
        Extract water intake amount from user text.
        
        Args:
            text: User input text
            
        Returns:
            Water intake in ml, or None if not found
        """
        text = text.lower().strip()
        
        for pattern in self.intake_patterns:
            match = re.search(pattern, text)
            if match:
                amount = int(match.group(1))
                
                # Determine unit
                unit_text = text[match.end():].strip()
                unit = 'ml'  # default
                
                for unit_key in self.conversions.keys():
                    if unit_key in unit_text:
                        unit = unit_key
                        break
                
                # Convert to ml
                return amount * self.conversions[unit]
        
        return None

    def get_intake_category(self, current_intake: int, daily_goal: int) -> str:
        """
        Categorize current intake level.
        
        Args:
            current_intake: Current water intake in ml
            daily_goal: Daily goal in ml
            
        Returns:
            Category string
        """
        if current_intake == 0:
            return 'no_water'
        elif current_intake < daily_goal * 0.3:
            return 'low_intake'
        elif current_intake < daily_goal * 0.7:
            return 'moderate_intake'
        elif current_intake < daily_goal:
            return 'near_goal'
        elif current_intake == daily_goal:
            return 'goal_reached'
        else:
            return 'over_goal'

    def generate_response(self, category: str, **kwargs) -> str:
        """
        Generate a sarcastic response based on category and context.
        
        Args:
            category: Response category
            **kwargs: Context variables for response formatting
            
        Returns:
            Formatted sarcastic response
        """
        if category not in self.personality_responses:
            category = 'error'
        
        response_template = random.choice(self.personality_responses[category])
        
        try:
            return response_template.format(**kwargs)
        except KeyError:
            # If formatting fails, return a generic response
            return random.choice(self.personality_responses['error'])

    def process_user_input(self, text: str, current_intake: int, daily_goal: int) -> Dict:
        """
        Process user input and generate appropriate response.
        
        Args:
            text: User input text
            current_intake: Current daily water intake in ml
            daily_goal: Daily hydration goal in ml
            
        Returns:
            Dictionary with response and any extracted data
        """
        logger.info(f"Processing user input: '{text}' (current: {current_intake}ml, goal: {daily_goal}ml)")
        
        # Check for greeting
        greetings = ['hello', 'hi', 'hey', 'start', 'begin']
        if any(greeting in text.lower() for greeting in greetings):
            response = self.generate_response('greeting')
            return {
                'response': response,
                'action': 'greeting',
                'extracted_intake': None
            }
        
        # Try to extract water intake
        extracted_intake = self.extract_water_intake(text)
        
        if extracted_intake:
            # User reported water intake
            new_total = current_intake + extracted_intake
            category = self.get_intake_category(new_total, daily_goal)
            
            remaining = max(0, daily_goal - new_total)
            excess = max(0, new_total - daily_goal)
            
            response = self.generate_response(
                category,
                intake=new_total,
                remaining=remaining,
                excess=excess,
                added=extracted_intake
            )
            
            return {
                'response': response,
                'action': 'log_intake',
                'extracted_intake': extracted_intake,
                'new_total': new_total,
                'category': category
            }
        
        # Check for status request
        status_keywords = ['status', 'progress', 'how much', 'total', 'goal']
        if any(keyword in text.lower() for keyword in status_keywords):
            category = self.get_intake_category(current_intake, daily_goal)
            remaining = max(0, daily_goal - current_intake)
            excess = max(0, current_intake - daily_goal)
            
            response = self.generate_response(
                category,
                intake=current_intake,
                remaining=remaining,
                excess=excess
            )
            
            return {
                'response': response,
                'action': 'status_check',
                'extracted_intake': None
            }
        
        # Default response for unclear input
        response = self.generate_response('error')
        return {
            'response': response,
            'action': 'error',
            'extracted_intake': None
        }

    def generate_reminder(self, current_intake: int, daily_goal: int) -> str:
        """
        Generate a sarcastic reminder message.
        
        Args:
            current_intake: Current daily water intake in ml
            daily_goal: Daily hydration goal in ml
            
        Returns:
            Sarcastic reminder message
        """
        remaining = max(0, daily_goal - current_intake)
        
        return self.generate_response(
            'reminder',
            intake=current_intake,
            remaining=remaining,
            goal=daily_goal
        )
