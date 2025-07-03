"""
Smart Hydration feature package.
Provides weather-based hydration recommendations.
"""

from .weather_api import WeatherAPI
from .hydration_calculator import HydrationCalculator
from .integration import smart_hydration_bp, init_app

__all__ = ['WeatherAPI', 'HydrationCalculator', 'smart_hydration_bp', 'init_app']
