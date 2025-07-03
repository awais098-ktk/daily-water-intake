# Feature Integration Guide

This guide explains how to integrate the future features into the main Water Intake Tracker application.

## General Integration Process

1. **Feature Selection**
   - Choose which feature to implement next based on priority and difficulty
   - Review the feature's README.md for implementation details

2. **Dependencies Installation**
   - Install required dependencies from the feature's requirements.txt
   - Example: `pip install -r future_features/smart_hydration/requirements.txt`

3. **Code Integration**
   - Copy the feature's files to the appropriate locations in the main app
   - Import and initialize the feature in the main app

4. **Database Updates**
   - Apply any required database migrations
   - Initialize new tables if needed

5. **Testing**
   - Run the feature's tests to ensure proper functionality
   - Test integration with the main app

6. **UI Integration**
   - Add feature UI components to the appropriate templates
   - Update navigation and menus as needed

## Smart Hydration Integration

### Step 1: Install Dependencies
```bash
pip install -r future_features/smart_hydration/requirements.txt
```

### Step 2: Add API Key
Add your OpenWeatherMap API key to the app configuration:
```python
# In app.py or config.py
app.config['OPENWEATHERMAP_API_KEY'] = 'your_api_key_here'
```

### Step 3: Initialize the Feature
```python
# In app.py
from future_features.smart_hydration import init_app as init_smart_hydration

# Initialize the feature
init_smart_hydration(app)
```

### Step 4: Add Weather Widget to Dashboard
In your dashboard.html template, add:
```html
{% if show_weather_widget %}
    <div id="weather-widget-container">
        {{ include_weather_widget() }}
    </div>
{% endif %}
```

### Step 5: Include JavaScript
In your base template or dashboard template:
```html
<script src="{{ url_for('static', filename='js/weather_widget.js') }}"></script>
```

## Wearable Integration

### Step 1: Install Dependencies
```bash
pip install -r future_features/wearable_integration/requirements.txt
```

### Step 2: Add API Credentials
Add your Google Fit and Fitbit API credentials to the app configuration.

### Step 3: Initialize the Feature
```python
# In app.py
from future_features.wearable_integration import init_app as init_wearable

# Initialize the feature
init_wearable(app)
```

### Step 4: Add Connection UI to Settings
In your settings.html template, add the wearable connection section.

## Barcode Scanner Integration

### Step 1: Install Dependencies
```bash
pip install -r future_features/barcode_scanner/requirements.txt
```

### Step 2: Initialize the Feature
```python
# In app.py
from future_features.barcode_scanner import init_app as init_barcode_scanner

# Initialize the feature
init_barcode_scanner(app)
```

### Step 3: Add Scan Button to Dashboard
In your dashboard.html template, add the barcode scan button.

## Gamification Integration

### Step 1: Initialize the Feature
```python
# In app.py
from future_features.gamification import init_app as init_gamification

# Initialize the feature
init_gamification(app)
```

### Step 2: Add Achievements Tab to Profile
In your profile.html template, add the achievements section.

## Feature Flags

To enable/disable features easily, consider implementing feature flags:

```python
# In config.py
FEATURES = {
    'smart_hydration': True,
    'wearable_integration': False,
    'barcode_scanner': False,
    'gamification': True,
    'virtual_pet': False,
    'gesture_logging': False,
    'voice_assistant': False,
    'cloud_sync': False,
    'data_export': True,
    'urine_tracker': False,
    'smart_reminders': False
}

# In app.py
if app.config['FEATURES']['smart_hydration']:
    init_smart_hydration(app)

# In templates
{% if config.FEATURES.gamification %}
    <!-- Show gamification UI -->
{% endif %}
```

## Testing Integration

After integrating each feature, run the feature's tests:

```bash
python -m unittest discover -s future_features/smart_hydration
```

Also run the main app tests to ensure nothing was broken:

```bash
python -m unittest discover
```

## Troubleshooting

If you encounter issues during integration:

1. Check the feature's README.md for specific requirements
2. Ensure all dependencies are installed
3. Check for conflicts with existing code
4. Review the app logs for error messages
5. Consult the feature's test files for usage examples
