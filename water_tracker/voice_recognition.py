"""
Simplified voice recognition module for Water Intake Tracker
This version works without requiring speech_recognition or pydub
"""

import re
import logging
import json
import os
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
VOLUME_PATTERNS = [
    r'(\d+)\s*ml',  # 500ml
    r'(\d+)\s*milliliter',  # 500 milliliters
    r'(\d+)\s*cl',  # 33cl
    r'(\d+)\s*l',  # 1l or 1 l
    r'(\d+\.\d+)\s*l',  # 1.5l
    r'(\d+)\s*oz',  # 16oz
    r'(\d+)\s*ounce',  # 16 ounces
    r'(\d+)\s*cup',  # 2 cups
    r'half\s*a\s*cup',  # half a cup
    r'quarter\s*cup',  # quarter cup
    r'(\d+)\s*glass',  # 1 glass
]

# Conversion factors to ml
CONVERSION_FACTORS = {
    'ml': 1,
    'milliliter': 1,
    'cl': 10,  # 1cl = 10ml
    'l': 1000,  # 1l = 1000ml
    'oz': 29.5735,  # 1oz = 29.5735ml
    'ounce': 29.5735,
    'cup': 236.588,  # 1 cup = 236.588ml
    'glass': 250,  # Assuming 1 glass = 250ml
    'half a cup': 118.294,  # Half cup = 118.294ml
    'quarter cup': 59.147  # Quarter cup = 59.147ml
}

# Drink type keywords
DRINK_TYPES = {
    'water': ['water', 'h2o'],
    'tea': ['tea', 'green tea', 'black tea', 'herbal tea'],
    'coffee': ['coffee', 'espresso', 'latte', 'cappuccino'],
    'milk': ['milk', 'almond milk', 'soy milk', 'oat milk'],
    'juice': ['juice', 'orange juice', 'apple juice', 'fruit juice'],
    'soda': ['soda', 'coke', 'pepsi', 'sprite', 'soft drink']
}

# Food-related patterns and keywords
FOOD_PATTERNS = [
    r'(\d+)\s*gram[s]?\s*of\s*(.+)',  # 100 grams of chicken
    r'(\d+)\s*g\s*of\s*(.+)',  # 100g of rice
    r'(\d+)\s*ounce[s]?\s*of\s*(.+)',  # 4 ounces of salmon
    r'(\d+)\s*oz\s*of\s*(.+)',  # 4oz of nuts
    r'(\d+)\s*piece[s]?\s*of\s*(.+)',  # 2 pieces of bread
    r'(\d+)\s*slice[s]?\s*of\s*(.+)',  # 3 slices of cheese
    r'(\d+)\s*cup[s]?\s*of\s*(.+)',  # 1 cup of rice
    r'a\s*(.+)',  # a banana
    r'an\s*(.+)',  # an apple
    r'some\s*(.+)',  # some nuts
]

FOOD_KEYWORDS = {
    'fruits': ['apple', 'banana', 'orange', 'berry', 'grape', 'strawberry', 'blueberry'],
    'vegetables': ['broccoli', 'carrot', 'spinach', 'tomato', 'lettuce', 'cucumber'],
    'proteins': ['chicken', 'beef', 'fish', 'salmon', 'egg', 'tofu', 'beans'],
    'grains': ['rice', 'bread', 'pasta', 'oats', 'quinoa', 'cereal'],
    'dairy': ['cheese', 'yogurt', 'butter', 'cream'],
    'snacks': ['nuts', 'chips', 'crackers', 'cookies', 'almonds', 'peanuts'],
    'sweets': ['chocolate', 'candy', 'cake', 'ice cream', 'cookie']
}

MEAL_TYPE_KEYWORDS = {
    'breakfast': ['breakfast', 'morning meal', 'morning'],
    'lunch': ['lunch', 'midday meal', 'noon'],
    'dinner': ['dinner', 'evening meal', 'supper'],
    'snack': ['snack', 'snacking', 'between meals']
}

# Weight/quantity conversion factors to grams
FOOD_CONVERSION_FACTORS = {
    'gram': 1,
    'grams': 1,
    'g': 1,
    'ounce': 28.35,
    'ounces': 28.35,
    'oz': 28.35,
    'piece': 50,  # Average piece weight
    'pieces': 50,
    'slice': 30,  # Average slice weight
    'slices': 30,
    'cup': 150,  # Average cup weight for solid foods
    'cups': 150
}

class VoiceProcessor:
    """Simplified class for voice processing operations"""

    def __init__(self):
        """Initialize the voice processor"""
        # Sample voice inputs for simulation (drinks)
        self.sample_drink_inputs = [
            "I drank 250 ml of water",
            "I had a cup of coffee",
            "I drank 500 ml of water",
            "I had 330 ml of soda",
            "I drank a glass of juice",
            "I had 200 ml of tea",
            "I drank 350 ml of pepsi",
            "I had a bottle of water",
            "I drank half a cup of milk"
        ]

        # Food inputs are no longer supported - keeping for reference only
        self.sample_food_inputs = []

    def extract_volume(self, text):
        """Extract volume information from text"""
        try:
            # Convert text to lowercase for easier matching
            text = text.lower()

            # Try each pattern
            for pattern in VOLUME_PATTERNS:
                matches = re.findall(pattern, text)
                if matches:
                    # Get the first match
                    volume_str = matches[0] if isinstance(matches[0], str) else matches[0][0]

                    # Handle special cases
                    if pattern == r'half\s*a\s*cup':
                        return 118  # ~118ml
                    elif pattern == r'quarter\s*cup':
                        return 59  # ~59ml

                    # Convert to float
                    volume = float(volume_str)

                    # Determine unit and apply conversion factor
                    unit = re.search(pattern, text).group(0).replace(volume_str, '').strip()

                    # Find the appropriate conversion factor
                    conversion_factor = 1  # Default to ml
                    for key, factor in CONVERSION_FACTORS.items():
                        if key in unit:
                            conversion_factor = factor
                            break

                    # Convert to ml
                    volume_ml = int(volume * conversion_factor)

                    return volume_ml

            # If no volume found, return a random volume
            return random.choice([200, 250, 330, 350, 500])

        except Exception as e:
            logger.error(f"Error extracting volume: {e}")
            return 250  # Default to 250ml

    def extract_drink_type(self, text):
        """Extract drink type from text"""
        try:
            # Convert text to lowercase for easier matching
            text = text.lower()

            # Check for each drink type
            for drink_type, keywords in DRINK_TYPES.items():
                for keyword in keywords:
                    if keyword in text:
                        return drink_type

            # Default to water if no match
            return 'water'

        except Exception as e:
            logger.error(f"Error extracting drink type: {e}")
            return 'water'

    def extract_food_info(self, text):
        """Extract food information from text"""
        try:
            # Convert text to lowercase for easier matching
            text = text.lower()

            # Initialize result
            result = {
                'food_name': None,
                'quantity_g': 100,  # Default quantity
                'meal_type': 'snack'  # Default meal type
            }

            # Try each food pattern
            for pattern in FOOD_PATTERNS:
                matches = re.findall(pattern, text)
                if matches:
                    if len(matches[0]) == 2:  # Pattern with quantity and food
                        quantity_str, food_name = matches[0]

                        # Extract quantity
                        try:
                            quantity = float(quantity_str)

                            # Determine unit from pattern
                            if 'gram' in pattern or 'g' in pattern:
                                result['quantity_g'] = quantity
                            elif 'ounce' in pattern or 'oz' in pattern:
                                result['quantity_g'] = quantity * FOOD_CONVERSION_FACTORS['ounce']
                            elif 'piece' in pattern:
                                result['quantity_g'] = quantity * FOOD_CONVERSION_FACTORS['piece']
                            elif 'slice' in pattern:
                                result['quantity_g'] = quantity * FOOD_CONVERSION_FACTORS['slice']
                            elif 'cup' in pattern:
                                result['quantity_g'] = quantity * FOOD_CONVERSION_FACTORS['cup']

                            result['food_name'] = food_name.strip()
                            break

                        except ValueError:
                            continue
                    else:  # Pattern with just food name (a/an/some)
                        food_name = matches[0]
                        result['food_name'] = food_name.strip()
                        result['quantity_g'] = 100  # Default quantity
                        break

            # If no pattern matched, try to extract food name from keywords
            if not result['food_name']:
                for category, keywords in FOOD_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword in text:
                            result['food_name'] = keyword
                            break
                    if result['food_name']:
                        break

            # Extract meal type
            result['meal_type'] = self.extract_meal_type(text)

            return result

        except Exception as e:
            logger.error(f"Error extracting food info: {e}")
            return {
                'food_name': 'unknown food',
                'quantity_g': 100,
                'meal_type': 'snack'
            }

    def extract_meal_type(self, text):
        """Extract meal type from text"""
        try:
            text = text.lower()

            # Check for meal type keywords
            for meal_type, keywords in MEAL_TYPE_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text:
                        return meal_type

            # Default based on time if no explicit meal type
            from datetime import datetime
            current_hour = datetime.now().hour

            if 5 <= current_hour < 11:
                return 'breakfast'
            elif 11 <= current_hour < 16:
                return 'lunch'
            elif 16 <= current_hour < 22:
                return 'dinner'
            else:
                return 'snack'

        except Exception as e:
            logger.error(f"Error extracting meal type: {e}")
            return 'snack'

    def is_food_input(self, text):
        """Determine if the input is about food rather than drinks"""
        text = text.lower()

        # Food indicators
        food_indicators = ['ate', 'eat', 'eating', 'had', 'consumed', 'food', 'meal']
        drink_indicators = ['drank', 'drink', 'drinking', 'sipped', 'beverage']

        # Check for explicit food/drink indicators
        has_food_indicator = any(indicator in text for indicator in food_indicators)
        has_drink_indicator = any(indicator in text for indicator in drink_indicators)

        if has_food_indicator and not has_drink_indicator:
            return True
        elif has_drink_indicator and not has_food_indicator:
            return False

        # Check for food keywords
        for category, keywords in FOOD_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return True

        # Check for drink keywords
        for drink_type, keywords in DRINK_TYPES.items():
            if any(keyword in text for keyword in keywords):
                return False

        # Check for food-specific units
        food_units = ['gram', 'grams', 'g', 'piece', 'pieces', 'slice', 'slices']
        if any(unit in text for unit in food_units):
            return True

        # Default to drink if unclear
        return False

    def process_voice_input(self, audio_file):
        """
        Simulate processing voice input
        In a real implementation, this would use speech recognition
        """
        try:
            # Check if the audio file exists
            if not os.path.exists(audio_file):
                logger.error(f"Audio file not found: {audio_file}")
                return {
                    'success': False,
                    'error': f"Audio file not found: {audio_file}",
                    'text': ""
                }

            # Log the audio file details
            logger.info(f"Processing audio file: {audio_file}")
            logger.info(f"File size: {os.path.getsize(audio_file)} bytes")

            # Simulate transcription by selecting a random drink sample
            # Food input is no longer supported
            text = random.choice(self.sample_drink_inputs)
            input_type = 'drink'

            return self.process_text_input(text)

        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'text': ""
            }

    def process_text_input(self, text):
        """Process text input and determine if it's food or drink"""
        try:
            logger.info(f"Processing text input: {text}")

            # Determine if this is food or drink input
            is_food = self.is_food_input(text)

            if is_food:
                # Food input is no longer supported
                return {
                    'success': False,
                    'type': 'food',
                    'error': 'Food logging via voice is not supported. Please use the eating tracker manually.',
                    'text': text
                }
            else:
                # Process as drink input
                volume = self.extract_volume(text)
                drink_type = self.extract_drink_type(text)

                return {
                    'success': True,
                    'type': 'drink',
                    'volume_ml': volume,
                    'drink_type': drink_type,
                    'text': text
                }

        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': text
            }
