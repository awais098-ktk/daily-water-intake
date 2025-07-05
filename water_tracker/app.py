from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import os
import secrets
import json
import shutil
import random
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename



# Import custom modules with error handling
try:
    from water_tracker.image_processing import ImageProcessor
    image_processing_available = True
except ImportError:
    try:
        from image_processing import ImageProcessor
        image_processing_available = True
    except ImportError:
        print("Warning: Image processing module not available. Container recognition feature will be disabled.")
        image_processing_available = False

try:
    from water_tracker.ocr import OCRProcessor
    ocr_available = True
except ImportError:
    try:
        from ocr import OCRProcessor
        ocr_available = True
    except ImportError:
        print("Warning: OCR module not available. Label reading feature will be disabled.")
        ocr_available = False

try:
    from water_tracker.voice_recognition import VoiceProcessor
    voice_recognition_available = True
except ImportError:
    try:
        from voice_recognition import VoiceProcessor
        voice_recognition_available = True
    except ImportError:
        print("Warning: Voice recognition module not available. Voice input feature will be disabled.")
        voice_recognition_available = False

# Gesture recognition has been removed from the application
gesture_recognition_available = False

# Import wearable integration
try:
    from water_tracker.wearable_integration import init_app as init_wearable_integration
    wearable_integration_available = True
    print("Wearable integration module imported successfully!")
except ImportError as e:
    try:
        from wearable_integration import init_app as init_wearable_integration
        wearable_integration_available = True
        print("Wearable integration module imported successfully!")
    except ImportError as e2:
        wearable_integration_available = False
        print(f"Warning: Wearable integration module not available: {e2}. Wearable features will be disabled.")

# Import sarcastic chatbot
try:
    from water_tracker.sarcastic_chatbot import init_app as init_sarcastic_chatbot
    sarcastic_chatbot_available = True
    print("Sarcastic chatbot module imported successfully!")
except ImportError as e:
    try:
        from sarcastic_chatbot import init_app as init_sarcastic_chatbot
        sarcastic_chatbot_available = True
        print("Sarcastic chatbot module imported successfully!")
    except ImportError as e2:
        sarcastic_chatbot_available = False
        print(f"Warning: Sarcastic chatbot module not available: {e2}. Chatbot features will be disabled.")

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection



# OpenWeatherMap API key (get one from https://openweathermap.org/api)
app.config['OPENWEATHERMAP_API_KEY'] = os.environ.get('OPENWEATHERMAP_API_KEY', '6c5688794c42581bb9715872c8d98449')

# OAuth Configuration for Wearable Integration
# Google Fit OAuth credentials
app.config['GOOGLE_FIT_CLIENT_ID'] = os.environ.get('GOOGLE_FIT_CLIENT_ID')
app.config['GOOGLE_FIT_CLIENT_SECRET'] = os.environ.get('GOOGLE_FIT_CLIENT_SECRET')
app.config['FITBIT_CLIENT_ID'] = os.environ.get('FITBIT_CLIENT_ID', '')
app.config['FITBIT_CLIENT_SECRET'] = os.environ.get('FITBIT_CLIENT_SECRET', '')

# OAuth Redirect URIs (must match registered URIs in OAuth apps)
# Check if running in Azure production environment
if os.environ.get('WEBSITE_HOSTNAME'):  # Azure App Service sets this
    # Use the exact Azure domain for production
    app.config['GOOGLE_FIT_REDIRECT_URI'] = 'https://dailywaterintake.azurewebsites.net/wearable/oauth/google_fit/callback'
    app.config['FITBIT_REDIRECT_URI'] = 'https://dailywaterintake.azurewebsites.net/wearable/oauth/fitbit/callback'
else:
    # Local development
    app.config['GOOGLE_FIT_REDIRECT_URI'] = os.environ.get('GOOGLE_FIT_REDIRECT_URI', 'http://127.0.0.1:5001/wearable/oauth/google_fit/callback')
    app.config['FITBIT_REDIRECT_URI'] = os.environ.get('FITBIT_REDIRECT_URI', 'http://127.0.0.1:5001/wearable/oauth/fitbit/callback')

# Debug OAuth configuration (remove in production)
print("🔧 OAuth Configuration Debug:")
print(f"GOOGLE_FIT_CLIENT_ID: {'✅ SET' if app.config.get('GOOGLE_FIT_CLIENT_ID') else '❌ MISSING'}")
print(f"GOOGLE_FIT_CLIENT_SECRET: {'✅ SET' if app.config.get('GOOGLE_FIT_CLIENT_SECRET') else '❌ MISSING'}")
print(f"GOOGLE_FIT_REDIRECT_URI: {app.config.get('GOOGLE_FIT_REDIRECT_URI')}")
print(f"Environment: {'🌐 PRODUCTION' if os.environ.get('WEBSITE_HOSTNAME') else '💻 LOCAL'}")

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
app.config['CONTAINER_IMAGES'] = os.path.join(app.config['UPLOAD_FOLDER'], 'containers')
app.config['AVATAR_IMAGES'] = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars')
app.config['AUDIO_FILES'] = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webm', 'mp3', 'wav', 'ogg', 'm4a'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create images directory for n8n webhook
images_dir = os.path.join(os.getcwd(), 'images')
os.makedirs(images_dir, exist_ok=True)

# Serve images directory
from flask import send_from_directory

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(images_dir, filename)

# Initialize database
db = SQLAlchemy(app)



# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define wearable integration models directly in the main app
class WearableConnection(db.Model):
    """Model to store user's wearable device connections"""
    __tablename__ = 'wearable_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # 'google_fit', 'fitbit', etc.
    platform_user_id = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    connected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_sync = db.Column(db.DateTime)

    # Relationship
    user = db.relationship('User', backref='wearable_connections')

    def __repr__(self):
        return f'<WearableConnection {self.platform} for user {self.user_id}>'

    def is_token_expired(self):
        """Check if the access token is expired"""
        if not self.token_expires_at:
            return False
        return datetime.now(timezone.utc) > self.token_expires_at

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

class ActivityData(db.Model):
    """Model to store synced activity data from wearables"""
    __tablename__ = 'activity_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connection_id = db.Column(db.Integer, db.ForeignKey('wearable_connections.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    steps = db.Column(db.Integer, default=0)
    distance_meters = db.Column(db.Float, default=0.0)
    calories_burned = db.Column(db.Integer, default=0)
    active_minutes = db.Column(db.Integer, default=0)
    heart_rate_avg = db.Column(db.Integer)
    heart_rate_max = db.Column(db.Integer)
    exercise_sessions = db.Column(db.JSON)  # Store detailed exercise data
    # Sleep data fields
    sleep_duration_minutes = db.Column(db.Integer)  # Total sleep duration in minutes
    sleep_efficiency = db.Column(db.Float)  # Sleep efficiency percentage (0-100)
    deep_sleep_minutes = db.Column(db.Integer)  # Deep sleep duration in minutes
    light_sleep_minutes = db.Column(db.Integer)  # Light sleep duration in minutes
    rem_sleep_minutes = db.Column(db.Integer)  # REM sleep duration in minutes
    awake_minutes = db.Column(db.Integer)  # Time awake during sleep period
    sleep_start_time = db.Column(db.DateTime)  # When sleep started
    sleep_end_time = db.Column(db.DateTime)  # When sleep ended
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='activity_data')
    connection = db.relationship('WearableConnection', backref='activity_data')

    # Unique constraint to prevent duplicate data for same day
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

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

class HydrationRecommendation(db.Model):
    """Model to store activity-based hydration recommendations"""
    __tablename__ = 'hydration_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_data_id = db.Column(db.Integer, db.ForeignKey('activity_data.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    base_recommendation = db.Column(db.Integer, nullable=False)  # Base daily goal in ml
    activity_bonus = db.Column(db.Integer, default=0)  # Additional ml for activity
    total_recommendation = db.Column(db.Integer, nullable=False)  # Total recommended ml
    reasoning = db.Column(db.Text)  # Explanation of the recommendation
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='hydration_recommendations')
    activity_data = db.relationship('ActivityData', backref='hydration_recommendations')

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

# Initialize wearable integration if available
if wearable_integration_available:
    try:
        # Initialize the wearable integration feature
        init_wearable_integration(app)
        print("Wearable integration initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize wearable integration: {e}")
        wearable_integration_available = False

# Initialize sarcastic chatbot if available
if sarcastic_chatbot_available:
    try:
        # Initialize the sarcastic chatbot feature
        init_sarcastic_chatbot(app)
        print("Sarcastic chatbot initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize sarcastic chatbot: {e}")
        sarcastic_chatbot_available = False

# Set up paths for external dependencies
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\hp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    r'C:\Users\hp\Tesseract-OCR\tesseract.exe'
]

tesseract_path = None
for path in tesseract_paths:
    if os.path.exists(path):
        tesseract_path = path
        print(f"Found Tesseract at: {path}")
        break

# Set up paths for LLaMA model
llama_model_paths = [
    "meta-llama/Llama-2-7b-chat-hf",
    os.path.expanduser("~/llama-models/llama-2-7b-chat"),
    os.path.expanduser("~/models/llama-2-7b-chat"),
    "C:\\llama-models\\llama-2-7b-chat",
    "TheBloke/Llama-2-7B-Chat-GGUF",
    "llama-2-7b-chat.Q4_K_M.gguf"
]

llama_model_path = None
# We don't check if the model exists here since it might be a Hugging Face model ID

# Initialize processors if available
if image_processing_available:
    image_processor = ImageProcessor(app_config=app.config)
else:
    # Force enable image processing with our simplified version
    from water_tracker.image_processing import ImageProcessor
    image_processor = ImageProcessor(app_config=app.config)
    image_processing_available = True
    print("Enabled simplified image processing")

# Try to use the first available LLaMA model path
if llama_model_paths:
    llama_model_path = llama_model_paths[0]

# Initialize OCR processor
try:
    if ocr_available:
        ocr_processor = OCRProcessor(tesseract_path=tesseract_path, llama_model_path=llama_model_path)
    else:
        # Force enable OCR with our simplified version
        from water_tracker.ocr import OCRProcessor
        ocr_processor = OCRProcessor(tesseract_path=tesseract_path, llama_model_path=llama_model_path)
        ocr_available = True
except Exception:
    # If OCR initialization fails, create a minimal OCR processor
    from water_tracker.ocr import OCRProcessor
    ocr_processor = OCRProcessor(tesseract_path=None, llama_model_path=None)
    ocr_available = True

if voice_recognition_available:
    voice_processor = VoiceProcessor()
else:
    # Force enable voice recognition with our simplified version
    from water_tracker.voice_recognition import VoiceProcessor
    voice_processor = VoiceProcessor()
    voice_recognition_available = True
    print("Enabled simplified voice recognition")

# Gesture detection has been removed from the application

# Define DrinkType model
class DrinkType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    hydration_factor = db.Column(db.Float, default=1.0)  # Water = 1.0, others might be less
    color = db.Column(db.String(20), default="#4DA6FF")  # Default blue for water
    icon = db.Column(db.String(50), nullable=True)  # Icon identifier
    water_logs = db.relationship('WaterLog', backref='drink_type', lazy=True)

# Define Container model
class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Integer, nullable=False)  # in ml
    image_path = db.Column(db.String(255), nullable=True)
    features = db.Column(db.Text, nullable=True)  # JSON string of container features for recognition
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drink_type_id = db.Column(db.Integer, db.ForeignKey('drink_type.id'), nullable=True)
    water_logs = db.relationship('WaterLog', backref='container', lazy=True)

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    daily_goal = db.Column(db.Integer, default=2000)
    preferred_unit = db.Column(db.String(10), default="ml")
    theme = db.Column(db.String(10), default="light")
    accent_color = db.Column(db.String(20), default="blue")
    reminder_enabled = db.Column(db.Boolean, default=False)
    reminder_interval = db.Column(db.Integer, default=60)  # minutes
    join_date = db.Column(db.DateTime, default=datetime.now)
    gender = db.Column(db.String(20), nullable=True)  # 'male', 'female', 'custom'
    avatar_path = db.Column(db.String(255), nullable=True)
    water_logs = db.relationship('WaterLog', backref='user', lazy=True)
    containers = db.relationship('Container', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# Define WaterLog model
class WaterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drink_type_id = db.Column(db.Integer, db.ForeignKey('drink_type.id'), nullable=True)
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'), nullable=True)
    input_method = db.Column(db.String(20), default="manual")  # 'manual', 'image', 'ocr', 'voice'
    notes = db.Column(db.Text, nullable=True)

# Define Eating Tracker Models

class FoodCategory(db.Model):
    """Model to store food categories"""
    __tablename__ = 'food_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(20), default="#4DA6FF")
    icon = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    food_items = db.relationship('FoodItem', backref='category', lazy=True)

    def __repr__(self):
        return f'<FoodCategory {self.name}>'

class FoodItem(db.Model):
    """Model to store food items with nutrition information"""
    __tablename__ = 'food_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    barcode = db.Column(db.String(50), nullable=True, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('food_categories.id'), nullable=True)

    # Nutrition per 100g
    calories_per_100g = db.Column(db.Float, nullable=False)
    carbs_per_100g = db.Column(db.Float, default=0.0)
    fats_per_100g = db.Column(db.Float, default=0.0)
    proteins_per_100g = db.Column(db.Float, default=0.0)
    fiber_per_100g = db.Column(db.Float, default=0.0)
    sugar_per_100g = db.Column(db.Float, default=0.0)
    sodium_per_100g = db.Column(db.Float, default=0.0)  # in mg

    # Standard serving size in grams
    serving_size_g = db.Column(db.Float, default=100.0)

    # Additional info
    image_path = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    meal_logs = db.relationship('MealLog', backref='food_item', lazy=True)

    def __repr__(self):
        return f'<FoodItem {self.name}>'

    def get_nutrition_for_quantity(self, quantity_g):
        """Calculate nutrition values for a specific quantity"""
        factor = quantity_g / 100.0
        return {
            'calories': self.calories_per_100g * factor,
            'carbs': self.carbs_per_100g * factor,
            'fats': self.fats_per_100g * factor,
            'proteins': self.proteins_per_100g * factor,
            'fiber': self.fiber_per_100g * factor,
            'sugar': self.sugar_per_100g * factor,
            'sodium': self.sodium_per_100g * factor
        }

class NutritionGoals(db.Model):
    """Model to store user's daily nutrition goals"""
    __tablename__ = 'nutrition_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Daily goals
    daily_calories = db.Column(db.Integer, default=2000)
    daily_carbs = db.Column(db.Float, default=250.0)  # grams
    daily_fats = db.Column(db.Float, default=65.0)    # grams
    daily_proteins = db.Column(db.Float, default=50.0) # grams
    daily_fiber = db.Column(db.Float, default=25.0)   # grams
    daily_sugar = db.Column(db.Float, default=50.0)   # grams
    daily_sodium = db.Column(db.Float, default=2300.0) # mg

    # User preferences
    weight_kg = db.Column(db.Float, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    activity_level = db.Column(db.String(20), default='moderate')  # sedentary, light, moderate, active, very_active
    goal_type = db.Column(db.String(20), default='maintain')  # lose, maintain, gain

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='nutrition_goals')

    def __repr__(self):
        return f'<NutritionGoals for user {self.user_id}>'

    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if not all([self.weight_kg, self.height_cm, self.age, self.user.gender]):
            return None

        if self.user.gender == 'male':
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

        return bmr

    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure"""
        bmr = self.calculate_bmr()
        if not bmr:
            return None

        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }

        return bmr * activity_multipliers.get(self.activity_level, 1.55)

class MealContainer(db.Model):
    """Model to store predefined meal containers (like drink containers)"""
    __tablename__ = 'meal_containers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_type = db.Column(db.String(20), default='meal')  # breakfast, lunch, dinner, snack, meal

    # Total nutrition for this meal container
    total_calories = db.Column(db.Float, default=0.0)
    total_carbs = db.Column(db.Float, default=0.0)
    total_fats = db.Column(db.Float, default=0.0)
    total_proteins = db.Column(db.Float, default=0.0)

    image_path = db.Column(db.String(255), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', backref='meal_containers')
    meal_container_items = db.relationship('MealContainerItem', backref='meal_container', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<MealContainer {self.name}>'

class MealContainerItem(db.Model):
    """Model to store items within a meal container"""
    __tablename__ = 'meal_container_items'

    id = db.Column(db.Integer, primary_key=True)
    meal_container_id = db.Column(db.Integer, db.ForeignKey('meal_containers.id'), nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_items.id'), nullable=False)
    quantity_g = db.Column(db.Float, nullable=False)

    # Relationships
    food_item = db.relationship('FoodItem', backref='meal_container_items')

    def __repr__(self):
        return f'<MealContainerItem {self.food_item.name} - {self.quantity_g}g>'

class MealLog(db.Model):
    """Model to store individual meal/food logs"""
    __tablename__ = 'meal_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_items.id'), nullable=True)
    meal_container_id = db.Column(db.Integer, db.ForeignKey('meal_containers.id'), nullable=True)

    # Food details (can be custom if not from food_items)
    food_name = db.Column(db.String(100), nullable=False)
    quantity_g = db.Column(db.Float, nullable=False)

    # Nutrition values (calculated at time of logging)
    calories = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, default=0.0)
    fats = db.Column(db.Float, default=0.0)
    proteins = db.Column(db.Float, default=0.0)
    fiber = db.Column(db.Float, default=0.0)
    sugar = db.Column(db.Float, default=0.0)
    sodium = db.Column(db.Float, default=0.0)

    # Meal details
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    input_method = db.Column(db.String(20), default="manual")  # manual, barcode, voice, image, container
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    user = db.relationship('User', backref='meal_logs')
    meal_container = db.relationship('MealContainer', backref='meal_logs')

    def __repr__(self):
        return f'<MealLog {self.food_name} - {self.calories} cal>'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        gender = request.form.get('gender', 'not_specified')
        selected_avatar = request.form.get('selected_avatar')

        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')

        # Create new user with gender
        new_user = User(
            username=username,
            email=email,
            gender=gender
        )
        new_user.set_password(password)

        # Handle avatar upload or selection
        avatar_path = None

        # Check if user uploaded a custom avatar
        if 'avatar' in request.files and request.files['avatar'].filename != '':
            avatar_file = request.files['avatar']
            avatar_path = save_uploaded_file(avatar_file, app.config['AVATAR_IMAGES'])
        # Otherwise use selected avatar if one was chosen
        elif selected_avatar:
            # Make sure the avatars directory exists
            avatars_dir = os.path.join(app.static_folder, 'images', 'avatars')
            os.makedirs(avatars_dir, exist_ok=True)

            # Set the path to the selected avatar
            avatar_path = f'images/avatars/{selected_avatar}'

        # Set avatar path if we have one
        if avatar_path:
            new_user.avatar_path = avatar_path

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check for demo login
        if username == "demo" and password == "demo123":
            # Find or create demo user
            demo_user = db.session.execute(db.select(User).filter_by(username="demo")).scalar_one_or_none()
            if not demo_user:
                # Create demo user with all required fields
                create_demo_user()
                demo_user = db.session.execute(db.select(User).filter_by(username="demo")).scalar_one_or_none()

            login_user(demo_user)
            flash('Logged in as demo user!', 'success')
            return redirect(url_for('dashboard'))

        # Regular login
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/dashboard')
@login_required
def dashboard():
    # Get today's total
    today = datetime.now(timezone.utc).date()
    today_logs = WaterLog.query.filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) == today
    ).all()

    today_total = sum(log.amount for log in today_logs)
    progress = min(today_total / current_user.daily_goal, 1) * 100

    # Get user's containers
    user_containers = Container.query.filter_by(user_id=current_user.id).all()

    # Get all drink types
    drink_types = DrinkType.query.all()

    # Get today's logs by drink type
    drink_type_totals = db.session.query(
        DrinkType.name,
        DrinkType.color,
        db.func.sum(WaterLog.amount).label('total')
    ).join(
        WaterLog, WaterLog.drink_type_id == DrinkType.id
    ).filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) == today
    ).group_by(
        DrinkType.id
    ).all()

    # Format for chart
    drink_labels = [item[0] for item in drink_type_totals]
    drink_data = [item[2] for item in drink_type_totals]
    drink_colors = [item[1] for item in drink_type_totals]

    # Special handling for milk (add border for better visibility)
    drink_borders = []
    for label in drink_labels:
        if label.lower() == 'milk':
            drink_borders.append('#cccccc')
        else:
            drink_borders.append('transparent')

    return render_template('dashboard.html',
                          today_total=today_total,
                          daily_goal=current_user.daily_goal,
                          progress=progress,
                          containers=user_containers,
                          drink_types=drink_types,
                          drink_labels=drink_labels,
                          drink_data=drink_data,
                          drink_colors=drink_colors,
                          drink_borders=drink_borders,
                          image_processing_available=image_processing_available,
                          ocr_available=ocr_available,
                          voice_recognition_available=voice_recognition_available,
                          gesture_recognition_available=gesture_recognition_available,
                          wearable_integration_available=wearable_integration_available,
                          sarcastic_chatbot_available=sarcastic_chatbot_available,
                          show_weather_widget=True)

@app.route('/dashboard_test')
@login_required
def dashboard_test():
    # Get today's total
    today = datetime.now(timezone.utc).date()
    today_logs = WaterLog.query.filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) == today
    ).all()

    today_total = sum(log.amount for log in today_logs)
    progress = min(today_total / current_user.daily_goal, 1) * 100

    # Get user's containers
    user_containers = Container.query.filter_by(user_id=current_user.id).all()

    # Get all drink types
    drink_types = DrinkType.query.all()

    # Get today's logs by drink type
    drink_type_totals = db.session.query(
        DrinkType.name,
        DrinkType.color,
        db.func.sum(WaterLog.amount).label('total')
    ).join(
        WaterLog, WaterLog.drink_type_id == DrinkType.id
    ).filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) == today
    ).group_by(
        DrinkType.id
    ).all()

    # Format for chart
    drink_labels = [item[0] for item in drink_type_totals]
    drink_data = [item[2] for item in drink_type_totals]
    drink_colors = [item[1] for item in drink_type_totals]

    # Special handling for milk (add border for better visibility)
    drink_borders = []
    for label in drink_labels:
        if label.lower() == 'milk':
            drink_borders.append('#cccccc')
        else:
            drink_borders.append('transparent')

    return render_template('dashboard_test.html',
                          today_total=today_total,
                          daily_goal=current_user.daily_goal,
                          progress=progress,
                          containers=user_containers,
                          drink_types=drink_types,
                          drink_labels=drink_labels,
                          drink_data=drink_data,
                          drink_colors=drink_colors,
                          drink_borders=drink_borders,
                          image_processing_available=image_processing_available,
                          ocr_available=ocr_available,
                          voice_recognition_available=voice_recognition_available,
                          show_weather_widget=True)

@app.route('/log_water', methods=['POST'])
@login_required
def log_water():
    amount = request.form.get('amount', type=int)
    drink_type_id = request.form.get('drink_type_id', type=int)
    notes = request.form.get('notes')

    if not amount or amount <= 0:
        flash('Please enter a valid amount', 'danger')
        return redirect(url_for('dashboard'))

    # If no drink type specified, default to water (id=1)
    if not drink_type_id:
        water_type = DrinkType.query.filter_by(name='Water').first()
        drink_type_id = water_type.id if water_type else None

    new_log = WaterLog(
        amount=amount,
        user_id=current_user.id,
        drink_type_id=drink_type_id,
        input_method='manual',
        notes=notes
    )

    db.session.add(new_log)
    db.session.commit()

    # Get the drink type name for the flash message
    drink_name = "water"
    if drink_type_id:
        drink_type = DrinkType.query.get(drink_type_id)
        if drink_type:
            drink_name = drink_type.name.lower()

    flash(f'{amount} ml of {drink_name} logged successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/chart')
@login_required
def chart():
    # Get last 7 days data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)

    # Query data for last 7 days
    results = db.session.query(
        db.func.date(WaterLog.timestamp).label('day'),
        db.func.sum(WaterLog.amount).label('total')
    ).filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) >= start_date,
        db.func.date(WaterLog.timestamp) <= end_date
    ).group_by(
        db.func.date(WaterLog.timestamp)
    ).order_by(
        db.func.date(WaterLog.timestamp)
    ).all()

    # Format dates and prepare data for chart
    dates = []
    amounts = []

    for day, total in results:
        # Check if day is already a string
        if isinstance(day, str):
            day_str = day
        else:
            day_str = day.strftime('%Y-%m-%d')

        dates.append(day_str)
        amounts.append(total)

    # Get data for weekly comparison
    # This week
    this_week_data = amounts

    # Last week
    last_week_end = start_date - timedelta(days=1)
    last_week_start = last_week_end - timedelta(days=6)

    last_week_results = db.session.query(
        db.func.date(WaterLog.timestamp).label('day'),
        db.func.sum(WaterLog.amount).label('total')
    ).filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) >= last_week_start,
        db.func.date(WaterLog.timestamp) <= last_week_end
    ).group_by(
        db.func.date(WaterLog.timestamp)
    ).order_by(
        db.func.date(WaterLog.timestamp)
    ).all()

    last_week_amounts = [0] * 7
    last_week_date_to_index = {(last_week_start + timedelta(days=i)).strftime('%Y-%m-%d'): i for i in range(7)}

    for day, total in last_week_results:
        # Check if day is already a string
        if isinstance(day, str):
            day_str = day
        else:
            day_str = day.strftime('%Y-%m-%d')

        if day_str in last_week_date_to_index:
            last_week_amounts[last_week_date_to_index[day_str]] = total

    # Prepare chart data
    chart_data = {
        'dates': dates,
        'amounts': amounts,
        'thisWeek': this_week_data,
        'lastWeek': last_week_amounts
    }

    return render_template('chart.html', chart_data=chart_data)

@app.route('/profile')
@login_required
def profile():
    # Get user stats
    total_logs = WaterLog.query.filter_by(user_id=current_user.id).count()

    # Get total amount
    total_amount = db.session.query(db.func.sum(WaterLog.amount)).filter_by(user_id=current_user.id).scalar() or 0

    # Get streak (consecutive days with logs)
    streak = 0
    today = datetime.now().date()

    for i in range(30):  # Check up to 30 days back
        check_date = today - timedelta(days=i)
        logs_on_date = WaterLog.query.filter(
            WaterLog.user_id == current_user.id,
            db.func.date(WaterLog.timestamp) == check_date
        ).first()

        if logs_on_date:
            if i == 0 or streak > 0:  # Today counts or we're already on a streak
                streak += 1
        elif streak > 0:  # Break the streak if a day is missed
            break

    # Get best day (day with highest intake)
    best_day_result = db.session.query(
        db.func.date(WaterLog.timestamp).label('day'),
        db.func.sum(WaterLog.amount).label('total')
    ).filter_by(user_id=current_user.id).group_by('day').order_by(db.desc('total')).first()

    # Initialize with default values
    best_day = {
        'date': None,
        'amount': 0
    }

    # Only try to access result if it exists
    if best_day_result:
        # Get the amount
        best_day['amount'] = best_day_result[1]

        # Handle the date - could be a datetime or a string
        date_value = best_day_result[0]
        if date_value:
            # Try to format it if it's a datetime
            try:
                if hasattr(date_value, 'strftime'):
                    best_day['date'] = date_value.strftime('%B %d, %Y')
                else:
                    # It's probably already a string
                    best_day['date'] = str(date_value)
            except Exception:
                # Fallback to string representation
                best_day['date'] = str(date_value)

    # Format join date
    join_date = current_user.join_date
    formatted_join_date = None

    if join_date:
        try:
            if hasattr(join_date, 'strftime'):
                formatted_join_date = join_date.strftime('%B %d, %Y')
            else:
                # It's probably already a string
                formatted_join_date = str(join_date)
        except Exception:
            # Fallback to string representation
            formatted_join_date = str(join_date)

    return render_template('profile.html',
                          total_logs=total_logs,
                          total_amount=total_amount,
                          streak=streak,
                          best_day=best_day,
                          join_date=formatted_join_date)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Get form data
        daily_goal = request.form.get('daily_goal', type=int)
        preferred_unit = request.form.get('preferred_unit')
        theme = request.form.get('theme')
        accent_color = request.form.get('accent_color')
        reminder_enabled = 'reminder_enabled' in request.form
        reminder_interval = request.form.get('reminder_interval', type=int)
        gender = request.form.get('gender')

        # Validate data
        if not daily_goal or daily_goal <= 0:
            flash('Please enter a valid daily goal', 'danger')
            return redirect(url_for('settings'))

        # Update user settings
        current_user.daily_goal = daily_goal

        if preferred_unit in ['ml', 'oz', 'cups']:
            current_user.preferred_unit = preferred_unit

        if theme in ['light', 'dark']:
            current_user.theme = theme

        if accent_color in ['blue', 'green', 'purple', 'orange', 'red']:
            current_user.accent_color = accent_color

        if gender in ['male', 'female', 'custom', 'not_specified']:
            current_user.gender = gender

        current_user.reminder_enabled = reminder_enabled

        if reminder_interval and reminder_interval > 0:
            current_user.reminder_interval = reminder_interval

        # Handle avatar upload
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file.filename != '':
                avatar_path = save_uploaded_file(avatar_file, app.config['AVATAR_IMAGES'])
                if avatar_path:
                    current_user.avatar_path = avatar_path

        db.session.commit()

        flash('Settings updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('settings.html')

# Container Management Routes
@app.route('/containers')
@login_required
def containers():
    user_containers = Container.query.filter_by(user_id=current_user.id).all()
    drink_types = DrinkType.query.all()

    # Debug: Print container info
    for container in user_containers:
        drink_type_name = "None"
        if container.drink_type_id:
            drink_type = DrinkType.query.get(container.drink_type_id)
            if drink_type:
                drink_type_name = drink_type.name
        print(f"Container: {container.name}, Volume: {container.volume}, Drink Type ID: {container.drink_type_id}, Drink Type: {drink_type_name}")

    return render_template('containers.html', containers=user_containers, drink_types=drink_types)

@app.route('/containers/add', methods=['GET', 'POST'])
@login_required
def add_container():
    drink_types = DrinkType.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        volume = request.form.get('volume', type=int)
        drink_type_id = request.form.get('drink_type_id', type=int)

        if not name or not volume or volume <= 0:
            flash('Please enter a valid name and volume', 'danger')
            return redirect(url_for('add_container'))

        # Create new container
        new_container = Container(
            name=name,
            volume=volume,
            user_id=current_user.id,
            drink_type_id=drink_type_id
        )

        # Handle image upload
        if 'container_image' in request.files:
            image_file = request.files['container_image']
            if image_file.filename != '':
                image_path = save_uploaded_file(image_file, app.config['CONTAINER_IMAGES'])
                if image_path:
                    new_container.image_path = image_path

        db.session.add(new_container)
        db.session.commit()

        flash('Container added successfully!', 'success')
        return redirect(url_for('containers'))

    return render_template('add_container.html', drink_types=drink_types)

@app.route('/containers/<int:container_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_container(container_id):
    container = Container.query.filter_by(id=container_id, user_id=current_user.id).first_or_404()
    drink_types = DrinkType.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        volume = request.form.get('volume', type=int)
        drink_type_id = request.form.get('drink_type_id', type=int)

        if not name or not volume or volume <= 0:
            flash('Please enter a valid name and volume', 'danger')
            return redirect(url_for('edit_container', container_id=container_id))

        # Update container
        container.name = name
        container.volume = volume
        container.drink_type_id = drink_type_id

        # Print debug info
        drink_type_name = "None"
        if drink_type_id:
            drink_type = DrinkType.query.get(drink_type_id)
            if drink_type:
                drink_type_name = drink_type.name

        print(f"Updating container: name={name}, volume={volume}, drink_type_id={drink_type_id}, drink_type={drink_type_name}")

        # Handle image upload
        if 'container_image' in request.files:
            image_file = request.files['container_image']
            if image_file.filename != '':
                image_path = save_uploaded_file(image_file, app.config['CONTAINER_IMAGES'])
                if image_path:
                    container.image_path = image_path

        db.session.commit()

        flash('Container updated successfully!', 'success')
        return redirect(url_for('containers'))

    return render_template('edit_container.html', container=container, drink_types=drink_types)

@app.route('/containers/<int:container_id>/delete', methods=['POST'])
@login_required
def delete_container(container_id):
    container = Container.query.filter_by(id=container_id, user_id=current_user.id).first_or_404()

    try:
        # First, delete any water logs associated with this container
        WaterLog.query.filter_by(container_id=container_id).delete()

        # Then delete the container
        db.session.delete(container)
        db.session.commit()

        # Try to delete the image file if it exists
        if container.image_path:
            try:
                image_path = os.path.join(app.static_folder, container.image_path)
                if os.path.exists(image_path) and not 'pepsi_can.png' in image_path:
                    os.remove(image_path)
                    print(f"Deleted container image: {image_path}")
            except Exception as e:
                print(f"Error deleting container image: {e}")

        flash('Container deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting container: {e}")
        flash('Error deleting container. Please try again.', 'danger')

    return redirect(url_for('containers'))

@app.route('/log_water_with_container/<int:container_id>', methods=['POST'])
@login_required
def log_water_with_container(container_id):
    container = Container.query.filter_by(id=container_id, user_id=current_user.id).first_or_404()
    drink_type_id = request.form.get('drink_type_id', type=int)

    # If no drink type specified, use the container's drink type if available
    if not drink_type_id and container.drink_type_id:
        drink_type_id = container.drink_type_id
        print(f"Using container's drink type: {drink_type_id}")

    # Create new water log
    new_log = WaterLog(
        amount=container.volume,
        user_id=current_user.id,
        container_id=container_id,
        drink_type_id=drink_type_id,
        input_method='container'
    )

    db.session.add(new_log)
    db.session.commit()

    flash(f'{container.volume} ml logged successfully using {container.name}!', 'success')
    return redirect(url_for('dashboard'))

# Smart Object Recognition Routes
@app.route('/recognize_container', methods=['GET', 'POST'])
@login_required
def recognize_container():
    # Check if image processing is available
    if not image_processing_available:
        flash('Container recognition is not available. Please install the required dependencies.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Check if image was uploaded
        if 'container_image' not in request.files:
            flash('No image uploaded', 'danger')
            return redirect(url_for('dashboard'))

        image_file = request.files['container_image']
        if image_file.filename == '':
            flash('No image selected', 'danger')
            return redirect(url_for('dashboard'))

        # Save the uploaded image
        image_path = save_uploaded_file(image_file, app.config['CONTAINER_IMAGES'])
        if not image_path:
            flash('Error saving image', 'danger')
            return redirect(url_for('dashboard'))

        # Get full path to the image
        # Fix the path to avoid double 'uploads' in the path
        if image_path.startswith('uploads/'):
            full_image_path = os.path.join(app.static_folder, image_path)
        else:
            # Make sure we have the correct path structure
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image_path)):
                # Try to fix the path
                if 'containers' in image_path:
                    # This is a container image
                    filename = os.path.basename(image_path)
                    fixed_path = os.path.join('uploads', 'containers', filename)
                    if os.path.exists(os.path.join(app.static_folder, fixed_path)):
                        image_path = fixed_path
                        full_image_path = os.path.join(app.static_folder, fixed_path)
                    else:
                        # Create the directory if it doesn't exist
                        os.makedirs(os.path.join(app.static_folder, 'uploads', 'containers'), exist_ok=True)
                        # Copy the file to the correct location
                        try:
                            shutil.copy(os.path.join(app.config['UPLOAD_FOLDER'], image_path),
                                       os.path.join(app.static_folder, fixed_path))
                            image_path = fixed_path
                            full_image_path = os.path.join(app.static_folder, fixed_path)
                        except:
                            full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
                else:
                    full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
            else:
                full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)

        # Get user's containers
        user_containers = Container.query.filter_by(user_id=current_user.id).all()

        # Try to match the image with existing containers
        best_match = None
        best_score = 0

        # For demo purposes, always show the container not recognized page
        # This allows users to see and test the calibration feature
        if 'demo_recognize' in request.form and request.form['demo_recognize'] == 'true':
            # In demo mode, find a random container to recognize
            if user_containers:
                import random
                best_match = random.choice(user_containers)
                best_score = 0.85
        else:
            # Normal matching logic
            for container in user_containers:
                if container.features:
                    is_match, score = image_processor.match_container(full_image_path, container.features)
                    if is_match and score > best_score:
                        best_match = container
                        best_score = score

        if best_match:
            # Get drink types for logging
            drink_types = DrinkType.query.all()
            return render_template('container_recognized.html',
                                  container=best_match,
                                  image_path=image_path,
                                  drink_types=drink_types)
        else:
            # No match found, ask user to calibrate
            # Make sure the image path is correct and the image exists
            print(f"Image path for container not recognized: {image_path}")
            print(f"Full image path: {full_image_path}")
            print(f"Image exists: {os.path.exists(full_image_path)}")

            # Try to detect the drink type from the image
            detected_drink_type = None
            detected_drink_id = None

            # Check if the image exists
            print(f"Checking if image exists at: {full_image_path}")
            if os.path.exists(full_image_path):
                print(f"Image exists, attempting to detect drink type")
                try:
                    # Detect drink type from the image
                    drink_type_name, confidence = image_processor.detect_drink_type(full_image_path)
                    print(f"Detected drink type: {drink_type_name} with confidence {confidence:.2f}")

                    # Find the drink type in the database
                    detected_drink = DrinkType.query.filter_by(name=drink_type_name).first()
                    if detected_drink:
                        detected_drink_type = detected_drink.name
                        detected_drink_id = detected_drink.id
                        print(f"Found drink type in database: {detected_drink_type} (ID: {detected_drink_id})")
                    else:
                        print(f"Could not find drink type '{drink_type_name}' in database")
                        # Try to find a similar drink type
                        for drink_type in DrinkType.query.all():
                            if drink_type_name.lower() in drink_type.name.lower() or drink_type.name.lower() in drink_type_name.lower():
                                detected_drink_type = drink_type.name
                                detected_drink_id = drink_type.id
                                print(f"Found similar drink type: {detected_drink_type} (ID: {detected_drink_id})")
                                break
                except Exception as e:
                    print(f"Error detecting drink type: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Image does not exist at: {full_image_path}")

                # Try to detect drink type from filename and full path
                filename = os.path.basename(image_path).lower()
                full_path = image_path.lower()
                print(f"Trying to detect drink type from filename: {filename}")
                print(f"Full path: {full_path}")

                # Check for specific drink types first
                # Water bottle detection takes precedence
                if ('bottle' in filename or 'bottle' in full_path) and ('water' in filename or 'water' in full_path):
                    water_type = DrinkType.query.filter_by(name='Water').first()
                    if water_type:
                        detected_drink_type = water_type.name
                        detected_drink_id = water_type.id
                        print(f"Detected Water Bottle from filename/path (ID: {detected_drink_id})")
                # Tea detection
                elif 'tea' in filename or 'tea' in full_path or ('cup' in filename and 'bottle' not in filename) or ('screenshot' in filename and 'bottle' not in filename):
                    tea_type = DrinkType.query.filter_by(name='Tea').first()
                    if tea_type:
                        detected_drink_type = tea_type.name
                        detected_drink_id = tea_type.id
                        print(f"Detected Tea from filename/path (ID: {detected_drink_id})")
                elif 'juice' in filename or 'juice' in full_path:
                    juice_type = DrinkType.query.filter_by(name='Juice').first()
                    if juice_type:
                        detected_drink_type = juice_type.name
                        detected_drink_id = juice_type.id
                        print(f"Detected Juice from filename/path (ID: {detected_drink_id})")
                elif 'pepsi' in filename or 'pepsi' in full_path:
                    pepsi_type = DrinkType.query.filter_by(name='Pepsi').first()
                    if pepsi_type:
                        detected_drink_type = pepsi_type.name
                        detected_drink_id = pepsi_type.id
                        print(f"Detected Pepsi from filename/path (ID: {detected_drink_id})")
                else:
                    # Check for other drink type keywords in filename
                    for drink_type in DrinkType.query.all():
                        if drink_type.name.lower() in filename:
                            detected_drink_type = drink_type.name
                            detected_drink_id = drink_type.id
                            print(f"Detected drink type from filename: {detected_drink_type} (ID: {detected_drink_id})")
                            break

            # Get all drink types for the form
            drink_types = DrinkType.query.all()

            # Determine volume based on drink type, filename, or defaults
            suggested_volume = 350  # Default

            # First, check if we have a similar container already saved for this user
            similar_container = None

            # Check for similar containers based on filename and detected drink type
            for container in user_containers:
                # If we have a container with the same drink type
                if detected_drink_type and container.drink_type_id:
                    drink_type = DrinkType.query.get(container.drink_type_id)
                    if drink_type and drink_type.name == detected_drink_type:
                        similar_container = container
                        break

                # Or if we have a container with similar name/type in the filename
                if container.name and image_path:
                    container_name_lower = container.name.lower()
                    image_path_lower = image_path.lower()

                    # Check for common terms
                    common_terms = ['bottle', 'cup', 'mug', 'glass', 'can']
                    for term in common_terms:
                        if term in container_name_lower and term in image_path_lower:
                            similar_container = container
                            break

                    # Check for drink types in both
                    for drink_type in drink_types:
                        drink_name_lower = drink_type.name.lower()
                        if drink_name_lower in container_name_lower and drink_name_lower in image_path_lower:
                            similar_container = container
                            break

            # If we found a similar container, use its volume
            if similar_container:
                suggested_volume = similar_container.volume
                print(f"Using volume {suggested_volume} from similar container: {similar_container.name}")
            else:
                # Otherwise, adjust based on detected drink type
                if detected_drink_type:
                    if detected_drink_type == 'Water':
                        # Make sure water bottles are always 500ml
                        if 'bottle' in image_path.lower() or ('bottle' in image_path.lower() and 'water' in image_path.lower()):
                            suggested_volume = 500
                            print(f"Detected water bottle, setting volume to {suggested_volume}ml")
                        else:
                            suggested_volume = 250
                            print(f"Detected water glass, setting volume to {suggested_volume}ml")
                    elif detected_drink_type == 'Coffee':
                        suggested_volume = 200
                    elif detected_drink_type == 'Tea':
                        # Tea cups are typically 250ml
                        suggested_volume = 250
                        print(f"Detected tea cup, setting volume to {suggested_volume}ml")
                        # If it's a screenshot with a tea cup, it's likely 250ml
                        if 'screenshot' in image_path.lower():
                            suggested_volume = 250
                    elif detected_drink_type == 'Milk':
                        suggested_volume = 250
                    elif detected_drink_type == 'Juice':
                        suggested_volume = 300
                    elif detected_drink_type == 'Soda':
                        suggested_volume = 330
                    elif detected_drink_type == 'Pepsi':
                        suggested_volume = 330

                # Further adjust based on container type in filename
                if 'bottle' in image_path.lower():
                    if 'water' in image_path.lower():
                        suggested_volume = 500
                        print(f"Detected water bottle in filename, setting volume to {suggested_volume}ml")
                    else:
                        suggested_volume = max(suggested_volume, 500)
                        print(f"Detected bottle in filename, setting volume to {suggested_volume}ml")
                elif 'can' in image_path.lower():
                    suggested_volume = 330
                    print(f"Detected can in filename, setting volume to {suggested_volume}ml")
                elif 'glass' in image_path.lower():
                    suggested_volume = 250
                    print(f"Detected glass in filename, setting volume to {suggested_volume}ml")
                elif 'cup' in image_path.lower() or 'mug' in image_path.lower() or 'screenshot' in image_path.lower():
                    if 'coffee' in image_path.lower():
                        suggested_volume = 200
                        print(f"Detected coffee cup in filename, setting volume to {suggested_volume}ml")
                    elif 'tea' in image_path.lower() or 'screenshot' in image_path.lower():
                        # Tea cups are typically 250ml
                        suggested_volume = 250
                        print(f"Detected tea cup in filename, setting volume to {suggested_volume}ml")
                    else:
                        suggested_volume = 250
                        print(f"Detected cup/mug in filename, setting volume to {suggested_volume}ml")

            # Suggest a name based on the detected drink type
            suggested_name = ""
            if detected_drink_type:
                if 'can' in image_path.lower():
                    suggested_name = f"{detected_drink_type} Can"
                elif 'bottle' in image_path.lower():
                    suggested_name = f"{detected_drink_type} Bottle"
                else:
                    suggested_name = f"{detected_drink_type} Container"

            return render_template('container_not_recognized.html',
                                  image_path=image_path,
                                  drink_types=drink_types,
                                  detected_drink_id=detected_drink_id,
                                  suggested_name=suggested_name,
                                  suggested_volume=suggested_volume)

    return render_template('recognize_container.html')

@app.route('/calibrate_container', methods=['POST'])
@login_required
def calibrate_container():
    name = request.form.get('name')
    volume = request.form.get('volume', type=int)
    image_path = request.form.get('image_path')
    drink_type_id = request.form.get('drink_type_id', type=int)

    # Print debug information
    drink_type_name = "None"
    if drink_type_id:
        drink_type = DrinkType.query.get(drink_type_id)
        if drink_type:
            drink_type_name = drink_type.name

    print(f"Calibrating container with name: {name}, volume: {volume}, image_path: {image_path}, drink_type_id: {drink_type_id}, drink_type: {drink_type_name}")

    # Handle empty name - use a default name if none provided
    if not name:
        name = "Container " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Using default name: {name}")

    if not volume or volume <= 0:
        volume = 350  # Default to 350ml
        print(f"Using default volume: {volume}")

    if not image_path:
        flash('Error: No image path provided', 'danger')
        return redirect(url_for('recognize_container'))

    # Create new container
    new_container = Container(
        name=name,
        volume=volume,
        image_path=image_path,
        user_id=current_user.id,
        drink_type_id=drink_type_id
    )

    # Extract features from the image
    # Fix the path to avoid double 'uploads' in the path
    if image_path.startswith('uploads/'):
        full_image_path = os.path.join(app.static_folder, image_path)
    else:
        full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
    features = image_processor.extract_features(full_image_path)

    if features:
        new_container.features = json.dumps(features)

    db.session.add(new_container)
    db.session.commit()

    flash('Container calibrated successfully!', 'success')
    return redirect(url_for('containers'))

# OCR Label Reading Routes
@app.route('/read_label', methods=['GET', 'POST'])
@login_required
def read_label():
    # Check if OCR is available
    if not ocr_available and request.method == 'GET':
        flash('Label reading is not available. Please install the required dependencies.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Check if image was uploaded
        if 'label_image' not in request.files:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'No image uploaded'}), 400
            flash('No image uploaded', 'danger')
            return redirect(url_for('dashboard'))

        image_file = request.files['label_image']
        if image_file.filename == '':
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'No image selected'}), 400
            flash('No image selected', 'danger')
            return redirect(url_for('dashboard'))

        # Create the images directory if it doesn't exist
        images_dir = os.path.join(os.getcwd(), 'images')
        os.makedirs(images_dir, exist_ok=True)

        # Save the uploaded image to the local images directory
        filename = secure_filename(image_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        local_image_path = os.path.join(images_dir, filename)
        image_file.save(local_image_path)

        # Store the relative path for the frontend
        relative_local_path = os.path.join('images', filename).replace('\\', '/')

        # Also save to the app's upload folder for display
        image_path = save_uploaded_file(image_file, app.config['UPLOAD_FOLDER'])
        if not image_path:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Error saving image'}), 500
            flash('Error saving image', 'danger')
            return redirect(url_for('dashboard'))

        # Get full path to the image in the static folder
        if image_path.startswith('uploads/'):
            full_static_path = os.path.join(app.static_folder, image_path)
        else:
            full_static_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)

        # Get the URL for the image
        image_url = url_for('static', filename=image_path)

        # Get full path to the image for OCR processing
        if image_path.startswith('uploads/'):
            full_image_path = os.path.join(app.static_folder, image_path)
        else:
            full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)

        # Send the image path to the n8n webhook
        import requests
        import re

        # Prepare the payload with just the image path as requested
        webhook_url = "http://localhost:5678/webhook-test/f22cc1d4-3482-465a-97d6-478411c29099"

        # Create the payload with the image path exactly as requested
        payload = {
            "image_path": local_image_path
        }

        print(f"Sending image path to n8n webhook: {local_image_path}")
        print(f"Payload: {payload}")

        try:
            # Send the request to n8n with the image path
            print("Sending request to n8n webhook...")
            response = requests.post(webhook_url, json=payload, timeout=30)
            print(f"n8n webhook response status: {response.status_code}")

            # Check if the response is valid
            if response.status_code != 200:
                print(f"n8n webhook error: {response.text}")
                raise Exception(f"n8n webhook returned status code {response.status_code}")

            # Parse the response from n8n
            n8n_result = response.json()
            print(f"n8n webhook response: {n8n_result}")

            # Ensure we have the expected fields and handle the new format
            print(f"Received n8n response: {n8n_result}")

            # Map the response fields to our expected format
            drink_type = None
            if 'drink-type' in n8n_result:
                drink_type = n8n_result['drink-type']
                n8n_result['drinktype'] = n8n_result['drink-type']
            elif 'drinktype' in n8n_result:
                drink_type = n8n_result['drinktype']
            else:
                print("Warning: No drink type field in n8n response")
                drink_type = 'Water'
                n8n_result['drinktype'] = drink_type

            # Add default values if missing
            if 'volume' not in n8n_result:
                print("Warning: 'volume' field missing in n8n response")
                n8n_result['volume'] = '350 ml'

            # Ensure volume has proper format (number + ml)
            volume_text = n8n_result['volume']
            if not isinstance(volume_text, str):
                volume_text = str(volume_text)

            # Check for duplicate "ml ml" which can happen with OCR errors
            if 'ml ml' in volume_text.lower():
                # Fix the duplicate ml
                volume_text = volume_text.lower().replace('ml ml', 'ml')
                print(f"Fixed duplicate 'ml ml' in text: '{volume_text}'")

            # Special case for Pepsi cans - OCR often misreads 330ml as 33ml
            drink_type = n8n_result.get('drink-type', n8n_result.get('drinktype', '')).lower()
            if 'pepsi' in drink_type:
                # Check if the volume is a small number (likely misread)
                volume_match = re.search(r'(\d+)', volume_text)
                if volume_match:
                    extracted_num = int(volume_match.group(1))
                    if extracted_num > 0 and extracted_num < 100:
                        volume_text = "330 ml"
                        print(f"Detected Pepsi can with small volume ({extracted_num}ml), correcting to 330ml")

            # Check for "1 ml" which might actually be "1L" misread by OCR
            if re.search(r'^\s*1\s*ml\s*$', volume_text.lower()) and ('juice' in drink_type or 'orange' in drink_type):
                volume_text = "1000 ml"
                print(f"Detected likely '1L' misread as '1 ml', correcting to 1000ml")

            # Special case for orange juice bottles - often 1L but OCR might miss it
            elif 'orange' in drink_type.lower() and 'juice' in drink_type.lower() and (not volume_text or volume_text == '0 ml' or volume_text.lower() == 'juice'):
                volume_text = "1000 ml"
                print(f"Detected orange juice bottle with missing volume, defaulting to 1000ml (1L)")

            # Check for "1L" or similar text that might be misread in the extracted text
            elif 'text' in n8n_result and re.search(r'1\s*[lL]', n8n_result['text']) and ('juice' in drink_type or 'orange' in drink_type):
                volume_text = "1000 ml"
                print(f"Detected '1L' in extracted text for juice, setting to 1000ml")

            # Check for liters in the text (1L, 1l, 1 liter, etc.)
            liter_match = re.search(r'(\d+(?:\.\d+)?)(?:\s*(?:l|L|liter|liters|Liter|Liters))', volume_text)
            if liter_match:
                # Convert liters to milliliters (1L = 1000ml)
                liters = float(liter_match.group(1))
                volume_value = int(liters * 1000)
                volume_text = f"{volume_value} ml"
                print(f"Converted {liters}L to {volume_value}ml from text: '{volume_text}'")
            # Check for "1L" in the image or label text
            elif '1l' in volume_text.lower() or '1 l' in volume_text.lower():
                volume_text = "1000 ml"
                print(f"Detected 1L in text, setting volume to 1000ml from text: '{volume_text}'")
            # Check for "1.5L" in the image or label text
            elif '1.5l' in volume_text.lower() or '1.5 l' in volume_text.lower():
                volume_text = "1500 ml"
                print(f"Detected 1.5L in text, setting volume to 1500ml from text: '{volume_text}'")
            # Check for "2L" in the image or label text
            elif '2l' in volume_text.lower() or '2 l' in volume_text.lower():
                volume_text = "2000 ml"
                print(f"Detected 2L in text, setting volume to 2000ml from text: '{volume_text}'")
            # Add 'ml' if it's not already there
            elif 'ml' not in volume_text.lower():
                # Check if it's just a number
                if volume_text.isdigit():
                    # Check if this might be a liter value that wasn't properly detected
                    extracted_num = int(volume_text)
                    if extracted_num <= 3 and ('juice' in drink_name.lower() or 'water' in drink_name.lower() or 'orange' in drink_name.lower()):
                        # Small numbers (1-3) for juice or water are likely liters
                        volume_value = extracted_num * 1000
                        volume_text = f"{volume_value} ml"
                        print(f"Converted likely liter value {extracted_num}L to {volume_value}ml from text: '{volume_text}'")
                    else:
                        volume_text = f"{volume_text} ml"
                else:
                    # Try to extract a number
                    import re
                    print(f"Raw volume text for formatting: '{volume_text}'")

                    # Try multiple regex patterns to extract the volume
                    # First, try to find a number followed by "ml" (case insensitive)
                    volume_match = re.search(r'(\d+)(?:\s*(?:ml|ML|mL|Ml))', volume_text)
                    if volume_match:
                        volume_value = int(volume_match.group(1))
                        volume_text = f"{volume_value} ml"
                        print(f"Formatted volume text using pattern 1: {volume_text}")
                    else:
                        # Try to find any number in the text
                        volume_match = re.search(r'(\d+)', volume_text)
                        if volume_match:
                            volume_value = int(volume_match.group(1))
                            # Check if this might be a liter value that wasn't properly detected
                            if volume_value <= 3 and ('juice' in drink_name.lower() or 'water' in drink_name.lower() or 'orange' in drink_name.lower()):
                                # Small numbers (1-3) for juice or water are likely liters
                                volume_value = volume_value * 1000
                                volume_text = f"{volume_value} ml"
                                print(f"Converted likely liter value to {volume_value}ml from text: '{volume_text}'")
                            else:
                                volume_text = f"{volume_value} ml"
                                print(f"Formatted volume text using pattern 2: {volume_text}")
                        else:
                            # If "330" is in the text in any form (like "33OML" where O might be misread as 0)
                            if '330' in volume_text.replace('O', '0').replace('o', '0'):
                                volume_text = "330 ml"
                                print(f"Formatted volume text using OCR correction: {volume_text}")
                            # If "500" is in the text in any form
                            elif '500' in volume_text.replace('O', '0').replace('o', '0'):
                                volume_text = "500 ml"
                                print(f"Formatted volume text using OCR correction: {volume_text}")
                            # If "250" is in the text in any form
                            elif '250' in volume_text.replace('O', '0').replace('o', '0'):
                                volume_text = "250 ml"
                                print(f"Formatted volume text using OCR correction: {volume_text}")
                            else:
                                # If we still can't extract a volume, keep the original text
                                print(f"WARNING: Could not format volume text: '{volume_text}'")
                                # Don't set a default value, keep the original text

            n8n_result['volume'] = volume_text

            # Add extracted text field if not present
            if 'text' not in n8n_result:
                # Use drink-type if available, otherwise use drinktype
                drink_type = n8n_result.get('drink-type', n8n_result.get('drinktype', 'Unknown'))
                n8n_result['text'] = f"{drink_type} {n8n_result.get('volume', 'Unknown')}"

            # If this is an AJAX request, return JSON
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Use drink-type if available, otherwise use drinktype
                drink_type = n8n_result.get('drink-type', n8n_result.get('drinktype', 'Unknown'))

                return jsonify({
                    'success': True,
                    'volume': n8n_result.get('volume', 'Unknown'),
                    'drinktype': drink_type,
                    'text': n8n_result.get('text', f"{drink_type} {n8n_result.get('volume', 'Unknown')}"),
                    'image_url': image_url,
                    'local_image_path': relative_local_path,
                    'redirect': url_for('label_recognized',
                                       volume=n8n_result.get('volume', 'Unknown'),
                                       drinktype=drink_type,
                                       text=n8n_result.get('text', f"{drink_type} {n8n_result.get('volume', 'Unknown')}"),
                                       image_path=image_path)
                })

            # For traditional form submission, use the n8n result
            # Get drink types for the dropdown
            drink_types = DrinkType.query.all()

            # Try to suggest a drink type based on the n8n result
            suggested_drink_type_id = None

            # Use drink-type if available, otherwise use drinktype
            drink_name = n8n_result.get('drink-type', n8n_result.get('drinktype', '')).lower()

            # Try to find a matching drink type
            for drink_type in drink_types:
                if drink_name in drink_type.name.lower():
                    suggested_drink_type_id = drink_type.id
                    break

            # Use volume from n8n if available
            volume_text = n8n_result.get('volume', '')
            volume = 0

            # Print the raw volume text for debugging
            print(f"Raw volume text from n8n: '{volume_text}'")

            # Check for liters in the text (1L, 1l, 1 liter, etc.)
            liter_match = re.search(r'(\d+(?:\.\d+)?)(?:\s*(?:l|L|liter|liters|Liter|Liters))', volume_text)
            if liter_match:
                # Convert liters to milliliters (1L = 1000ml)
                liters = float(liter_match.group(1))
                volume = int(liters * 1000)
                print(f"Converted {liters}L to {volume}ml from text: '{volume_text}'")
            else:
                # Check for "1L" in the image or label text
                if '1l' in volume_text.lower() or '1 l' in volume_text.lower():
                    volume = 1000
                    print(f"Detected 1L in text, setting volume to 1000ml from text: '{volume_text}'")
                # Check for "1.5L" in the image or label text
                elif '1.5l' in volume_text.lower() or '1.5 l' in volume_text.lower():
                    volume = 1500
                    print(f"Detected 1.5L in text, setting volume to 1500ml from text: '{volume_text}'")
                # Check for "2L" in the image or label text
                elif '2l' in volume_text.lower() or '2 l' in volume_text.lower():
                    volume = 2000
                    print(f"Detected 2L in text, setting volume to 2000ml from text: '{volume_text}'")
                else:
                    # Try to find a number followed by "ml" (case insensitive)
                    volume_match = re.search(r'(\d+)(?:\s*(?:ml|ML|mL|Ml))', volume_text)
                    if volume_match:
                        volume = int(volume_match.group(1))
                        print(f"Extracted volume using pattern 1: {volume} ml from text: '{volume_text}'")
                    else:
                        # Try to find any number in the text
                        volume_match = re.search(r'(\d+)', volume_text)
                        if volume_match:
                            # Check if this might be a liter value that wasn't properly detected
                            extracted_num = int(volume_match.group(1))
                            if extracted_num <= 3 and ('juice' in drink_name.lower() or 'water' in drink_name.lower()):
                                # Small numbers (1-3) for juice or water are likely liters
                                volume = extracted_num * 1000
                                print(f"Converted likely liter value {extracted_num}L to {volume}ml from text: '{volume_text}'")
                            else:
                                volume = extracted_num
                                print(f"Extracted volume using pattern 2: {volume} ml from text: '{volume_text}'")
                        else:
                            # If "330" is in the text in any form (like "33OML" where O might be misread as 0)
                            if '330' in volume_text.replace('O', '0').replace('o', '0'):
                                volume = 330
                                print(f"Extracted volume using OCR correction: 330 ml from text: '{volume_text}'")
                            # If "500" is in the text in any form
                            elif '500' in volume_text.replace('O', '0').replace('o', '0'):
                                volume = 500
                                print(f"Extracted volume using OCR correction: 500 ml from text: '{volume_text}'")
                            # If "250" is in the text in any form
                            elif '250' in volume_text.replace('O', '0').replace('o', '0'):
                                volume = 250
                                print(f"Extracted volume using OCR correction: 250 ml from text: '{volume_text}'")
                            # Special case for orange juice - default to 1L (1000ml)
                            elif 'orange' in drink_type.lower() and 'juice' in drink_type.lower():
                                volume = 1000
                                print(f"Detected orange juice with no volume, defaulting to 1000ml (1L)")
                            else:
                                # If we still can't extract a volume, use the original text
                                print(f"WARNING: Could not extract volume from n8n response: '{volume_text}'")
                                # Ask the user to manually enter the volume
                                volume = 0  # This will trigger the "Invalid volume" error and redirect to dashboard

            # Create text for display
            # Use drink-type if available, otherwise use drinktype
            drink_type = n8n_result.get('drink-type', n8n_result.get('drinktype', 'Unknown'))
            text = f"{drink_type} {n8n_result.get('volume', 'Unknown')}"

            return render_template('label_recognized.html',
                                  volume=volume,
                                  text=text,
                                  image_path=image_path,
                                  drink_types=drink_types,
                                  suggested_drink_type_id=suggested_drink_type_id,
                                  extraction_method='n8n')

        except Exception as e:
            print(f"Error with n8n webhook: {e}")
            import traceback
            traceback.print_exc()

            # If this is an AJAX request, return error JSON
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': f"Error with n8n webhook: {str(e)}",
                    'image_url': image_url
                })

            # Fall back to OCR processing for traditional form submission
            print("Falling back to OCR processing due to n8n webhook error")
            try:
                result = ocr_processor.process_label(full_image_path)
            except Exception as ocr_error:
                print(f"Error with OCR processing: {ocr_error}")
                traceback.print_exc()
                # Return a generic error response
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'error': f"Error processing image: {str(ocr_error)}",
                        'image_url': image_url
                    })
                return render_template('label_not_recognized.html',
                                      text=f"Error: {str(ocr_error)}",
                                      image_path=image_path,
                                      drink_types=DrinkType.query.all())

            # Process the OCR result
            if result['success']:
                drink_types = DrinkType.query.all()
                suggested_drink_type_id = None
                extraction_method = result.get('method', 'ocr')

                # Try to suggest a drink type based on the OCR result
                if 'drink_type' in result and result['drink_type']:
                    drink_name = result['drink_type'].lower()
                    for drink_type in drink_types:
                        if drink_name in drink_type.name.lower():
                            suggested_drink_type_id = drink_type.id
                            break

                return render_template('label_recognized.html',
                                      volume=result['volume_ml'],
                                      text=result['text'],
                                      image_path=image_path,
                                      drink_types=drink_types,
                                      suggested_drink_type_id=suggested_drink_type_id,
                                      extraction_method=extraction_method)
            else:
                drink_types = DrinkType.query.all()
                return render_template('label_not_recognized.html',
                                      text=result.get('text', ''),
                                      image_path=image_path,
                                      drink_types=drink_types)





    return render_template('read_label.html')

@app.route('/label_recognized', methods=['GET'])
@login_required
def label_recognized():
    # Get parameters from the URL
    volume = request.args.get('volume', '0')
    drinktype = request.args.get('drinktype', 'Unknown')
    text = request.args.get('text', '')
    image_path = request.args.get('image_path', '')

    print(f"label_recognized route received volume: {volume}, type: {type(volume)}")

    # Extract numeric value from volume text (e.g., "350ml" -> 350)
    import re
    print(f"Raw volume text in label_recognized: '{volume}'")

    # Check for duplicate "ml ml" which can happen with OCR errors
    if isinstance(volume, str) and 'ml ml' in volume.lower():
        # Fix the duplicate ml
        volume = volume.lower().replace('ml ml', 'ml')
        print(f"Fixed duplicate 'ml ml' in text: '{volume}'")

    # Check for "1 ml" which might actually be "1L" misread by OCR
    if isinstance(volume, str) and re.search(r'^\s*1\s*ml\s*$', volume.lower()) and ('juice' in text.lower() or 'orange' in text.lower()):
        volume = 1000
        print(f"Detected likely '1L' misread as '1 ml', correcting to 1000ml")

    # Check for liters in the text (1L, 1l, 1 liter, etc.)
    if isinstance(volume, str):
        liter_match = re.search(r'(\d+(?:\.\d+)?)(?:\s*(?:l|L|liter|liters|Liter|Liters))', volume)
        if liter_match:
            # Convert liters to milliliters (1L = 1000ml)
            liters = float(liter_match.group(1))
            volume = int(liters * 1000)
            print(f"Converted {liters}L to {volume}ml from text: '{volume}'")
        else:
            # Check for "1L" in the image or label text
            if '1l' in volume.lower() or '1 l' in volume.lower():
                volume = 1000
                print(f"Detected 1L in text, setting volume to 1000ml from text: '{volume}'")
            # Check for "1.5L" in the image or label text
            elif '1.5l' in volume.lower() or '1.5 l' in volume.lower():
                volume = 1500
                print(f"Detected 1.5L in text, setting volume to 1500ml from text: '{volume}'")
            # Check for "2L" in the image or label text
            elif '2l' in volume.lower() or '2 l' in volume.lower():
                volume = 2000
                print(f"Detected 2L in text, setting volume to 2000ml from text: '{volume}'")
            else:
                # Try to find a number followed by "ml" (case insensitive)
                volume_match = re.search(r'(\d+)(?:\s*(?:ml|ML|mL|Ml))', volume)
                if volume_match:
                    volume = int(volume_match.group(1))
                    print(f"Extracted volume using pattern 1: {volume} ml from text: '{volume}'")
                else:
                    # Try to find any number in the text
                    volume_match = re.search(r'(\d+)', volume)
                    if volume_match:
                        # Check if this might be a liter value that wasn't properly detected
                        extracted_num = int(volume_match.group(1))
                        if extracted_num <= 3 and ('juice' in text.lower() or 'water' in text.lower() or 'orange' in text.lower()):
                            # Small numbers (1-3) for juice or water are likely liters
                            volume = extracted_num * 1000
                            print(f"Converted likely liter value {extracted_num}L to {volume}ml from text: '{volume}'")
                        else:
                            volume = extracted_num
                            print(f"Extracted volume using pattern 2: {volume} ml from text: '{volume}'")
                    else:
                        # If "330" is in the text in any form (like "33OML" where O might be misread as 0)
                        if '330' in volume.replace('O', '0').replace('o', '0'):
                            volume = 330
                            print(f"Extracted volume using OCR correction: 330 ml from text: '{volume}'")
                        # If "500" is in the text in any form
                        elif '500' in volume.replace('O', '0').replace('o', '0'):
                            volume = 500
                            print(f"Extracted volume using OCR correction: 500 ml from text: '{volume}'")
                        # If "250" is in the text in any form
                        elif '250' in volume.replace('O', '0').replace('o', '0'):
                            volume = 250
                            print(f"Extracted volume using OCR correction: 250 ml from text: '{volume}'")
                        # Special case for orange juice - default to 1L (1000ml)
                        elif 'orange' in text.lower() and 'juice' in text.lower():
                            volume = 1000
                            print(f"Detected orange juice with no volume, defaulting to 1000ml (1L)")
                        else:
                            # If we still can't extract a volume, show an error
                            print(f"WARNING: Could not extract volume from text: '{volume}'")
                            volume = 0  # This will trigger the "Invalid volume" error

    # Get drink types for the dropdown
    drink_types = DrinkType.query.all()

    # Try to suggest a drink type based on the drinktype
    suggested_drink_type_id = None
    drink_name = drinktype.lower()

    # Special case for orange juice with missing volume
    if ('orange' in drink_name or 'juice' in drink_name) and (not volume or volume == 0 or volume == '0'):
        print(f"Detected Orange Juice with missing volume in label_recognized route, setting to 1000ml")
        volume = 1000

    # Try to find a matching drink type
    for drink_type in drink_types:
        if drink_name in drink_type.name.lower():
            suggested_drink_type_id = drink_type.id
            break

    return render_template('label_recognized.html',
                          volume=volume,
                          text=text,
                          image_path=image_path,
                          drink_types=drink_types,
                          suggested_drink_type_id=suggested_drink_type_id,
                          extraction_method='n8n')

@app.route('/log_from_label', methods=['POST'])
@login_required
def log_from_label():
    # Get the raw volume value from the form
    raw_volume = request.form.get('volume')
    print(f"log_from_label received raw volume: {raw_volume}, type: {type(raw_volume)}")

    # Extract numeric value from the volume string if it's not already a number
    if raw_volume and isinstance(raw_volume, str):
        import re
        # Extract only the numeric part
        numeric_match = re.search(r'(\d+)', raw_volume)
        if numeric_match:
            raw_volume = numeric_match.group(1)
            print(f"Extracted numeric volume: {raw_volume}")

    # Convert to integer
    volume = int(raw_volume) if raw_volume and raw_volume.isdigit() else 0
    # Direct check for orange juice in the form data
    form_text = request.form.get('text', '').lower()
    if ('orange' in form_text and 'juice' in form_text) and (not volume or volume == 0):
        print(f"Direct fix: Detected Orange Juice with missing volume, setting to 1000ml (1L)")
        volume = 1000

    print(f"log_from_label converted volume: {volume}, type: {type(volume)}")

    drink_type_id = request.form.get('drink_type_id', type=int)

    # Special case for Pepsi cans - OCR often misreads 330ml as 33ml
    if drink_type_id:
        drink_type = DrinkType.query.get(drink_type_id)
        if drink_type and drink_type.name.lower() == 'pepsi' and volume > 0 and volume < 100:
            print(f"Detected Pepsi can with small volume ({volume}ml), correcting to 330ml")
            volume = 330
        # Special case for Orange Juice - often 1L bottles
        elif drink_type and ('orange' in drink_type.name.lower() or 'juice' in drink_type.name.lower()) and (volume == 0 or not volume):
            print(f"Detected Orange Juice with missing volume, setting to 1000ml (1L)")
            volume = 1000

    if not volume or volume <= 0:
        flash('Invalid volume', 'danger')
        return redirect(url_for('dashboard'))

    # If no drink type specified, default to water (id=1)
    if not drink_type_id:
        water_type = DrinkType.query.filter_by(name='Water').first()
        drink_type_id = water_type.id if water_type else None

    # Create new water log
    new_log = WaterLog(
        amount=volume,
        user_id=current_user.id,
        drink_type_id=drink_type_id,
        input_method='ocr'
    )

    db.session.add(new_log)
    db.session.commit()

    # Get the drink type name for the flash message
    drink_name = "water"
    if drink_type_id:
        drink_type = DrinkType.query.get(drink_type_id)
        if drink_type:
            drink_name = drink_type.name.lower()

    flash(f'{volume} ml of {drink_name} logged successfully from label!', 'success')
    return redirect(url_for('dashboard'))

# Voice Recognition Route
@app.route('/voice_n8n', methods=['GET', 'POST'])
@login_required
def voice_n8n():
    """Voice input using local processing"""
    # Check if voice recognition is available
    if not voice_recognition_available:
        flash('Voice input is not available. Please install the required dependencies.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('voice_n8n.html')

# Gesture Logging Route - REMOVED
# Hand gesture feature has been removed from the application

# Redirect old voice_input URL to new voice_n8n
@app.route('/voice_input', methods=['GET', 'POST'])
@login_required
def voice_input():
    """Redirect to the new voice input page"""
    return redirect(url_for('voice_n8n'))

@app.route('/api/process_voice', methods=['POST'])
@login_required
def process_voice():
    """API endpoint to process voice input locally - supports both food and drinks"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Process the text using our enhanced voice processor
        result = voice_processor.process_text_input(text)

        if not result['success']:
            return jsonify({'error': result.get('error', 'Processing failed')}), 400

        if result['type'] == 'food':
            # Food input is no longer supported
            return jsonify({
                'success': False,
                'error': 'Food logging via voice is not supported. Please use the eating tracker manually.',
                'type': 'food_not_supported'
            })
        else:
            # Drink input processing
            volume_ml = result['volume_ml']
            drink_type = result['drink_type']

            # Get drink type ID from database
            drink_type_obj = DrinkType.query.filter_by(name=drink_type.title()).first()
            if not drink_type_obj:
                drink_type_obj = DrinkType.query.filter_by(name='Water').first()

            print(f"Processed drink input: '{text}' → {volume_ml}ml of {drink_type}")

            return jsonify({
                'success': True,
                'type': 'drink',
                'result': {
                    'volume': f"{volume_ml} ml",
                    'drink_type': drink_type.title(),
                    'drink_type_id': drink_type_obj.id if drink_type_obj else 1,
                    'volume_ml': volume_ml,
                    'text': result['text'],
                    'source': 'voice_processor'
                }
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



@app.route('/api/progress')
@login_required
def progress_api():
    """Get current day's water intake progress"""
    try:
        from datetime import date

        # Get today's intake from database
        today = date.today()
        today_entries = WaterLog.query.filter(
            WaterLog.user_id == current_user.id,
            db.func.date(WaterLog.timestamp) == today
        ).all()

        total_intake = sum(entry.amount for entry in today_entries)
        daily_goal = current_user.daily_goal
        progress_percentage = (total_intake / daily_goal * 100) if daily_goal > 0 else 0

        # Also try to get data from n8n/Google Sheets if configured
        n8n_webhook_url = app.config.get('N8N_WEBHOOK_URL')
        external_data = None

        if n8n_webhook_url:
            try:
                import requests
                # Query n8n for today's data
                query_data = {
                    'action': 'get_daily_total',
                    'name': current_user.username,
                    'date': today.strftime('%Y-%m-%d')
                }

                response = requests.post(n8n_webhook_url, json=query_data, timeout=10)
                if response.status_code == 200:
                    external_data = response.json()
            except Exception as e:
                print(f"Error querying n8n: {e}")

        return jsonify({
            'success': True,
            'total_intake': total_intake,
            'daily_goal': daily_goal,
            'progress_percentage': min(progress_percentage, 100),
            'date': today.strftime('%Y-%m-%d'),
            'entries_count': len(today_entries),
            'external_data': external_data
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



# Barcode Scanner Routes
@app.route('/barcode_scanner')
@login_required
def barcode_scanner():
    """Show barcode scanner page"""
    return render_template('barcode_scanner.html')

@app.route('/api/lookup_barcode', methods=['POST'])
@login_required
def lookup_barcode():
    """API endpoint to look up product information by barcode"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.json
    barcode = data.get('barcode', '')
    lookup_type = data.get('type', 'auto')  # 'drink', 'food', or 'auto'

    if not barcode:
        return jsonify({'error': 'No barcode provided'}), 400

    try:
        print(f"Looking up barcode: {barcode} (type: {lookup_type})")

        # Check if we already have this food item in our database
        existing_food = FoodItem.query.filter_by(barcode=barcode).first()
        if existing_food:
            print(f"Found existing food item in database: {existing_food.name}")
            return jsonify({
                'success': True,
                'product': {
                    'id': existing_food.id,
                    'name': existing_food.name,
                    'brand': existing_food.brand,
                    'barcode': barcode,
                    'type': 'food',
                    'calories_per_100g': existing_food.calories_per_100g,
                    'carbs_per_100g': existing_food.carbs_per_100g,
                    'fats_per_100g': existing_food.fats_per_100g,
                    'proteins_per_100g': existing_food.proteins_per_100g,
                    'fiber_per_100g': existing_food.fiber_per_100g,
                    'sugar_per_100g': existing_food.sugar_per_100g,
                    'sodium_per_100g': existing_food.sodium_per_100g,
                    'serving_size_g': existing_food.serving_size_g,
                    'category': existing_food.category.name if existing_food.category else None,
                    'source': 'local_database'
                }
            })

        # Try to look up the barcode using Open Food Facts API
        import requests

        # Open Food Facts API
        api_url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                product_data = response.json()

                if product_data.get('status') == 1 and 'product' in product_data:
                    product = product_data['product']

                    # Determine if this is a food or drink
                    is_food = is_food_product(product)

                    if is_food or lookup_type == 'food':
                        # Extract food/nutrition information
                        product_info = extract_food_info_from_openfoodfacts(product, barcode)
                    else:
                        # Extract drink information (existing logic)
                        product_info = {
                            'name': product.get('product_name', 'Unknown Product'),
                            'brand': product.get('brands', 'Unknown Brand'),
                            'image_url': product.get('image_url', ''),
                            'volume': extract_volume_from_product(product),
                            'drink_type_id': classify_drink_type(product),
                            'barcode': barcode,
                            'type': 'drink',
                            'source': 'openfoodfacts'
                        }

                    print(f"Product found: {product_info['name']} by {product_info.get('brand', 'Unknown')}")

                    return jsonify({
                        'success': True,
                        'product': product_info
                    })
                else:
                    print(f"Product not found in Open Food Facts for barcode: {barcode}")
            else:
                print(f"Open Food Facts API error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Open Food Facts API: {e}")

        # If Open Food Facts fails, try UPC Database API (alternative)
        try:
            upc_api_url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
            response = requests.get(upc_api_url, timeout=10)

            if response.status_code == 200:
                upc_data = response.json()

                if upc_data.get('code') == 'OK' and 'items' in upc_data and upc_data['items']:
                    item = upc_data['items'][0]

                    # Determine if this is food or drink
                    title = item.get('title', '')
                    is_food = is_food_product_from_title(title)

                    if is_food or lookup_type == 'food':
                        product_info = {
                            'name': title,
                            'brand': item.get('brand', 'Unknown Brand'),
                            'image_url': item.get('images', [''])[0] if item.get('images') else '',
                            'barcode': barcode,
                            'type': 'food',
                            'calories_per_100g': 0,  # UPC DB doesn't provide nutrition info
                            'carbs_per_100g': 0,
                            'fats_per_100g': 0,
                            'proteins_per_100g': 0,
                            'serving_size_g': 100,
                            'source': 'upcitemdb'
                        }
                    else:
                        product_info = {
                            'name': title,
                            'brand': item.get('brand', 'Unknown Brand'),
                            'image_url': item.get('images', [''])[0] if item.get('images') else '',
                            'volume': extract_volume_from_title(title),
                            'drink_type_id': classify_drink_type_from_title(title),
                            'barcode': barcode,
                            'type': 'drink',
                            'source': 'upcitemdb'
                        }

                    print(f"Product found in UPC DB: {product_info['name']}")

                    return jsonify({
                        'success': True,
                        'product': product_info
                    })

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to UPC Database API: {e}")

        # If all APIs fail, return not found
        print(f"Product not found in any database for barcode: {barcode}")
        return jsonify({
            'success': False,
            'error': 'Product not found',
            'barcode': barcode
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def extract_volume_from_product(product):
    """Extract volume from Open Food Facts product data"""
    # Try to get volume from quantity field
    quantity = product.get('quantity', '')
    if quantity:
        volume = extract_volume_from_text(quantity)
        if volume:
            return volume

    # Try to get from product name
    product_name = product.get('product_name', '')
    if product_name:
        volume = extract_volume_from_text(product_name)
        if volume:
            return volume

    # Default volume
    return 500

def extract_volume_from_title(title):
    """Extract volume from product title"""
    volume = extract_volume_from_text(title)
    return volume if volume else 500

def extract_volume_from_text(text):
    """Extract volume in ml from text"""
    import re

    # Look for patterns like "500ml", "1.5L", "16 fl oz", etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*ml',
        r'(\d+(?:\.\d+)?)\s*ML',
        r'(\d+(?:\.\d+)?)\s*l(?:iter)?',
        r'(\d+(?:\.\d+)?)\s*L(?:ITER)?',
        r'(\d+(?:\.\d+)?)\s*fl\s*oz',
        r'(\d+(?:\.\d+)?)\s*oz',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))

            # Convert to ml
            if 'l' in pattern.lower() and 'ml' not in pattern.lower():
                # Liters to ml
                return int(value * 1000)
            elif 'oz' in pattern.lower():
                # Fluid ounces to ml
                return int(value * 29.5735)
            else:
                # Already in ml
                return int(value)

    return None

def classify_drink_type(product):
    """Classify drink type from Open Food Facts product data"""
    # Get categories
    categories = product.get('categories', '').lower()
    product_name = product.get('product_name', '').lower()

    # Combine for analysis
    text = f"{categories} {product_name}"

    return classify_drink_type_from_title(text)

def classify_drink_type_from_title(title):
    """Classify drink type from product title/text"""
    title_lower = title.lower()

    print(f"Classifying drink type for: '{title}'")

    # Classification logic - order matters, check specific brands first
    if any(word in title_lower for word in ['pepsi', 'pepsi-cola']):
        print("Classified as Pepsi")
        return 7  # Pepsi
    elif any(word in title_lower for word in ['coca-cola', 'coke', 'coca cola']):
        print("Classified as Soda (Coca-Cola)")
        return 6  # Soda
    elif any(word in title_lower for word in ['sprite', 'fanta', 'mountain dew', 'dr pepper']):
        print("Classified as Soda (other brands)")
        return 6  # Soda
    elif any(word in title_lower for word in ['soda', 'cola', 'carbonated', 'soft drink']):
        print("Classified as Soda (generic)")
        return 6  # Soda
    elif any(word in title_lower for word in ['water', 'aqua', 'h2o']):
        print("Classified as Water")
        return 1  # Water
    elif any(word in title_lower for word in ['tea', 'iced tea', 'green tea', 'black tea']):
        print("Classified as Tea")
        return 2  # Tea
    elif any(word in title_lower for word in ['coffee', 'espresso', 'latte', 'cappuccino']):
        print("Classified as Coffee")
        return 3  # Coffee
    elif any(word in title_lower for word in ['juice', 'orange', 'apple', 'grape', 'cranberry']):
        print("Classified as Juice")
        return 4  # Juice
    elif any(word in title_lower for word in ['milk', 'dairy', 'lactose']):
        print("Classified as Milk")
        return 5  # Milk
    else:
        print("No match found, defaulting to Water")
        return 1  # Default to water

# Food-related helper functions for barcode scanning
def is_food_product(product):
    """Determine if a product from Open Food Facts is food (not drink)"""
    # Check categories
    categories = product.get('categories', '').lower()

    # Drink indicators
    drink_keywords = ['beverage', 'drink', 'juice', 'water', 'soda', 'tea', 'coffee', 'milk', 'beer', 'wine']
    if any(keyword in categories for keyword in drink_keywords):
        return False

    # Food indicators
    food_keywords = ['food', 'snack', 'meal', 'bread', 'fruit', 'vegetable', 'meat', 'dairy', 'cereal']
    if any(keyword in categories for keyword in food_keywords):
        return True

    # Check product name
    product_name = product.get('product_name', '').lower()
    if any(keyword in product_name for keyword in drink_keywords):
        return False

    # Default to food if unclear
    return True

def is_food_product_from_title(title):
    """Determine if a product is food based on title"""
    title_lower = title.lower()

    drink_keywords = ['drink', 'juice', 'water', 'soda', 'tea', 'coffee', 'milk', 'beer', 'wine', 'beverage']
    if any(keyword in title_lower for keyword in drink_keywords):
        return False

    return True

def extract_food_info_from_openfoodfacts(product, barcode):
    """Extract food/nutrition information from Open Food Facts product data"""
    # Get basic product info
    name = product.get('product_name', 'Unknown Product')
    brand = product.get('brands', 'Unknown Brand')
    image_url = product.get('image_url', '')

    # Get nutrition facts (per 100g)
    nutriments = product.get('nutriments', {})

    # Extract nutrition values with fallbacks
    calories = nutriments.get('energy-kcal_100g', nutriments.get('energy_100g', 0))
    if isinstance(calories, str):
        try:
            calories = float(calories)
        except:
            calories = 0

    carbs = nutriments.get('carbohydrates_100g', 0)
    if isinstance(carbs, str):
        try:
            carbs = float(carbs)
        except:
            carbs = 0

    fats = nutriments.get('fat_100g', 0)
    if isinstance(fats, str):
        try:
            fats = float(fats)
        except:
            fats = 0

    proteins = nutriments.get('proteins_100g', 0)
    if isinstance(proteins, str):
        try:
            proteins = float(proteins)
        except:
            proteins = 0

    fiber = nutriments.get('fiber_100g', 0)
    if isinstance(fiber, str):
        try:
            fiber = float(fiber)
        except:
            fiber = 0

    sugar = nutriments.get('sugars_100g', 0)
    if isinstance(sugar, str):
        try:
            sugar = float(sugar)
        except:
            sugar = 0

    sodium = nutriments.get('sodium_100g', 0)
    if isinstance(sodium, str):
        try:
            sodium = float(sodium) * 1000  # Convert g to mg
        except:
            sodium = 0
    elif sodium > 0:
        sodium = sodium * 1000  # Convert g to mg

    # Get serving size
    serving_size = product.get('serving_size', '100g')
    serving_size_g = 100  # Default
    try:
        # Try to extract number from serving size
        import re
        match = re.search(r'(\d+)', serving_size)
        if match:
            serving_size_g = float(match.group(1))
    except:
        serving_size_g = 100

    # Determine food category
    categories = product.get('categories', '').lower()
    category_name = classify_food_category(categories, name)

    return {
        'name': name,
        'brand': brand,
        'image_url': image_url,
        'barcode': barcode,
        'type': 'food',
        'calories_per_100g': calories,
        'carbs_per_100g': carbs,
        'fats_per_100g': fats,
        'proteins_per_100g': proteins,
        'fiber_per_100g': fiber,
        'sugar_per_100g': sugar,
        'sodium_per_100g': sodium,
        'serving_size_g': serving_size_g,
        'category': category_name,
        'source': 'openfoodfacts'
    }

def classify_food_category(categories, product_name):
    """Classify food into categories based on Open Food Facts categories"""
    categories_lower = categories.lower()
    name_lower = product_name.lower()

    # Define category mappings
    category_mappings = {
        'Fruits': ['fruit', 'apple', 'banana', 'orange', 'berry'],
        'Vegetables': ['vegetable', 'carrot', 'broccoli', 'spinach', 'tomato'],
        'Grains': ['bread', 'rice', 'pasta', 'cereal', 'grain', 'wheat'],
        'Proteins': ['meat', 'chicken', 'beef', 'fish', 'egg', 'protein'],
        'Dairy': ['dairy', 'milk', 'cheese', 'yogurt', 'butter'],
        'Snacks': ['snack', 'chip', 'cookie', 'cracker', 'candy'],
        'Nuts & Seeds': ['nut', 'almond', 'peanut', 'seed', 'walnut'],
        'Sweets': ['sweet', 'chocolate', 'candy', 'dessert', 'cake']
    }

    # Check categories and product name
    for category, keywords in category_mappings.items():
        if any(keyword in categories_lower or keyword in name_lower for keyword in keywords):
            return category

    return 'Other'

# Data Export Routes
@app.route('/export_data')
@login_required
def export_data():
    """Show data export page"""
    return render_template('export_data.html', drink_types=DrinkType.query.all())

@app.route('/test-export')
@login_required
def test_export_page():
    """Test export functionality page"""
    return render_template('test_export.html', drink_types=DrinkType.query.all())

@app.route('/api/test-export-debug', methods=['GET', 'POST'])
@login_required
def test_export_debug():
    """Debug endpoint for testing export functionality"""
    try:
        from data_export import DataExporter

        # Create exporter
        exporter = DataExporter(current_user.id)

        # Get basic stats
        stats = exporter.get_summary_stats()

        # Test CSV export
        csv_data = exporter.export_csv()
        csv_length = len(csv_data) if csv_data else 0

        return jsonify({
            'success': True,
            'user_id': current_user.id,
            'username': current_user.username,
            'stats': stats,
            'csv_length': csv_length,
            'csv_preview': csv_data[:200] if csv_data else None,
            'message': 'Export functionality is working correctly'
        })

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/export', methods=['POST'])
@login_required
def api_export():
    """API endpoint for data export"""
    try:
        from data_export import DataExporter
    except ImportError:
        from .data_export import DataExporter
    from datetime import datetime
    import tempfile
    import os

    try:
        # Get form data
        export_format = request.form.get('format', 'csv')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        drink_types = request.form.getlist('drink_types')
        include_charts = request.form.get('include_charts') == 'true'
        include_food = request.form.get('include_food') == 'true'

        # Parse dates
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Add 23:59:59 to include the entire end date
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Convert drink_types to integers if provided
        if drink_types:
            drink_types = [int(dt) for dt in drink_types if dt.isdigit()]
        else:
            drink_types = None

        # Create exporter
        exporter = DataExporter(current_user.id)

        # Generate export based on format
        if export_format == 'csv':
            if include_food:
                content = exporter.export_combined_csv(start_date, end_date, drink_types)
                filename_prefix = 'combined_data'
            else:
                content = exporter.export_csv(start_date, end_date, drink_types, include_food)
                filename_prefix = 'water_intake_data'

            if content is None:
                return jsonify({'error': 'No data found for the specified criteria'}), 404

            # Create response
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}_{datetime.now().strftime("%Y%m%d")}.csv'
            return response

        elif export_format == 'json':
            content = exporter.export_json(start_date, end_date, drink_types, include_food)
            if content is None:
                return jsonify({'error': 'No data found for the specified criteria'}), 404

            # Create response
            response = make_response(content)
            response.headers['Content-Type'] = 'application/json'
            filename_prefix = 'combined_data' if include_food else 'water_intake_data'
            response.headers['Content-Disposition'] = f'attachment; filename={filename_prefix}_{datetime.now().strftime("%Y%m%d")}.json'
            return response

        elif export_format == 'pdf':
            # Check if ReportLab is available for PDF generation
            try:
                from data_export import reportlab_available
            except ImportError:
                from .data_export import reportlab_available

            print(f"PDF export requested. ReportLab available: {reportlab_available}")

            if not reportlab_available:
                print("ReportLab not available, falling back to text export")
                # If ReportLab is not available, export as text file instead
                content = exporter.export_pdf(start_date, end_date, drink_types, include_charts)
                if content is None:
                    return jsonify({'error': 'No data found for the specified criteria'}), 404

                # Create response as text file
                response = make_response(content)
                response.headers['Content-Type'] = 'text/plain'
                response.headers['Content-Disposition'] = f'attachment; filename=water_intake_report_{datetime.now().strftime("%Y%m%d")}.txt'
                return response
            else:
                print("ReportLab available, generating PDF")
                # Normal PDF export
                content = exporter.export_pdf(start_date, end_date, drink_types, include_charts)
                if content is None:
                    print("PDF export returned None - no data found")
                    return jsonify({'error': 'No data found for the specified criteria'}), 404

                print(f"PDF generated successfully, size: {len(content)} bytes")
                # Create response
                response = make_response(content)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=water_intake_report_{datetime.now().strftime("%Y%m%d")}.pdf'
                return response

        else:
            return jsonify({'error': 'Invalid export format'}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/preview', methods=['POST'])
@login_required
def api_export_preview():
    """API endpoint for export preview/statistics"""
    try:
        from data_export import DataExporter
    except ImportError:
        from .data_export import DataExporter
    from datetime import datetime

    try:
        # Get form data
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        drink_types = request.form.getlist('drink_types')

        # Parse dates
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Convert drink_types to integers if provided
        if drink_types:
            drink_types = [int(dt) for dt in drink_types if dt.isdigit()]
        else:
            drink_types = None

        # Create exporter and get statistics
        exporter = DataExporter(current_user.id)
        stats = exporter.get_summary_stats(start_date, end_date)

        print(f"Raw stats: {stats}")
        print(f"Stats types: {[(k, type(v)) for k, v in stats.items()]}")

        # Convert any numpy/pandas data types to native Python types for JSON serialization
        def convert_to_json_serializable(obj):
            """Convert numpy/pandas types to native Python types"""
            # Handle numpy/pandas types by checking type names
            type_name = type(obj).__name__

            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif hasattr(obj, 'tolist'):  # numpy array
                return obj.tolist()
            elif 'int' in type_name:  # int64, int32, etc.
                return int(obj)
            elif 'float' in type_name:  # float64, float32, etc.
                return float(obj)
            elif 'bool' in type_name:  # bool_, etc.
                return bool(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(v) for v in obj]
            else:
                return obj

        # Clean the stats data
        clean_stats = convert_to_json_serializable(stats)
        print(f"Clean stats: {clean_stats}")
        print(f"Clean stats types: {[(k, type(v)) for k, v in clean_stats.items()]}")

        return jsonify({
            'success': True,
            'stats': clean_stats
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/water-data')
@login_required
def api_water_data():
    # Get last 7 days data
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=6)

    # Query data for last 7 days
    results = db.session.query(
        db.func.date(WaterLog.timestamp).label('day'),
        db.func.sum(WaterLog.amount).label('total')
    ).filter(
        WaterLog.user_id == current_user.id,
        db.func.date(WaterLog.timestamp) >= start_date,
        db.func.date(WaterLog.timestamp) <= end_date
    ).group_by(
        db.func.date(WaterLog.timestamp)
    ).order_by(
        db.func.date(WaterLog.timestamp)
    ).all()

    # Format data for API
    data = []
    for day, total in results:
        # Check if day is already a string
        if isinstance(day, str):
            date_str = day
        else:
            date_str = day.strftime('%Y-%m-%d')
        data.append({'date': date_str, 'amount': total})

    return jsonify({
        'success': True,
        'data': data,
        'user': {
            'username': current_user.username,
            'daily_goal': current_user.daily_goal,
            'preferred_unit': current_user.preferred_unit
        }
    })

# ============================================================================
# EATING TRACKER ROUTES
# ============================================================================

@app.route('/eating')
@login_required
def eating_dashboard():
    """Main eating tracker dashboard"""
    # Get today's date
    today = datetime.now(timezone.utc).date()

    # Get today's meal logs
    today_meals = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        db.func.date(MealLog.timestamp) == today
    ).all()

    # Calculate today's nutrition totals
    today_nutrition = {
        'calories': sum(meal.calories for meal in today_meals),
        'carbs': sum(meal.carbs for meal in today_meals),
        'fats': sum(meal.fats for meal in today_meals),
        'proteins': sum(meal.proteins for meal in today_meals),
        'fiber': sum(meal.fiber for meal in today_meals),
        'sugar': sum(meal.sugar for meal in today_meals),
        'sodium': sum(meal.sodium for meal in today_meals)
    }

    # Get user's nutrition goals
    nutrition_goals = NutritionGoals.query.filter_by(user_id=current_user.id).first()
    if not nutrition_goals:
        # Create default goals
        nutrition_goals = NutritionGoals(user_id=current_user.id)
        db.session.add(nutrition_goals)
        db.session.commit()

    # Calculate progress percentages
    progress = {}
    if nutrition_goals:
        progress = {
            'calories': min((today_nutrition['calories'] / nutrition_goals.daily_calories) * 100, 100) if nutrition_goals.daily_calories > 0 else 0,
            'carbs': min((today_nutrition['carbs'] / nutrition_goals.daily_carbs) * 100, 100) if nutrition_goals.daily_carbs > 0 else 0,
            'fats': min((today_nutrition['fats'] / nutrition_goals.daily_fats) * 100, 100) if nutrition_goals.daily_fats > 0 else 0,
            'proteins': min((today_nutrition['proteins'] / nutrition_goals.daily_proteins) * 100, 100) if nutrition_goals.daily_proteins > 0 else 0
        }

    # Get meals by type for today
    meals_by_type = {}
    for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
        meals_by_type[meal_type] = [meal for meal in today_meals if meal.meal_type == meal_type]

    # Get user's meal containers
    meal_containers = MealContainer.query.filter_by(user_id=current_user.id).order_by(MealContainer.is_favorite.desc()).limit(6).all()

    # Get food categories
    food_categories = FoodCategory.query.all()

    return render_template('eating_dashboard.html',
                          today_nutrition=today_nutrition,
                          nutrition_goals=nutrition_goals,
                          progress=progress,
                          meals_by_type=meals_by_type,
                          meal_containers=meal_containers,
                          food_categories=food_categories)

@app.route('/eating/log_meal', methods=['POST'])
@login_required
def log_meal():
    """Log a meal entry"""
    try:
        # Get form data
        food_name = request.form.get('food_name')
        quantity_g = float(request.form.get('quantity_g', 0))
        meal_type = request.form.get('meal_type', 'meal')
        food_item_id = request.form.get('food_item_id', type=int)
        meal_container_id = request.form.get('meal_container_id', type=int)
        notes = request.form.get('notes')

        # Validate required fields
        if not food_name or quantity_g <= 0:
            flash('Please enter a valid food name and quantity', 'danger')
            return redirect(url_for('eating_dashboard'))

        # Calculate nutrition values
        calories = carbs = fats = proteins = fiber = sugar = sodium = 0

        if food_item_id:
            # Get nutrition from food item
            food_item = FoodItem.query.get(food_item_id)
            if food_item:
                nutrition = food_item.get_nutrition_for_quantity(quantity_g)
                calories = nutrition['calories']
                carbs = nutrition['carbs']
                fats = nutrition['fats']
                proteins = nutrition['proteins']
                fiber = nutrition['fiber']
                sugar = nutrition['sugar']
                sodium = nutrition['sodium']
        elif meal_container_id:
            # Get nutrition from meal container
            meal_container = MealContainer.query.get(meal_container_id)
            if meal_container:
                # For meal containers, we use the total nutrition values
                calories = meal_container.total_calories
                carbs = meal_container.total_carbs
                fats = meal_container.total_fats
                proteins = meal_container.total_proteins
        else:
            # Manual entry - get nutrition from form
            calories = float(request.form.get('calories', 0))
            carbs = float(request.form.get('carbs', 0))
            fats = float(request.form.get('fats', 0))
            proteins = float(request.form.get('proteins', 0))
            fiber = float(request.form.get('fiber', 0))
            sugar = float(request.form.get('sugar', 0))
            sodium = float(request.form.get('sodium', 0))

        # Create meal log entry
        meal_log = MealLog(
            user_id=current_user.id,
            food_item_id=food_item_id,
            meal_container_id=meal_container_id,
            food_name=food_name,
            quantity_g=quantity_g,
            calories=calories,
            carbs=carbs,
            fats=fats,
            proteins=proteins,
            fiber=fiber,
            sugar=sugar,
            sodium=sodium,
            meal_type=meal_type,
            input_method='manual',
            notes=notes
        )

        db.session.add(meal_log)
        db.session.commit()

        flash(f'{food_name} logged successfully! ({calories:.0f} calories)', 'success')
        return redirect(url_for('eating_dashboard'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error logging meal: {str(e)}', 'danger')
        return redirect(url_for('eating_dashboard'))

@app.route('/eating/nutrition_goals', methods=['GET', 'POST'])
@login_required
def nutrition_goals():
    """Manage nutrition goals"""
    goals = NutritionGoals.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        # Get form data
        daily_calories = int(request.form.get('daily_calories', 2000))
        daily_carbs = float(request.form.get('daily_carbs', 250))
        daily_fats = float(request.form.get('daily_fats', 65))
        daily_proteins = float(request.form.get('daily_proteins', 50))
        daily_fiber = float(request.form.get('daily_fiber', 25))
        daily_sugar = float(request.form.get('daily_sugar', 50))
        daily_sodium = float(request.form.get('daily_sodium', 2300))

        weight_kg = request.form.get('weight_kg', type=float)
        height_cm = request.form.get('height_cm', type=float)
        age = request.form.get('age', type=int)
        activity_level = request.form.get('activity_level', 'moderate')
        goal_type = request.form.get('goal_type', 'maintain')

        if not goals:
            # Create new goals
            goals = NutritionGoals(
                user_id=current_user.id,
                daily_calories=daily_calories,
                daily_carbs=daily_carbs,
                daily_fats=daily_fats,
                daily_proteins=daily_proteins,
                daily_fiber=daily_fiber,
                daily_sugar=daily_sugar,
                daily_sodium=daily_sodium,
                weight_kg=weight_kg,
                height_cm=height_cm,
                age=age,
                activity_level=activity_level,
                goal_type=goal_type
            )
            db.session.add(goals)
        else:
            # Update existing goals
            goals.daily_calories = daily_calories
            goals.daily_carbs = daily_carbs
            goals.daily_fats = daily_fats
            goals.daily_proteins = daily_proteins
            goals.daily_fiber = daily_fiber
            goals.daily_sugar = daily_sugar
            goals.daily_sodium = daily_sodium
            goals.weight_kg = weight_kg
            goals.height_cm = height_cm
            goals.age = age
            goals.activity_level = activity_level
            goals.goal_type = goal_type

        db.session.commit()
        flash('Nutrition goals updated successfully!', 'success')
        return redirect(url_for('eating_dashboard'))

    return render_template('nutrition_goals.html', goals=goals)

@app.route('/eating/food_search')
@login_required
def food_search():
    """Search for food items"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)

    # Build query
    food_query = FoodItem.query

    if query:
        food_query = food_query.filter(FoodItem.name.ilike(f'%{query}%'))

    if category_id:
        food_query = food_query.filter(FoodItem.category_id == category_id)

    foods = food_query.limit(20).all()
    categories = FoodCategory.query.all()

    return render_template('food_search.html', foods=foods, categories=categories, query=query, selected_category=category_id)

@app.route('/eating/api/food_search')
@login_required
def api_food_search():
    """API endpoint for food search (for AJAX)"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)

    # Build query
    food_query = FoodItem.query

    if query:
        food_query = food_query.filter(FoodItem.name.ilike(f'%{query}%'))

    if category_id:
        food_query = food_query.filter(FoodItem.category_id == category_id)

    foods = food_query.limit(10).all()

    # Format response
    results = []
    for food in foods:
        results.append({
            'id': food.id,
            'name': food.name,
            'brand': food.brand,
            'calories_per_100g': food.calories_per_100g,
            'carbs_per_100g': food.carbs_per_100g,
            'fats_per_100g': food.fats_per_100g,
            'proteins_per_100g': food.proteins_per_100g,
            'serving_size_g': food.serving_size_g,
            'category': food.category.name if food.category else None
        })

    return jsonify({'foods': results})

@app.route('/eating/api/nutrition_data')
@login_required
def api_nutrition_data():
    """API endpoint for nutrition data (for charts)"""
    days = request.args.get('days', 7, type=int)

    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)

    # Get meal logs for the date range
    meal_logs = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        MealLog.timestamp >= start_date,
        MealLog.timestamp <= end_date + timedelta(days=1)
    ).all()

    # Group by date and calculate totals
    nutrition_by_date = {}

    for log in meal_logs:
        date_str = log.timestamp.strftime('%Y-%m-%d')

        if date_str not in nutrition_by_date:
            nutrition_by_date[date_str] = {
                'calories': 0,
                'carbs': 0,
                'fats': 0,
                'proteins': 0,
                'fiber': 0,
                'sugar': 0,
                'sodium': 0
            }

        nutrition_by_date[date_str]['calories'] += log.calories
        nutrition_by_date[date_str]['carbs'] += log.carbs
        nutrition_by_date[date_str]['fats'] += log.fats
        nutrition_by_date[date_str]['proteins'] += log.proteins
        nutrition_by_date[date_str]['fiber'] += log.fiber or 0
        nutrition_by_date[date_str]['sugar'] += log.sugar or 0
        nutrition_by_date[date_str]['sodium'] += log.sodium or 0

    # Fill in missing dates with zeros
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str not in nutrition_by_date:
            nutrition_by_date[date_str] = {
                'calories': 0,
                'carbs': 0,
                'fats': 0,
                'proteins': 0,
                'fiber': 0,
                'sugar': 0,
                'sodium': 0
            }
        current_date += timedelta(days=1)

    return jsonify({
        'success': True,
        'data': nutrition_by_date
    })

@app.route('/eating/meal_containers')
@login_required
def meal_containers():
    """Manage meal containers"""
    containers = MealContainer.query.filter_by(user_id=current_user.id).order_by(MealContainer.created_at.desc()).all()
    return render_template('meal_containers.html', containers=containers)

@app.route('/eating/meal_containers/add', methods=['GET', 'POST'])
@login_required
def add_meal_container():
    """Add a new meal container"""
    if request.method == 'POST':
        try:
            print("Form data received:")
            for key, value in request.form.items():
                print(f"  {key}: {value}")
            print("Files received:")
            for key, file in request.files.items():
                print(f"  {key}: {file.filename if file else 'None'}")

            name = request.form.get('name')
            description = request.form.get('description')
            meal_type = request.form.get('meal_type', 'meal')

            # Get nutrition totals
            total_calories = float(request.form.get('total_calories', 0))
            total_carbs = float(request.form.get('total_carbs', 0))
            total_fats = float(request.form.get('total_fats', 0))
            total_proteins = float(request.form.get('total_proteins', 0))

            if not name:
                flash('Please enter a container name', 'danger')
                return redirect(url_for('add_meal_container'))

            # Handle image upload
            image_path = None
            if 'container_image' in request.files:
                file = request.files['container_image']
                print(f"File received: {file.filename}")
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid conflicts
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename

                    # Ensure uploads directory exists
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                    # Save to uploads folder
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_path = f'uploads/{filename}'
                    print(f"Image saved to: {image_path}")
                else:
                    print(f"File not valid or empty: {file.filename if file else 'No file'}")

            # Create meal container
            container = MealContainer(
                name=name,
                description=description,
                user_id=current_user.id,
                meal_type=meal_type,
                total_calories=total_calories,
                total_carbs=total_carbs,
                total_fats=total_fats,
                total_proteins=total_proteins,
                image_path=image_path
            )

            db.session.add(container)
            db.session.flush()  # Get the container ID

            # Add food items to the container
            food_items_data = {}
            for key, value in request.form.items():
                if key.startswith('food_items['):
                    # Parse the key to extract index and field
                    # Format: food_items[0][food_id] or food_items[0][quantity]
                    import re
                    match = re.match(r'food_items\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index = int(match.group(1))
                        field = match.group(2)

                        if index not in food_items_data:
                            food_items_data[index] = {}

                        food_items_data[index][field] = value

            # Create meal container items
            for item_data in food_items_data.values():
                if 'food_id' in item_data and 'quantity' in item_data:
                    container_item = MealContainerItem(
                        meal_container_id=container.id,
                        food_item_id=int(item_data['food_id']),
                        quantity_g=float(item_data['quantity'])
                    )
                    db.session.add(container_item)

            db.session.commit()

            flash('Meal container created successfully!', 'success')
            return redirect(url_for('meal_containers'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating meal container: {str(e)}', 'danger')
            return redirect(url_for('add_meal_container'))

    food_categories = FoodCategory.query.all()
    return render_template('add_meal_container.html', food_categories=food_categories)



@app.route('/eating/meal_containers/<int:container_id>/log', methods=['POST'])
@login_required
def log_meal_container(container_id):
    """Log a meal using a meal container"""
    container = MealContainer.query.filter_by(id=container_id, user_id=current_user.id).first_or_404()

    # Create meal log for the container
    meal_log = MealLog(
        user_id=current_user.id,
        meal_container_id=container_id,
        food_name=container.name,
        quantity_g=1,  # Meal containers are logged as 1 unit
        calories=container.total_calories,
        carbs=container.total_carbs,
        fats=container.total_fats,
        proteins=container.total_proteins,
        meal_type=container.meal_type,
        input_method='container'
    )

    db.session.add(meal_log)
    db.session.commit()

    flash(f'{container.name} logged successfully! ({container.total_calories:.0f} calories)', 'success')
    return redirect(url_for('eating_dashboard'))

@app.route('/eating/meal_containers/<int:container_id>/delete', methods=['POST'])
@login_required
def delete_meal_container(container_id):
    """Delete a meal container"""
    container = MealContainer.query.filter_by(id=container_id, user_id=current_user.id).first_or_404()

    try:
        db.session.delete(container)
        db.session.commit()
        flash(f'Meal container "{container.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting meal container: {str(e)}', 'danger')

    return redirect(url_for('meal_containers'))

@app.route('/eating/meal_containers/<int:container_id>/favorite', methods=['POST'])
@login_required
def toggle_meal_container_favorite(container_id):
    """Toggle favorite status of a meal container"""
    container = MealContainer.query.filter_by(id=container_id, user_id=current_user.id).first_or_404()

    try:
        container.is_favorite = not container.is_favorite
        db.session.commit()

        return jsonify({
            'success': True,
            'is_favorite': container.is_favorite
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/eating/voice_log', methods=['POST'])
@login_required
def voice_log_food():
    """Voice food logging is no longer supported"""
    return jsonify({
        'success': False,
        'error': 'Food logging via voice is not supported. Please use the eating tracker manually.'
    }), 400



@app.route('/eating/api/calculate_bmr', methods=['POST'])
@login_required
def calculate_bmr_api():
    """API endpoint to calculate BMR and TDEE"""
    try:
        data = request.json
        weight_kg = float(data.get('weight_kg', 0))
        height_cm = float(data.get('height_cm', 0))
        age = int(data.get('age', 0))
        gender = data.get('gender', current_user.gender)
        activity_level = data.get('activity_level', 'moderate')
        goal_type = data.get('goal_type', 'maintain')

        if not all([weight_kg, height_cm, age, gender]):
            return jsonify({'error': 'Missing required parameters'}), 400

        # Calculate BMR using Mifflin-St Jeor Equation
        if gender == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

        # Apply activity multiplier
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }

        tdee = bmr * activity_multipliers.get(activity_level, 1.55)

        # Adjust for goal
        target_calories = tdee
        if goal_type == 'lose':
            target_calories = tdee - 500  # 500 calorie deficit for 1 lb/week loss
        elif goal_type == 'gain':
            target_calories = tdee + 500  # 500 calorie surplus for 1 lb/week gain

        # Calculate macro recommendations (45-65% carbs, 20-35% fats, 10-35% proteins)
        carbs_grams = round((target_calories * 0.55) / 4)  # 55% of calories from carbs, 4 cal/g
        fats_grams = round((target_calories * 0.25) / 9)   # 25% of calories from fats, 9 cal/g
        proteins_grams = round((target_calories * 0.20) / 4)  # 20% of calories from proteins, 4 cal/g

        # Calculate other nutrients
        fiber_grams = max(25, round(target_calories / 1000 * 14))  # 14g per 1000 calories
        sugar_grams = round(target_calories * 0.10 / 4)  # Max 10% of calories from added sugars
        sodium_mg = 2300  # Standard recommendation

        return jsonify({
            'success': True,
            'bmr': round(bmr),
            'tdee': round(tdee),
            'target_calories': round(target_calories),
            'recommendations': {
                'daily_calories': round(target_calories),
                'daily_carbs': carbs_grams,
                'daily_fats': fats_grams,
                'daily_proteins': proteins_grams,
                'daily_fiber': fiber_grams,
                'daily_sugar': sugar_grams,
                'daily_sodium': sodium_mg
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/eating/api/nutrition_recommendations')
@login_required
def nutrition_recommendations():
    """Get nutrition recommendations based on user profile"""
    try:
        # Get user's nutrition goals
        goals = NutritionGoals.query.filter_by(user_id=current_user.id).first()

        if not goals:
            return jsonify({'error': 'No nutrition goals found'}), 404

        recommendations = {}

        # Calculate BMR and TDEE if we have the data
        if all([goals.weight_kg, goals.height_cm, goals.age]):
            bmr = goals.calculate_bmr()
            tdee = goals.calculate_tdee()

            if bmr and tdee:
                recommendations['bmr'] = round(bmr)
                recommendations['tdee'] = round(tdee)
                recommendations['calculated'] = True
            else:
                recommendations['calculated'] = False
        else:
            recommendations['calculated'] = False

        # Get current goals
        recommendations['current_goals'] = {
            'daily_calories': goals.daily_calories,
            'daily_carbs': goals.daily_carbs,
            'daily_fats': goals.daily_fats,
            'daily_proteins': goals.daily_proteins,
            'daily_fiber': goals.daily_fiber,
            'daily_sugar': goals.daily_sugar,
            'daily_sodium': goals.daily_sodium
        }

        # Calculate macro percentages
        total_calories = goals.daily_calories
        carb_calories = goals.daily_carbs * 4
        fat_calories = goals.daily_fats * 9
        protein_calories = goals.daily_proteins * 4

        recommendations['macro_percentages'] = {
            'carbs': round((carb_calories / total_calories) * 100, 1) if total_calories > 0 else 0,
            'fats': round((fat_calories / total_calories) * 100, 1) if total_calories > 0 else 0,
            'proteins': round((protein_calories / total_calories) * 100, 1) if total_calories > 0 else 0
        }

        return jsonify({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid duplicates
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"

        # Check for drink type keywords in filename
        original_filename = filename.lower()

        # For Pepsi cans, use the standard pepsi_can.png image
        if 'pepsi' in original_filename and not original_filename.endswith(('.webm', '.mp3', '.wav', '.ogg', '.m4a')):
            # Check if we have a pepsi_can.png in the containers folder
            pepsi_image_path = os.path.join(app.static_folder, 'uploads', 'containers', 'pepsi_can.png')
            if os.path.exists(pepsi_image_path):
                print(f"Using standard Pepsi can image for {original_filename}")
                return 'uploads/containers/pepsi_can.png'

        # Make sure the static/uploads/containers folder exists
        containers_folder = os.path.join(app.static_folder, 'uploads', 'containers')
        os.makedirs(containers_folder, exist_ok=True)

        # Make sure the static/uploads/audio folder exists
        audio_folder = os.path.join(app.static_folder, 'uploads', 'audio')
        os.makedirs(audio_folder, exist_ok=True)

        # Ensure the target folder exists
        os.makedirs(folder, exist_ok=True)

        # Save the file
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        print(f"Saved file to: {filepath}")

        # Check if this is an audio file
        if filename.lower().endswith(('.webm', '.mp3', '.wav', '.ogg', '.m4a')):
            # If this is an audio file, make sure it's in the static/uploads/audio folder
            if not filepath.startswith(audio_folder):
                # Copy the file to the audio folder
                target_path = os.path.join(audio_folder, filename)
                try:
                    shutil.copy(filepath, target_path)
                    print(f"Copied file to audio folder: {target_path}")
                    # Use the path relative to static folder
                    return os.path.join('uploads', 'audio', filename)
                except Exception as e:
                    print(f"Error copying file to audio folder: {e}")
                    # Continue with normal processing if copy fails

        # If this is a container image, make sure it's in the static/uploads/containers folder
        elif 'container' in folder.lower():
            # Check if the file is already in the correct location
            if not filepath.startswith(containers_folder):
                # Copy the file to the containers folder
                target_path = os.path.join(containers_folder, filename)
                try:
                    shutil.copy(filepath, target_path)
                    print(f"Copied file to containers folder: {target_path}")
                    # Use the path relative to static folder
                    return os.path.join('uploads', 'containers', filename)
                except Exception as e:
                    print(f"Error copying file to containers folder: {e}")

        # Determine the relative path for the database
        # If the folder is under static, extract the relative path
        static_folder = app.static_folder
        if folder.startswith(static_folder):
            relative_path = folder[len(static_folder) + 1:]  # +1 for the slash
            return os.path.join(relative_path, filename).replace('\\', '/')

        # If it's not under static, it's probably in a subfolder of uploads
        if 'uploads' in folder:
            # Check if uploads is in the path
            uploads_index = folder.find('uploads')
            if uploads_index != -1:
                relative_path = folder[uploads_index:]
                return os.path.join(relative_path, filename).replace('\\', '/')

        # Fallback to the old method
        return os.path.join('uploads', os.path.basename(folder), filename).replace('\\', '/')
    return None

# Function to create default drink types
def create_default_drink_types():
    # Define default drink types
    default_types = [
        {
            'name': 'Water',
            'hydration_factor': 1.0,
            'color': '#4DA6FF',
            'icon': 'bi-droplet-fill'
        },
        {
            'name': 'Tea',
            'hydration_factor': 0.8,
            'color': '#8B5A2B',
            'icon': 'bi-cup-hot-fill'
        },
        {
            'name': 'Coffee',
            'hydration_factor': 0.6,
            'color': '#6F4E37',
            'icon': 'bi-cup-fill'
        },
        {
            'name': 'Milk',
            'hydration_factor': 0.9,
            'color': '#F5F5F5',
            'icon': 'bi-cup-straw'
        },
        {
            'name': 'Juice',
            'hydration_factor': 0.7,
            'color': '#FFA500',
            'icon': 'bi-cup'
        },
        {
            'name': 'Soda',
            'hydration_factor': 0.3,
            'color': '#8B0000',
            'icon': 'bi-cup-straw'
        },
        {
            'name': 'Pepsi',
            'hydration_factor': 0.3,
            'color': '#0000AA',
            'icon': 'bi-cup-straw'
        }
    ]

    # Check if drink types already exist
    existing_types = DrinkType.query.all()
    if not existing_types:
        for drink_type in default_types:
            new_type = DrinkType(**drink_type)
            db.session.add(new_type)

        db.session.commit()
        print("Default drink types created successfully!")
    else:
        print("Drink types already exist.")

# Function to create default food categories
def create_default_food_categories():
    """Create default food categories for the eating tracker"""
    default_categories = [
        {'name': 'Fruits', 'color': '#FF6B6B', 'icon': 'bi-apple'},
        {'name': 'Vegetables', 'color': '#4ECDC4', 'icon': 'bi-flower1'},
        {'name': 'Grains', 'color': '#FFE66D', 'icon': 'bi-grain'},
        {'name': 'Proteins', 'color': '#FF8B94', 'icon': 'bi-egg'},
        {'name': 'Dairy', 'color': '#B4F8C8', 'icon': 'bi-cup'},
        {'name': 'Snacks', 'color': '#A8E6CF', 'icon': 'bi-cookie'},
        {'name': 'Beverages', 'color': '#4DA6FF', 'icon': 'bi-cup-straw'},
        {'name': 'Sweets', 'color': '#FFB3BA', 'icon': 'bi-heart-fill'},
        {'name': 'Nuts & Seeds', 'color': '#FFDFBA', 'icon': 'bi-circle-fill'},
        {'name': 'Other', 'color': '#D4EDDA', 'icon': 'bi-three-dots'}
    ]

    # Check if categories already exist
    existing_categories = FoodCategory.query.all()
    if not existing_categories:
        for category_data in default_categories:
            category = FoodCategory(**category_data)
            db.session.add(category)

        db.session.commit()
        print("Default food categories created successfully!")
    else:
        print("Food categories already exist.")

# Function to create sample food items
def create_sample_food_items():
    """Create sample food items for demonstration"""
    # Get categories
    fruits = FoodCategory.query.filter_by(name='Fruits').first()
    vegetables = FoodCategory.query.filter_by(name='Vegetables').first()
    grains = FoodCategory.query.filter_by(name='Grains').first()
    proteins = FoodCategory.query.filter_by(name='Proteins').first()
    dairy = FoodCategory.query.filter_by(name='Dairy').first()
    snacks = FoodCategory.query.filter_by(name='Snacks').first()

    # Check if food items already exist
    existing_items = FoodItem.query.all()
    if existing_items:
        print("Food items already exist.")
        return

    sample_foods = [
        # Fruits
        {
            'name': 'Apple',
            'category_id': fruits.id if fruits else None,
            'calories_per_100g': 52,
            'carbs_per_100g': 14,
            'fats_per_100g': 0.2,
            'proteins_per_100g': 0.3,
            'fiber_per_100g': 2.4,
            'sugar_per_100g': 10.4,
            'serving_size_g': 150
        },
        {
            'name': 'Banana',
            'category_id': fruits.id if fruits else None,
            'calories_per_100g': 89,
            'carbs_per_100g': 23,
            'fats_per_100g': 0.3,
            'proteins_per_100g': 1.1,
            'fiber_per_100g': 2.6,
            'sugar_per_100g': 12.2,
            'serving_size_g': 120
        },
        # Vegetables
        {
            'name': 'Broccoli',
            'category_id': vegetables.id if vegetables else None,
            'calories_per_100g': 34,
            'carbs_per_100g': 7,
            'fats_per_100g': 0.4,
            'proteins_per_100g': 2.8,
            'fiber_per_100g': 2.6,
            'sugar_per_100g': 1.5,
            'serving_size_g': 100
        },
        # Grains
        {
            'name': 'Brown Rice',
            'category_id': grains.id if grains else None,
            'calories_per_100g': 111,
            'carbs_per_100g': 23,
            'fats_per_100g': 0.9,
            'proteins_per_100g': 2.6,
            'fiber_per_100g': 1.8,
            'sugar_per_100g': 0.4,
            'serving_size_g': 150
        },
        {
            'name': 'Whole Wheat Bread',
            'category_id': grains.id if grains else None,
            'calories_per_100g': 247,
            'carbs_per_100g': 41,
            'fats_per_100g': 4.2,
            'proteins_per_100g': 13,
            'fiber_per_100g': 6,
            'sugar_per_100g': 6,
            'serving_size_g': 30
        },
        # Proteins
        {
            'name': 'Chicken Breast',
            'category_id': proteins.id if proteins else None,
            'calories_per_100g': 165,
            'carbs_per_100g': 0,
            'fats_per_100g': 3.6,
            'proteins_per_100g': 31,
            'fiber_per_100g': 0,
            'sugar_per_100g': 0,
            'serving_size_g': 100
        },
        {
            'name': 'Eggs',
            'category_id': proteins.id if proteins else None,
            'calories_per_100g': 155,
            'carbs_per_100g': 1.1,
            'fats_per_100g': 11,
            'proteins_per_100g': 13,
            'fiber_per_100g': 0,
            'sugar_per_100g': 1.1,
            'serving_size_g': 50
        },
        # Dairy
        {
            'name': 'Greek Yogurt',
            'category_id': dairy.id if dairy else None,
            'calories_per_100g': 59,
            'carbs_per_100g': 3.6,
            'fats_per_100g': 0.4,
            'proteins_per_100g': 10,
            'fiber_per_100g': 0,
            'sugar_per_100g': 3.6,
            'serving_size_g': 170
        },
        # Snacks
        {
            'name': 'Almonds',
            'category_id': snacks.id if snacks else None,
            'calories_per_100g': 579,
            'carbs_per_100g': 22,
            'fats_per_100g': 50,
            'proteins_per_100g': 21,
            'fiber_per_100g': 12,
            'sugar_per_100g': 4.4,
            'serving_size_g': 30
        }
    ]

    for food_data in sample_foods:
        food_item = FoodItem(**food_data)
        db.session.add(food_item)

    db.session.commit()
    print("Sample food items created successfully!")

# Function to create demo user
def create_demo_user():
    # Check if demo user already exists
    demo_user = db.session.execute(db.select(User).filter_by(username="demo")).scalar_one_or_none()

    if not demo_user:
        # Create demo user with all required fields
        demo_user = User(
            username="demo",
            email="demo@example.com",
            daily_goal=2000,
            preferred_unit="ml",
            theme="light",
            accent_color="blue",
            reminder_enabled=False,
            reminder_interval=60,
            gender="not_specified",
            join_date=datetime.now(timezone.utc)
        )
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()

        # Create some demo containers
        water_bottle = Container(
            name="Water Bottle",
            volume=500,
            user_id=demo_user.id,
            created_at=datetime.now(timezone.utc)
        )
        coffee_mug = Container(
            name="Coffee Mug",
            volume=350,
            user_id=demo_user.id,
            created_at=datetime.now(timezone.utc)
        )
        # Get the Pepsi drink type (or fallback to Soda)
        pepsi_type = DrinkType.query.filter_by(name='Pepsi').first()
        if not pepsi_type:
            pepsi_type = DrinkType.query.filter_by(name='Soda').first()

        pepsi_can = Container(
            name="Pepsi Can",
            volume=350,
            user_id=demo_user.id,
            image_path="uploads/containers/pepsi_can.png",
            drink_type_id=pepsi_type.id if pepsi_type else None,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(water_bottle)
        db.session.add(coffee_mug)
        db.session.add(pepsi_can)
        db.session.commit()

        # Create the uploads directory if it doesn't exist
        container_dir = os.path.join(app.static_folder, 'uploads', 'containers')
        os.makedirs(container_dir, exist_ok=True)

        # Copy a default pepsi can image if it doesn't exist
        pepsi_image_path = os.path.join(container_dir, 'pepsi_can.png')
        if not os.path.exists(pepsi_image_path):
            try:
                # Try to import PIL
                try:
                    from PIL import Image, ImageDraw
                    has_pil = True
                except ImportError:
                    has_pil = False
                    print("PIL (Pillow) is not installed. Skipping Pepsi can image creation in demo user.")

                if has_pil:
                    # Create a simple colored image for the pepsi can
                    img = Image.new('RGB', (200, 400), color=(0, 0, 150))  # Blue background
                    draw = ImageDraw.Draw(img)
                    draw.ellipse((50, 50, 150, 150), fill=(255, 0, 0))  # Red circle
                    # Add some text to make it look like a Pepsi can
                    draw.text((70, 200), "PEPSI", fill=(255, 255, 255))
                    img.save(pepsi_image_path)
            except Exception as e:
                print(f"Error creating pepsi can image for demo user: {e}")

        print("Demo user created successfully!")
    else:
        print("Demo user already exists.")

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CONTAINER_IMAGES'], exist_ok=True)
    os.makedirs(app.config['AVATAR_IMAGES'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FILES'], exist_ok=True)

    # Create placeholder images directory
    placeholder_dir = os.path.join(app.static_folder, 'images')
    os.makedirs(placeholder_dir, exist_ok=True)

    # Create container placeholder image if it doesn't exist
    container_placeholder_path = os.path.join(placeholder_dir, 'container_placeholder.png')
    if not os.path.exists(container_placeholder_path):
        try:
            # Try to import PIL
            try:
                from PIL import Image, ImageDraw, ImageFont
                has_pil = True
            except ImportError:
                has_pil = False
                print("PIL (Pillow) is not installed. Skipping image creation.")

            if has_pil:
                img = Image.new('RGB', (200, 200), color=(240, 240, 240))
                draw = ImageDraw.Draw(img)
                draw.rectangle((50, 50, 150, 150), outline=(200, 200, 200), width=2)
                draw.line((50, 50, 150, 150), fill=(200, 200, 200), width=2)
                draw.line((50, 150, 150, 50), fill=(200, 200, 200), width=2)

                # Add text
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                    draw.text((60, 160), "Container Image", fill=(100, 100, 100), font=font)
                except:
                    # If font not available, use default
                    draw.text((60, 160), "Container Image", fill=(100, 100, 100))

                img.save(container_placeholder_path)
                print(f"Created container placeholder image at {container_placeholder_path}")
        except Exception as e:
            print(f"Error creating container placeholder image: {e}")

    # Create a pepsi can image in the containers directory
    container_dir = os.path.join(app.static_folder, 'uploads', 'containers')
    os.makedirs(container_dir, exist_ok=True)

    pepsi_image_path = os.path.join(container_dir, 'pepsi_can.png')
    if not os.path.exists(pepsi_image_path):
        try:
            # Try to import PIL
            try:
                from PIL import Image, ImageDraw, ImageFont
                has_pil = True
            except ImportError:
                has_pil = False
                print("PIL (Pillow) is not installed. Skipping Pepsi can image creation.")

            if has_pil:
                # Create a more realistic Pepsi can
                img = Image.new('RGB', (200, 400), color=(0, 0, 150))  # Blue background
                draw = ImageDraw.Draw(img)

                # Can shape
                draw.rectangle((50, 50, 150, 350), fill=(0, 0, 150), outline=(200, 200, 200), width=2)

                # Pepsi logo (simplified)
                draw.ellipse((60, 80, 140, 160), fill=(255, 255, 255))  # White circle
                draw.arc((70, 90, 130, 150), start=0, end=180, fill=(255, 0, 0), width=10)  # Red arc
                draw.arc((70, 110, 130, 170), start=180, end=360, fill=(0, 0, 150), width=10)  # Blue arc

                # Add text
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                    draw.text((70, 200), "PEPSI", fill=(255, 255, 255), font=font)
                    draw.text((60, 240), "350ml", fill=(255, 255, 255), font=font)
                except:
                    # If font not available, use default
                    draw.text((70, 200), "PEPSI", fill=(255, 255, 255))
                    draw.text((60, 240), "350ml", fill=(255, 255, 255))

                # Add some details
                draw.rectangle((50, 280, 150, 300), fill=(200, 200, 200))  # Silver band

                img.save(pepsi_image_path)
                print(f"Created pepsi can image at {pepsi_image_path}")
        except Exception as e:
            print(f"Error creating pepsi can image: {e}")

    # Initialize Smart Hydration feature
    try:
        try:
            from smart_hydration import init_app as init_smart_hydration
        except ImportError:
            from water_tracker.smart_hydration import init_app as init_smart_hydration
        init_smart_hydration(app)
        print("Smart Hydration feature initialized")
    except Exception as e:
        import traceback
        print(f"Error initializing Smart Hydration feature: {e}")
        traceback.print_exc()

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Check if we need to initialize data
        if not DrinkType.query.first():
            # Create default drink types
            create_default_drink_types()

            # Create demo user
            create_demo_user()

        # Initialize food categories and items
        if not FoodCategory.query.first():
            create_default_food_categories()
            create_sample_food_items()

# OAuth Consent Screen Pages
@app.route('/privacy')
def privacy():
    """Privacy policy page for OAuth consent"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Terms of service page for OAuth consent"""
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)

