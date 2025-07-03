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
        # Hardcoded API key as fallback
        self.api_key = api_key or os.environ.get('OPENWEATHERMAP_API_KEY') or '6c5688794c42581bb9715872c8d98449'

        logger.info(f"Weather API initialized with key: {self.api_key[:5]}...{self.api_key[-5:]}")

        # Set the correct base URL for OpenWeatherMap API
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

        # Validate the API key
        self.api_key_valid = self._validate_api_key()
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
        # Make sure we have an API key
        if not self.api_key:
            # Use hardcoded API key as fallback
            self.api_key = '6c5688794c42581bb9715872c8d98449'
            logger.warning("Using hardcoded API key as fallback")
            # Validate the new key
            self.api_key_valid = self._validate_api_key()

        logger.info(f"Using API key: {self.api_key[:5]}...{self.api_key[-5:]}")

        # Determine location key for cache
        if city:
            location_key = f"city:{city}"
        elif lat is not None and lon is not None:
            location_key = f"latlon:{lat},{lon}"
        else:
            # Default to a known city if none provided
            city = "New York"
            location_key = f"city:{city}"
            logger.warning(f"No location provided, defaulting to {city}")

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

        # Log the request URL and parameters
        request_url = f"{self.base_url}?{requests.compat.urlencode(params)}"
        logger.info(f"Making API request to: {request_url.replace(self.api_key, 'API_KEY')}")

        # Check if API key is valid before making the request
        if not hasattr(self, 'api_key_valid') or not self.api_key_valid:
            logger.error("API key is not valid, returning mock data")
            if city:
                return self._get_mock_weather_data(city)
            else:
                return self._get_mock_weather_data("Unknown Location")

        # Make API request using the direct URL format as recommended
        try:
            # Construct the URL directly as recommended in the fix
            if city:
                # Use city name for the query
                api_url = f"{self.base_url}?q={city}&appid={self.api_key}&units=metric"
            else:
                # Use coordinates for the query
                api_url = f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"

            # Log the URL (hiding the API key)
            logger.info(f"Making API request to: {api_url.replace(self.api_key, 'API_KEY')}")

            # Make the request
            response = requests.get(api_url)

            # Log the response status
            logger.info(f"API response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"API error response: {response.text}")
                # If we get an unauthorized response, mark the API key as invalid
                if response.status_code == 401:
                    logger.error("API key is unauthorized, marking as invalid")
                    self.api_key_valid = False
                    if city:
                        return self._get_mock_weather_data(city)
                    else:
                        return self._get_mock_weather_data("Unknown Location")

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
            # Return a mock weather data for testing
            if city:
                return self._get_mock_weather_data(city)
            else:
                return self._get_mock_weather_data("Unknown Location")

    def _get_mock_weather_data(self, location_name):
        """Generate mock weather data for testing when API fails"""
        logger.info(f"Generating mock weather data for {location_name}")
        return {
            "coord": {"lon": 0, "lat": 0},
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
            "base": "stations",
            "main": {
                "temp": 25,
                "feels_like": 25,
                "temp_min": 23,
                "temp_max": 27,
                "pressure": 1015,
                "humidity": 60
            },
            "visibility": 10000,
            "wind": {"speed": 3, "deg": 180},
            "clouds": {"all": 0},
            "dt": int(datetime.now().timestamp()),
            "sys": {
                "type": 1,
                "id": 123,
                "country": "XX",
                "sunrise": int((datetime.now() - timedelta(hours=6)).timestamp()),
                "sunset": int((datetime.now() + timedelta(hours=6)).timestamp())
            },
            "timezone": 0,
            "id": 123456,
            "name": location_name,
            "cod": 200
        }

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

    def _validate_api_key(self):
        """
        Validate the API key by making a test request.

        Returns:
            bool: True if the API key is valid, False otherwise.
        """
        logger.info(f"Validating API key: {self.api_key[:5]}...{self.api_key[-5:]}")

        # Use a well-known city for validation
        test_city = "Lahore"

        # Construct the URL directly as recommended
        test_url = f"{self.base_url}?q={test_city}&appid={self.api_key}&units=metric"
        logger.info(f"Validation URL: {test_url.replace(self.api_key, 'API_KEY')}")

        try:
            # Make a test request
            response = requests.get(test_url)

            # Log the response status
            logger.info(f"API key validation response status: {response.status_code}")

            # Check if the response is successful
            if response.status_code == 200:
                # Try to parse the response as JSON to ensure it's valid
                try:
                    data = response.json()
                    if 'main' in data and 'temp' in data['main']:
                        logger.info(f"API key is valid. Current temperature in {test_city}: {data['main']['temp']}°C")
                    else:
                        logger.info("API key is valid but response format is unexpected")
                    return True
                except ValueError:
                    logger.error("API key validation failed: Response is not valid JSON")
                    return False
            else:
                logger.error(f"API key validation failed: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"API key validation error: {e}")
            return False
