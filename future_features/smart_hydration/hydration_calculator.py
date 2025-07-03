"""
Hydration Calculator module for Smart Hydration feature.
Calculates recommended water intake based on weather conditions.
"""

import logging
from .weather_api import WeatherAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HydrationCalculator:
    """Class to calculate hydration recommendations based on weather."""
    
    def __init__(self, api_key=None):
        """
        Initialize the HydrationCalculator.
        
        Args:
            api_key (str, optional): OpenWeatherMap API key. If None, will try to load from environment.
        """
        self.weather_api = WeatherAPI(api_key)
        self.base_hydration = 2000  # Base recommendation in ml
    
    def calculate_temperature_adjustment(self, temperature):
        """
        Calculate hydration adjustment based on temperature.
        
        Args:
            temperature (float): Temperature in Celsius.
            
        Returns:
            int: Adjustment in ml.
        """
        if temperature is None:
            return 0
        
        if temperature > 25:
            # +200ml for every 5°C above 25°C
            return int(((temperature - 25) / 5) * 200)
        elif temperature < 15:
            # -100ml for every 5°C below 15°C (minimum 0 adjustment)
            return max(int(((temperature - 15) / 5) * 100), -500)
        else:
            # No adjustment for temperatures between 15-25°C
            return 0
    
    def calculate_humidity_adjustment(self, humidity):
        """
        Calculate hydration adjustment based on humidity.
        
        Args:
            humidity (int): Humidity percentage.
            
        Returns:
            int: Adjustment in ml.
        """
        if humidity is None:
            return 0
        
        if humidity > 70:
            # +100ml for high humidity
            return 100
        elif humidity < 40:
            # +50ml for low humidity (dry air)
            return 50
        else:
            # No adjustment for normal humidity
            return 0
    
    def calculate_activity_adjustment(self, activity_level):
        """
        Calculate hydration adjustment based on activity level.
        
        Args:
            activity_level (str): Activity level ('high', 'moderate', 'low').
            
        Returns:
            int: Adjustment in ml.
        """
        if activity_level == 'high':
            return 300
        elif activity_level == 'moderate':
            return 150
        else:
            return 0
    
    def get_recommendation(self, city=None, lat=None, lon=None, activity_level='low', base_hydration=None):
        """
        Get hydration recommendation based on weather and activity.
        
        Args:
            city (str, optional): City name. Defaults to None.
            lat (float, optional): Latitude. Defaults to None.
            lon (float, optional): Longitude. Defaults to None.
            activity_level (str, optional): Activity level. Defaults to 'low'.
            base_hydration (int, optional): Base hydration in ml. Defaults to class default.
            
        Returns:
            dict: Recommendation data including total and adjustments.
        """
        if base_hydration is not None:
            self.base_hydration = base_hydration
        
        # Get weather data
        temperature = self.weather_api.get_temperature(city=city, lat=lat, lon=lon)
        humidity = self.weather_api.get_humidity(city=city, lat=lat, lon=lon)
        weather_condition = self.weather_api.get_weather_condition(city=city, lat=lat, lon=lon)
        
        # Calculate adjustments
        temp_adjustment = self.calculate_temperature_adjustment(temperature)
        humidity_adjustment = self.calculate_humidity_adjustment(humidity)
        activity_adjustment = self.calculate_activity_adjustment(activity_level)
        
        # Calculate total recommendation (minimum 2000ml)
        total = max(self.base_hydration + temp_adjustment + humidity_adjustment + activity_adjustment, 2000)
        
        # Prepare recommendation data
        recommendation = {
            'base': self.base_hydration,
            'temperature': temperature,
            'humidity': humidity,
            'weather_condition': weather_condition,
            'temp_adjustment': temp_adjustment,
            'humidity_adjustment': humidity_adjustment,
            'activity_adjustment': activity_adjustment,
            'total': total,
            'explanation': self._generate_explanation(temperature, humidity, activity_level, 
                                                     temp_adjustment, humidity_adjustment, activity_adjustment)
        }
        
        logger.info(f"Hydration recommendation: {total}ml (base: {self.base_hydration}ml, "
                   f"temp: {temp_adjustment}ml, humidity: {humidity_adjustment}ml, "
                   f"activity: {activity_adjustment}ml)")
        
        return recommendation
    
    def _generate_explanation(self, temperature, humidity, activity_level, 
                             temp_adjustment, humidity_adjustment, activity_adjustment):
        """
        Generate human-readable explanation for the recommendation.
        
        Returns:
            str: Explanation text.
        """
        explanation = []
        
        # Temperature explanation
        if temperature is not None:
            if temp_adjustment > 0:
                explanation.append(f"It's hot ({temperature:.1f}°C), so you should drink more water.")
            elif temp_adjustment < 0:
                explanation.append(f"It's cool ({temperature:.1f}°C), but stay hydrated.")
        
        # Humidity explanation
        if humidity is not None:
            if humidity > 70:
                explanation.append(f"High humidity ({humidity}%) increases water loss through sweating.")
            elif humidity < 40:
                explanation.append(f"Dry air ({humidity}%) can cause more water loss through breathing.")
        
        # Activity explanation
        if activity_level != 'low':
            if activity_level == 'high':
                explanation.append("Your high activity level requires additional hydration.")
            else:
                explanation.append("Your moderate activity level requires some additional hydration.")
        
        # If no adjustments
        if not explanation:
            explanation.append("Standard hydration recommendation for your profile.")
        
        return " ".join(explanation)
