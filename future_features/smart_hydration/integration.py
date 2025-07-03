"""
Integration module for Smart Hydration feature.
Shows how to integrate the feature with the main app.
"""

import os
from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import current_user, login_required
from .weather_api import WeatherAPI
from .hydration_calculator import HydrationCalculator

# Create Blueprint for smart hydration feature
smart_hydration_bp = Blueprint('smart_hydration', __name__, 
                              template_folder='templates',
                              static_folder='static',
                              url_prefix='/smart-hydration')

# Initialize weather API and hydration calculator
weather_api = None
hydration_calculator = None

def init_app(app):
    """Initialize the feature with the Flask app."""
    global weather_api, hydration_calculator
    
    # Get API key from app config or environment
    api_key = app.config.get('OPENWEATHERMAP_API_KEY') or os.environ.get('OPENWEATHERMAP_API_KEY')
    
    # Initialize components
    weather_api = WeatherAPI(api_key)
    hydration_calculator = HydrationCalculator(api_key)
    
    # Register blueprint
    app.register_blueprint(smart_hydration_bp)
    
    # Add weather widget to dashboard context
    @app.context_processor
    def inject_weather_widget():
        return {
            'show_weather_widget': True
        }

# API routes
@smart_hydration_bp.route('/api/weather', methods=['GET'])
@login_required
def get_weather():
    """API endpoint to get weather data."""
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    # Convert lat/lon to float if provided
    if lat is not None:
        try:
            lat = float(lat)
        except ValueError:
            return jsonify({'error': 'Invalid latitude'}), 400
    
    if lon is not None:
        try:
            lon = float(lon)
        except ValueError:
            return jsonify({'error': 'Invalid longitude'}), 400
    
    # Get weather data
    weather_data = weather_api.get_weather(city=city, lat=lat, lon=lon)
    
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'Could not fetch weather data'}), 500

@smart_hydration_bp.route('/api/hydration/recommendation', methods=['POST'])
@login_required
def get_hydration_recommendation():
    """API endpoint to get hydration recommendation."""
    data = request.json
    
    # Get user's base hydration from profile
    base_hydration = current_user.daily_goal if hasattr(current_user, 'daily_goal') else 2000
    
    # Get activity level from user profile or request
    activity_level = data.get('activity_level', 'low')
    
    # If weather data is provided directly
    if 'temperature' in data and 'humidity' in data:
        # Calculate adjustments directly
        temp_adjustment = hydration_calculator.calculate_temperature_adjustment(data.get('temperature'))
        humidity_adjustment = hydration_calculator.calculate_humidity_adjustment(data.get('humidity'))
        activity_adjustment = hydration_calculator.calculate_activity_adjustment(activity_level)
        
        # Calculate total recommendation (minimum 2000ml)
        total = max(base_hydration + temp_adjustment + humidity_adjustment + activity_adjustment, 2000)
        
        # Generate explanation
        explanation = hydration_calculator._generate_explanation(
            data.get('temperature'), 
            data.get('humidity'), 
            activity_level,
            temp_adjustment,
            humidity_adjustment,
            activity_adjustment
        )
        
        # Prepare recommendation data
        recommendation = {
            'base': base_hydration,
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'weather_condition': data.get('weather_condition'),
            'temp_adjustment': temp_adjustment,
            'humidity_adjustment': humidity_adjustment,
            'activity_adjustment': activity_adjustment,
            'total': total,
            'explanation': explanation
        }
        
        return jsonify(recommendation)
    
    # Otherwise, get recommendation from calculator
    city = data.get('city')
    lat = data.get('lat')
    lon = data.get('lon')
    
    # Convert lat/lon to float if provided
    if lat is not None:
        try:
            lat = float(lat)
        except ValueError:
            return jsonify({'error': 'Invalid latitude'}), 400
    
    if lon is not None:
        try:
            lon = float(lon)
        except ValueError:
            return jsonify({'error': 'Invalid longitude'}), 400
    
    # Get recommendation
    recommendation = hydration_calculator.get_recommendation(
        city=city, 
        lat=lat, 
        lon=lon, 
        activity_level=activity_level,
        base_hydration=base_hydration
    )
    
    return jsonify(recommendation)

@smart_hydration_bp.route('/api/user/update_goal', methods=['POST'])
@login_required
def update_daily_goal():
    """API endpoint to update user's daily goal."""
    data = request.json
    
    if 'daily_goal' not in data:
        return jsonify({'error': 'Missing daily_goal parameter'}), 400
    
    try:
        daily_goal = int(data['daily_goal'])
        if daily_goal < 500 or daily_goal > 10000:
            return jsonify({'error': 'Daily goal must be between 500 and 10000 ml'}), 400
        
        # Update user's daily goal
        current_user.daily_goal = daily_goal
        
        # Commit changes to database
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Daily goal updated successfully'})
    
    except ValueError:
        return jsonify({'error': 'Invalid daily goal value'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Template routes
@smart_hydration_bp.route('/widget')
@login_required
def weather_widget():
    """Route to render the weather widget template."""
    return render_template('weather_widget.html')

# How to include the widget in a template:
"""
{% if show_weather_widget %}
    <div id="weather-widget-container">
        {{ include_weather_widget() }}
    </div>
{% endif %}
"""

# Template function to include the widget
@smart_hydration_bp.app_template_global()
def include_weather_widget():
    """Template function to include the weather widget."""
    return render_template('weather_widget.html')
