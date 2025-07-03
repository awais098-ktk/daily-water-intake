"""
Weather API module for Smart Hydration feature.
Fetches weather data from OpenWeatherMap API.
"""

import os
import json
import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherAPI:
    """Class to handle weather API interactions."""
    
    def __init__(self, api_key=None, cache_duration=30):
        """
        Initialize the WeatherAPI.
        
        Args:
            api_key (str, optional): OpenWeatherMap API key. If None, will try to load from environment.
            cache_duration (int, optional): Cache duration in minutes. Defaults to 30.
        """
        self.api_key = api_key or os.environ.get('OPENWEATHERMAP_API_KEY')
        if not self.api_key:
            logger.warning("No OpenWeatherMap API key provided. Weather features will be disabled.")
        
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.cache_file = os.path.join(os.path.dirname(__file__), 'weather_cache.json')
        self.cache_duration = timedelta(minutes=cache_duration)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cached weather data if available."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    # Convert timestamp string to datetime
                    for location, data in cache.items():
                        if 'timestamp' in data:
                            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    return cache
        except Exception as e:
            logger.error(f"Error loading weather cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save weather data to cache file."""
        try:
            # Convert datetime to string for JSON serialization
            serializable_cache = {}
            for location, data in self.cache.items():
                serializable_cache[location] = data.copy()
                if 'timestamp' in serializable_cache[location]:
                    serializable_cache[location]['timestamp'] = data['timestamp'].isoformat()
            
            with open(self.cache_file, 'w') as f:
                json.dump(serializable_cache, f)
        except Exception as e:
            logger.error(f"Error saving weather cache: {e}")
    
    def get_weather(self, city=None, lat=None, lon=None, use_cache=True):
        """
        Get current weather data for a location.
        
        Args:
            city (str, optional): City name. Defaults to None.
            lat (float, optional): Latitude. Defaults to None.
            lon (float, optional): Longitude. Defaults to None.
            use_cache (bool, optional): Whether to use cached data if available. Defaults to True.
            
        Returns:
            dict: Weather data or None if request failed.
        """
        if not self.api_key:
            logger.error("Cannot fetch weather: No API key provided")
            return None
        
        # Determine location key for cache
        if city:
            location_key = f"city:{city}"
        elif lat is not None and lon is not None:
            location_key = f"latlon:{lat},{lon}"
        else:
            logger.error("Either city or lat/lon must be provided")
            return None
        
        # Check cache if enabled
        now = datetime.now()
        if use_cache and location_key in self.cache:
            cache_entry = self.cache[location_key]
            if now - cache_entry['timestamp'] < self.cache_duration:
                logger.info(f"Using cached weather data for {location_key}")
                return cache_entry['data']
        
        # Prepare API request
        params = {
            'appid': self.api_key,
            'units': 'metric'  # Use metric units (Celsius)
        }
        
        if city:
            params['q'] = city
        else:
            params['lat'] = lat
            params['lon'] = lon
        
        # Make API request
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            # Cache the result
            self.cache[location_key] = {
                'timestamp': now,
                'data': weather_data
            }
            self._save_cache()
            
            logger.info(f"Successfully fetched weather data for {location_key}")
            return weather_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def get_temperature(self, city=None, lat=None, lon=None):
        """
        Get current temperature for a location.
        
        Returns:
            float: Temperature in Celsius or None if request failed.
        """
        weather_data = self.get_weather(city=city, lat=lat, lon=lon)
        if weather_data and 'main' in weather_data and 'temp' in weather_data['main']:
            return weather_data['main']['temp']
        return None
    
    def get_humidity(self, city=None, lat=None, lon=None):
        """
        Get current humidity for a location.
        
        Returns:
            int: Humidity percentage or None if request failed.
        """
        weather_data = self.get_weather(city=city, lat=lat, lon=lon)
        if weather_data and 'main' in weather_data and 'humidity' in weather_data['main']:
            return weather_data['main']['humidity']
        return None
    
    def get_weather_condition(self, city=None, lat=None, lon=None):
        """
        Get current weather condition for a location.
        
        Returns:
            str: Weather condition description or None if request failed.
        """
        weather_data = self.get_weather(city=city, lat=lat, lon=lon)
        if weather_data and 'weather' in weather_data and len(weather_data['weather']) > 0:
            return weather_data['weather'][0]['description']
        return None
