"""
Wearable Integration Module for Water Intake Tracker

This module provides integration with popular wearable devices and fitness apps
to sync physical activity data and provide personalized hydration recommendations.

Supported platforms:
- Google Fit API
- Fitbit API
- Apple HealthKit (future)
"""

from flask import Blueprint
from .routes import wearable_bp
from .fitness_apis import GoogleFitAPI, FitbitAPI
from .activity_calculator import ActivityHydrationCalculator

def init_app(app):
    """Initialize the wearable integration feature with the Flask app."""

    # The models are already defined in the main app.py file
    # We don't need to create them again here

    # Initialize OAuth manager
    from .routes import init_oauth_manager
    init_oauth_manager(app.config)

    # Register the blueprint
    app.register_blueprint(wearable_bp, url_prefix='/wearable')

    # Add template globals
    @app.context_processor
    def inject_wearable_context():
        return {
            'wearable_integration_available': True,
            'supported_wearables': ['google_fit', 'fitbit'],
            'oauth_configured': bool(
                app.config.get('GOOGLE_FIT_CLIENT_ID') or
                app.config.get('FITBIT_CLIENT_ID')
            )
        }

    print("Wearable Integration feature initialized successfully!")

__all__ = [
    'init_app',
    'WearableConnection', 
    'ActivityData',
    'GoogleFitAPI',
    'FitbitAPI', 
    'ActivityHydrationCalculator'
]
