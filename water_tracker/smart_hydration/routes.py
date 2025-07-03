"""
Routes module for Smart Hydration feature.
Defines API endpoints and template routes.
"""

import os
import requests
from datetime import datetime, timedelta
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

    # Hardcode the API key for reliability
    api_key = '6c5688794c42581bb9715872c8d98449'

    # Initialize components
    weather_api = WeatherAPI(api_key)
    hydration_calculator = HydrationCalculator(api_key)

    # Register blueprint
    app.register_blueprint(smart_hydration_bp)

    # Log successful initialization
    print(f"Smart Hydration initialized with API key: {api_key[:5]}...{api_key[-5:]}")

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
    city = request.args.get('city', 'New York')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    print(f"Weather API request received for city: {city}")

    # Try to get weather data from the API using the fixed approach
    try:
        # Use a well-known city like Lahore or Karachi as suggested
        if city == 'Pakistan':
            city = 'Lahore'
            print(f"Changed country name 'Pakistan' to city name 'Lahore'")

        # Get the API key
        api_key = current_app.config.get('OPENWEATHERMAP_API_KEY', '6c5688794c42581bb9715872c8d98449')

        # Construct the URL directly as recommended
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        print(f"Making request to: {url.replace(api_key, 'API_KEY')}")

        # Make the request
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            # Parse the response as JSON
            weather_data = response.json()
            print(f"Successfully fetched weather data for {city}")
            return jsonify(weather_data)
        else:
            print(f"Error fetching weather data: {response.text}")
            return jsonify({
                "error": "Weather API error",
                "message": f"Weather API error: {response.status_code}",
                "cod": response.status_code
            }), response.status_code

    except Exception as e:
        print(f"Exception fetching weather data: {e}")
        return jsonify({
            "error": "Weather API error",
            "message": str(e),
            "cod": 500
        }), 500



@smart_hydration_bp.route('/api/hydration/recommendation', methods=['POST'])
@login_required
def get_hydration_recommendation():
    """API endpoint to get hydration recommendation."""
    data = request.json

    print(f"Hydration recommendation request received: {data}")

    # Get user's base hydration from profile
    base_hydration = current_user.daily_goal if hasattr(current_user, 'daily_goal') else 2000

    # Get weather data from the request
    temperature = data.get('temperature', 25)
    humidity = data.get('humidity', 60)
    weather_condition = data.get('weather_condition', 'clear sky')

    # Calculate adjustments based on weather
    temp_adjustment = 0
    if temperature > 30:
        temp_adjustment = 300
    elif temperature > 25:
        temp_adjustment = 200
    elif temperature > 20:
        temp_adjustment = 100

    humidity_adjustment = 0
    if humidity > 80:
        humidity_adjustment = 100
    elif humidity > 60:
        humidity_adjustment = 50

    # Activity adjustment (mock)
    activity_adjustment = 100

    # Calculate total recommended hydration
    total = base_hydration + temp_adjustment + humidity_adjustment + activity_adjustment

    # Create recommendation response
    recommendation = {
        'base': base_hydration,
        'temperature': temperature,
        'humidity': humidity,
        'weather_condition': weather_condition,
        'temp_adjustment': temp_adjustment,
        'humidity_adjustment': humidity_adjustment,
        'activity_adjustment': activity_adjustment,
        'total': total,
        'explanation': f'Based on the current weather ({temperature}°C, {humidity}% humidity, {weather_condition}) and your activity level, we recommend drinking {total} ml of water today.'
    }

    print(f"Returning hydration recommendation: {recommendation}")
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

# Template function to include the widget
@smart_hydration_bp.app_template_global()
def include_weather_widget():
    """Template function to include the weather widget."""
    return render_template('weather_widget.html')
