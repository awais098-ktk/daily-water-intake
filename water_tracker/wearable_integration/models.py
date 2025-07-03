"""
Database models for wearable integration
"""

from datetime import datetime, timezone

# Import db from the main app - this will be set during initialization
db = None

def get_models():
    """Get the wearable integration models"""
    # Import here to avoid circular imports
    from flask import current_app

    # Get the main app's database
    app_db = current_app.extensions['sqlalchemy']

    # Define models using the main app's database
    class WearableConnection(app_db.Model):
        """Model to store user's wearable device connections"""
        __tablename__ = 'wearable_connections'

        id = app_db.Column(app_db.Integer, primary_key=True)
        user_id = app_db.Column(app_db.Integer, app_db.ForeignKey('user.id'), nullable=False)
        platform = app_db.Column(app_db.String(50), nullable=False)  # 'google_fit', 'fitbit', etc.
        platform_user_id = app_db.Column(app_db.String(100), nullable=False)
        access_token = app_db.Column(app_db.Text, nullable=False)
        refresh_token = app_db.Column(app_db.Text)
        token_expires_at = app_db.Column(app_db.DateTime)
        is_active = app_db.Column(app_db.Boolean, default=True)
        connected_at = app_db.Column(app_db.DateTime, default=lambda: datetime.now(timezone.utc))
        last_sync = app_db.Column(app_db.DateTime)

        def __repr__(self):
            return f'<WearableConnection {self.platform} for user {self.user_id}>'

        def is_token_expired(self):
            """Check if the access token is expired"""
            if not self.token_expires_at:
                return False
            # Ensure both datetimes have the same timezone for comparison
            token_expires = self.token_expires_at
            if token_expires.tzinfo is None:
                token_expires = token_expires.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) > token_expires

        def to_dict(self):
            """Convert to dictionary for JSON serialization"""
            return {
                'id': self.id,
                'platform': self.platform,
                'platform_user_id': self.platform_user_id,
                'is_active': self.is_active,
                'connected_at': self.connected_at.isoformat() if self.connected_at else None,
                'last_sync': self.last_sync.isoformat() if self.last_sync else None,
                'token_expired': self.is_token_expired()
            }

    class ActivityData(app_db.Model):
        """Model to store synced activity data from wearables"""
        __tablename__ = 'activity_data'

        id = app_db.Column(app_db.Integer, primary_key=True)
        user_id = app_db.Column(app_db.Integer, app_db.ForeignKey('user.id'), nullable=False)
        connection_id = app_db.Column(app_db.Integer, app_db.ForeignKey('wearable_connections.id'), nullable=False)
        date = app_db.Column(app_db.Date, nullable=False)
        steps = app_db.Column(app_db.Integer, default=0)
        distance_meters = app_db.Column(app_db.Float, default=0.0)
        calories_burned = app_db.Column(app_db.Integer, default=0)
        active_minutes = app_db.Column(app_db.Integer, default=0)
        heart_rate_avg = app_db.Column(app_db.Integer)
        heart_rate_max = app_db.Column(app_db.Integer)
        exercise_sessions = app_db.Column(app_db.JSON)  # Store detailed exercise data
        # Sleep data fields
        sleep_duration_minutes = app_db.Column(app_db.Integer)  # Total sleep duration in minutes
        sleep_efficiency = app_db.Column(app_db.Float)  # Sleep efficiency percentage (0-100)
        deep_sleep_minutes = app_db.Column(app_db.Integer)  # Deep sleep duration in minutes
        light_sleep_minutes = app_db.Column(app_db.Integer)  # Light sleep duration in minutes
        rem_sleep_minutes = app_db.Column(app_db.Integer)  # REM sleep duration in minutes
        awake_minutes = app_db.Column(app_db.Integer)  # Time awake during sleep period
        sleep_start_time = app_db.Column(app_db.DateTime)  # When sleep started
        sleep_end_time = app_db.Column(app_db.DateTime)  # When sleep ended
        created_at = app_db.Column(app_db.DateTime, default=lambda: datetime.now(timezone.utc))
        updated_at = app_db.Column(app_db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

        # Unique constraint to prevent duplicate data for same day
        __table_args__ = (app_db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

        def __repr__(self):
            return f'<ActivityData {self.date} for user {self.user_id}>'

        def calculate_activity_level(self):
            """Calculate activity level based on steps and active minutes"""
            if self.steps >= 10000 or self.active_minutes >= 60:
                return 'high'
            elif self.steps >= 5000 or self.active_minutes >= 30:
                return 'moderate'
            elif self.steps >= 2000 or self.active_minutes >= 15:
                return 'low'
            else:
                return 'sedentary'

        def to_dict(self):
            """Convert to dictionary for JSON serialization"""
            return {
                'id': self.id,
                'date': self.date.isoformat() if self.date else None,
                'steps': self.steps,
                'distance_meters': self.distance_meters,
                'calories_burned': self.calories_burned,
                'active_minutes': self.active_minutes,
                'heart_rate_avg': self.heart_rate_avg,
                'heart_rate_max': self.heart_rate_max,
                'activity_level': self.calculate_activity_level(),
                'exercise_sessions': self.exercise_sessions,
                # Sleep data
                'sleep_duration_minutes': self.sleep_duration_minutes,
                'sleep_efficiency': self.sleep_efficiency,
                'deep_sleep_minutes': self.deep_sleep_minutes,
                'light_sleep_minutes': self.light_sleep_minutes,
                'rem_sleep_minutes': self.rem_sleep_minutes,
                'awake_minutes': self.awake_minutes,
                'sleep_start_time': self.sleep_start_time.isoformat() if self.sleep_start_time else None,
                'sleep_end_time': self.sleep_end_time.isoformat() if self.sleep_end_time else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    class HydrationRecommendation(app_db.Model):
        """Model to store activity-based hydration recommendations"""
        __tablename__ = 'hydration_recommendations'

        id = app_db.Column(app_db.Integer, primary_key=True)
        user_id = app_db.Column(app_db.Integer, app_db.ForeignKey('user.id'), nullable=False)
        activity_data_id = app_db.Column(app_db.Integer, app_db.ForeignKey('activity_data.id'), nullable=False)
        date = app_db.Column(app_db.Date, nullable=False)
        base_recommendation = app_db.Column(app_db.Integer, nullable=False)  # Base daily goal in ml
        activity_bonus = app_db.Column(app_db.Integer, default=0)  # Additional ml for activity
        total_recommendation = app_db.Column(app_db.Integer, nullable=False)  # Total recommended ml
        reasoning = app_db.Column(app_db.Text)  # Explanation of the recommendation
        created_at = app_db.Column(app_db.DateTime, default=lambda: datetime.now(timezone.utc))

        def __repr__(self):
            return f'<HydrationRecommendation {self.date} for user {self.user_id}: {self.total_recommendation}ml>'

        def to_dict(self):
            """Convert to dictionary for JSON serialization"""
            return {
                'id': self.id,
                'date': self.date.isoformat() if self.date else None,
                'base_recommendation': self.base_recommendation,
                'activity_bonus': self.activity_bonus,
                'total_recommendation': self.total_recommendation,
                'reasoning': self.reasoning,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    return WearableConnection, ActivityData, HydrationRecommendation

# Placeholder classes that will be replaced
class WearableConnection:
    pass

class ActivityData:
    pass

class HydrationRecommendation:
    pass
