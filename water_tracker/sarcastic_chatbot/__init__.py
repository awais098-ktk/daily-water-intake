"""
Sarcastic Chatbot Module for Water Intake Tracker

This module provides a sarcastic AI chatbot that integrates with the water intake
tracking system to provide humorous reminders and feedback about hydration habits.

Features:
- Sarcastic responses based on water intake progress
- Periodic reminders to drink water
- Integration with existing water tracking data
- Personality-driven conversation flow
"""

from .chatbot import SarcasticChatbot
from .routes import chatbot_bp
from .scheduler import ReminderScheduler

__all__ = ['SarcasticChatbot', 'chatbot_bp', 'ReminderScheduler']

def init_app(app):
    """Initialize the sarcastic chatbot with the Flask app."""
    from .routes import init_chatbot_routes
    init_chatbot_routes(app)
