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
        """Initialize the sarcastic chatbot with personality responses and app knowledge."""
        # App features knowledge base
        self.app_features = {
            'water_tracking': {
                'description': 'Track your daily water intake with multiple logging methods',
                'features': [
                    'Manual water logging with custom amounts',
                    'Quick-add buttons for common container sizes',
                    'Voice recognition for hands-free logging',
                    'OCR (camera) to scan water bottles and containers',
                    'Daily progress tracking with visual charts',
                    'Customizable daily hydration goals'
                ]
            },
            'google_fit': {
                'description': 'Connect with Google Fit to sync activity data and get personalized hydration recommendations',
                'features': [
                    'Automatic activity data sync from Google Fit',
                    'Steps, distance, and calories tracking',
                    'Activity-based hydration recommendations',
                    'Automatic token refresh for seamless sync',
                    'Historical activity data import'
                ]
            },
            'containers': {
                'description': 'Manage your water containers and bottles for accurate tracking',
                'features': [
                    'Add custom containers with specific volumes',
                    'Set default containers for quick logging',
                    'Container history and usage tracking',
                    'Quick-select from favorite containers'
                ]
            },
            'dashboard': {
                'description': 'Comprehensive overview of your hydration progress and health data',
                'features': [
                    'Real-time hydration progress with visual indicators',
                    'Daily, weekly, and monthly progress charts',
                    'Activity data integration from wearables',
                    'Weather-based hydration recommendations',
                    'Achievement badges and milestones'
                ]
            },
            'chatbot': {
                'description': 'AI-powered hydration assistant (that\'s me!) to help and guide you',
                'features': [
                    'Natural language water intake logging',
                    'Personalized hydration advice and reminders',
                    'App feature explanations and help',
                    'Sarcastic but helpful personality',
                    'Voice and text interaction support'
                ]
            },
            'voice_ocr': {
                'description': 'Advanced input methods for convenient water logging',
                'features': [
                    'Voice recognition: "I drank 500ml" or "Add 2 glasses"',
                    'Camera OCR: Scan water bottles to detect volume',
                    'Smart text recognition from bottle labels',
                    'Hands-free operation for busy lifestyles'
                ]
            },
            'analytics': {
                'description': 'Detailed insights into your hydration patterns and health',
                'features': [
                    'Hydration trend analysis over time',
                    'Activity correlation with water intake',
                    'Goal achievement statistics',
                    'Weekly and monthly progress reports',
                    'Personalized recommendations based on patterns'
                ]
            }
        }

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
            ],
            'help_general': [
                "Oh, you need help? How surprising! I can explain any app feature - just ask about 'water tracking', 'Google Fit', 'containers', 'dashboard', 'voice commands', or 'OCR scanning'.",
                "Lost already? Typical! Ask me about specific features like 'How do I track water?', 'What is Google Fit?', or 'How to use voice commands?'",
                "Need a tour guide for your own hydration app? I can explain water tracking, Google Fit sync, container management, dashboard features, and more. Just ask!",
                "Confused about how to stay hydrated? Revolutionary! Ask me about any feature: water logging, activity sync, voice commands, camera scanning, or dashboard analytics."
            ],
            'feature_explanation': [
                "Here's what {feature_name} does: {description}\n\nKey features:\n{features_list}\n\nNow stop being confused and start using it!",
                "Oh, you want to know about {feature_name}? Fine! {description}\n\nWhat it includes:\n{features_list}\n\nThere, I've done your homework for you.",
                "Let me educate you about {feature_name}: {description}\n\nFeatures you should actually use:\n{features_list}\n\nYou're welcome for the free lesson!"
            ],
            'how_to_water': [
                "Seriously? You need instructions on drinking water? Fine! You can log water by typing amounts like '500ml' or 'I drank 2 glasses', use the dashboard buttons, speak to me with voice commands, or scan bottles with your camera. Revolutionary concepts, I know.",
                "Water tracking for beginners: Type how much you drank, click the quick-add buttons, use voice commands, or scan containers with OCR. It's almost like the app was designed for this!",
                "Let me spell it out: Manual entry (type amounts), Quick buttons (dashboard), Voice commands ('I drank 300ml'), or Camera scanning (point and shoot). Pick your favorite method of basic human survival."
            ],
            'how_to_google_fit': [
                "Google Fit integration? Finally, some ambition! Go to the wearable connection page, click 'Connect Google Fit', authorize the app, and boom - your activity data syncs automatically. Your phone does the thinking so you don't have to!",
                "Want Google Fit sync? Navigate to wearable connections, connect your Google account, and let the magic happen. Your steps, activities, and calories will sync automatically. Technology is amazing when you actually use it!",
                "Google Fit setup: Wearable page → Connect Google Fit → Authorize → Automatic sync. Your activity data helps me give better hydration recommendations. You're welcome for the personalized service!"
            ],
            'how_to_voice': [
                "Voice commands? Look at you being all futuristic! Just say things like 'I drank 500ml', 'Add 2 glasses', or 'Log 1 bottle'. The app listens and logs automatically. It's like having a personal assistant, except I'm sarcastic.",
                "Voice logging is simple even for you: Speak naturally like 'I had 300ml' or 'Add one glass'. The app understands and logs it. Finally, technology that works with your lazy lifestyle!",
                "Voice commands for the speech-enabled: Say your water intake naturally - '500ml', '2 cups', 'one bottle'. The app converts speech to logs. It's like magic, but with more hydration!"
            ],
            'how_to_ocr': [
                "Camera scanning? Fancy! Point your camera at water bottles, containers, or labels. The OCR reads the volume automatically and logs it. It's like having X-ray vision, but for hydration tracking!",
                "OCR scanning for the visually inclined: Camera → Point at container → Automatic volume detection → Instant logging. The app reads what you're too lazy to type. Brilliant!",
                "Scan containers with your camera and let the app do the reading. Point, shoot, and the volume gets detected automatically. It's almost like the future, but for water tracking!"
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

    def get_feature_explanation(self, feature_key: str) -> str:
        """Get detailed explanation of an app feature."""
        if feature_key not in self.app_features:
            return "I don't know about that feature. Try asking about 'water tracking', 'Google Fit', 'containers', 'dashboard', 'voice commands', or 'OCR scanning'."

        feature = self.app_features[feature_key]
        features_list = '\n'.join([f"• {feature}" for feature in feature['features']])

        return self.generate_response('feature_explanation',
            feature_name=feature_key.replace('_', ' ').title(),
            description=feature['description'],
            features_list=features_list
        )

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

        text_lower = text.lower()

        # Check for help requests
        help_keywords = ['help', 'how', 'what', 'explain', 'guide', 'tutorial', 'features']
        if any(keyword in text_lower for keyword in help_keywords):
            # Check for specific feature help
            if 'water' in text_lower and ('track' in text_lower or 'log' in text_lower):
                response = self.generate_response('how_to_water')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            elif 'google fit' in text_lower or 'google' in text_lower:
                response = self.generate_response('how_to_google_fit')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            elif 'voice' in text_lower:
                response = self.generate_response('how_to_voice')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            elif 'ocr' in text_lower or 'camera' in text_lower or 'scan' in text_lower:
                response = self.generate_response('how_to_ocr')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            elif 'container' in text_lower:
                response = self.get_feature_explanation('containers')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            elif 'dashboard' in text_lower:
                response = self.get_feature_explanation('dashboard')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            elif 'feature' in text_lower:
                response = self.generate_response('help_general')
                return {'response': response, 'action': 'help', 'extracted_intake': None}
            else:
                response = self.generate_response('help_general')
                return {'response': response, 'action': 'help', 'extracted_intake': None}

        # Check for specific feature questions
        for feature_key in self.app_features.keys():
            feature_name = feature_key.replace('_', ' ')
            if feature_name in text_lower or feature_key in text_lower:
                response = self.get_feature_explanation(feature_key)
                return {'response': response, 'action': 'feature_info', 'extracted_intake': None}

        # Check for greeting
        greetings = ['hello', 'hi', 'hey', 'start', 'begin']
        if any(greeting in text_lower for greeting in greetings):
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
