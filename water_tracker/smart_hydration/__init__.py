"""
Smart Hydration feature package.
Provides weather-based hydration recommendations.
"""

from .weather_api import WeatherAPI
from .hydration_calculator import HydrationCalculator
from .routes import init_app

__all__ = ['WeatherAPI', 'HydrationCalculator', 'init_app']
