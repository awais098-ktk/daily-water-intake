"""
Reminder Scheduler for Sarcastic Chatbot

This module handles periodic reminders to drink water with sarcastic messages.
"""

import threading
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

# Try to import schedule, make it optional
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReminderScheduler:
    """
    Scheduler for sending periodic sarcastic water intake reminders.
    """
    
    def __init__(self, app=None):
        """
        Initialize the reminder scheduler.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.running = False
        self.scheduler_thread = None
        self.reminder_intervals = {
            'frequent': 2,    # Every 2 hours
            'normal': 3,      # Every 3 hours
            'relaxed': 4      # Every 4 hours
        }
        self.user_preferences = {}  # Store user reminder preferences
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        self.app = app
        
        # Set up default reminder schedule
        self.setup_default_schedule()
        
        # Start scheduler in background
        self.start_scheduler()
        
        logger.info("Reminder scheduler initialized")
    
    def setup_default_schedule(self):
        """Set up default reminder schedule."""
        if not SCHEDULE_AVAILABLE:
            logger.warning("Schedule module not available, reminders disabled")
            return

        # Clear any existing jobs
        schedule.clear()

        # Schedule reminders every 3 hours during waking hours (8 AM to 10 PM)
        reminder_times = ['08:00', '11:00', '14:00', '17:00', '20:00']

        for time_str in reminder_times:
            schedule.every().day.at(time_str).do(self.send_scheduled_reminders)

        logger.info(f"Scheduled reminders at: {', '.join(reminder_times)}")
    
    def start_scheduler(self):
        """Start the background scheduler thread."""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("Reminder scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Reminder scheduler stopped")
    
    def _run_scheduler(self):
        """Background thread function to run the scheduler."""
        if not SCHEDULE_AVAILABLE:
            logger.warning("Schedule module not available, scheduler thread disabled")
            return

        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler thread: {e}")
                time.sleep(60)
    
    def send_scheduled_reminders(self):
        """Send reminders to all active users."""
        if not self.app:
            logger.warning("No Flask app available for sending reminders")
            return
        
        try:
            with self.app.app_context():
                active_users = self.get_active_users()
                
                for user_id in active_users:
                    self.send_reminder_to_user(user_id)
                
                logger.info(f"Sent reminders to {len(active_users)} users")
                
        except Exception as e:
            logger.error(f"Error sending scheduled reminders: {e}")
    
    def send_reminder_to_user(self, user_id: int):
        """
        Send a reminder to a specific user.
        
        Args:
            user_id: User ID to send reminder to
        """
        try:
            from .chatbot import SarcasticChatbot
            from .routes import get_user_daily_intake
            
            # Get user's current intake
            current_intake, daily_goal = get_user_daily_intake(user_id)
            
            # Generate sarcastic reminder
            chatbot = SarcasticChatbot()
            reminder = chatbot.generate_reminder(current_intake, daily_goal)
            
            # Store reminder for user to see when they next visit
            self.store_reminder(user_id, reminder, current_intake, daily_goal)
            
            logger.info(f"Generated reminder for user {user_id}: {reminder[:50]}...")
            
        except Exception as e:
            logger.error(f"Error sending reminder to user {user_id}: {e}")
    
    def store_reminder(self, user_id: int, reminder: str, current_intake: int, daily_goal: int):
        """
        Store reminder in database or cache for user to see later.
        
        Args:
            user_id: User ID
            reminder: Reminder message
            current_intake: Current water intake
            daily_goal: Daily goal
        """
        try:
            # Import here to avoid circular imports
            import sys
            
            # Get models from the main app
            main_module = None
            for module_name, module in sys.modules.items():
                if hasattr(module, 'db') and hasattr(module, 'User'):
                    main_module = module
                    break
            
            if not main_module:
                logger.warning("Could not find main app module for storing reminder")
                return
            
            # For now, we'll create a simple reminder storage system
            # In a production app, you might want to create a dedicated Reminder model
            
            # Store in a simple cache or session-like storage
            # This is a simplified implementation
            reminder_data = {
                'message': reminder,
                'current_intake': current_intake,
                'daily_goal': daily_goal,
                'timestamp': datetime.now().isoformat(),
                'seen': False
            }
            
            # You could extend this to store in database or Redis
            logger.info(f"Reminder stored for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing reminder: {e}")
    
    def get_active_users(self) -> List[int]:
        """
        Get list of active user IDs who should receive reminders.
        
        Returns:
            List of user IDs
        """
        try:
            # Import here to avoid circular imports
            import sys
            
            # Get models from the main app
            main_module = None
            for module_name, module in sys.modules.items():
                if hasattr(module, 'User') and hasattr(module, 'WaterLog'):
                    main_module = module
                    break
            
            if not main_module:
                logger.warning("Could not find main app module")
                return []
            
            User = main_module.User
            WaterLog = main_module.WaterLog
            
            # Get users who have logged water in the last 7 days
            # This indicates they're actively using the app
            week_ago = datetime.now() - timedelta(days=7)
            
            active_user_ids = (
                User.query
                .join(WaterLog)
                .filter(WaterLog.timestamp >= week_ago)
                .distinct(User.id)
                .with_entities(User.id)
                .all()
            )
            
            return [user_id[0] for user_id in active_user_ids]
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    def set_user_reminder_preference(self, user_id: int, interval: str):
        """
        Set reminder interval preference for a user.
        
        Args:
            user_id: User ID
            interval: 'frequent', 'normal', or 'relaxed'
        """
        if interval in self.reminder_intervals:
            self.user_preferences[user_id] = interval
            logger.info(f"Set reminder preference for user {user_id}: {interval}")
        else:
            logger.warning(f"Invalid reminder interval: {interval}")
    
    def get_user_reminder_preference(self, user_id: int) -> str:
        """
        Get reminder interval preference for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Reminder interval preference
        """
        return self.user_preferences.get(user_id, 'normal')
    
    def should_send_reminder(self, user_id: int) -> bool:
        """
        Check if a reminder should be sent to a user based on their last activity.
        
        Args:
            user_id: User ID
            
        Returns:
            True if reminder should be sent
        """
        try:
            from .routes import get_user_daily_intake
            
            # Get user's current intake
            current_intake, daily_goal = get_user_daily_intake(user_id)
            
            # Send reminder if user hasn't reached their goal
            if current_intake < daily_goal:
                return True
            
            # Don't send if they've already exceeded their goal significantly
            if current_intake > daily_goal * 1.2:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if reminder should be sent: {e}")
            return True  # Default to sending reminder
    
    def get_next_reminder_time(self) -> Optional[datetime]:
        """
        Get the next scheduled reminder time.

        Returns:
            Next reminder datetime or None
        """
        if not SCHEDULE_AVAILABLE:
            return None

        try:
            next_job = schedule.next_run()
            return next_job
        except Exception:
            return None

# Global scheduler instance
reminder_scheduler = None

def init_reminder_scheduler(app):
    """Initialize the global reminder scheduler."""
    global reminder_scheduler
    reminder_scheduler = ReminderScheduler(app)
    return reminder_scheduler

def get_reminder_scheduler():
    """Get the global reminder scheduler instance."""
    return reminder_scheduler
