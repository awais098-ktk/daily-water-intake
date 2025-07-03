"""
Test script for the Weather Widget
"""

from flask import Flask, render_template
from flask_login import LoginManager, UserMixin, login_user, current_user

# Create a simple Flask app
app = Flask(__name__,
            template_folder='water_tracker/templates',
            static_folder='water_tracker/static')
app.config['SECRET_KEY'] = 'test_secret_key'

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Create a simple User class
class User(UserMixin):
    def __init__(self, id, username, daily_goal=2000):
        self.id = id
        self.username = username
        self.daily_goal = daily_goal

# Create a demo user
demo_user = User(1, 'demo')

@login_manager.user_loader
def load_user(user_id):
    if int(user_id) == 1:
        return demo_user
    return None

@app.route('/')
def index():
    # Auto-login the demo user
    login_user(demo_user)
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather Widget Test</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            body { padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">Weather Widget Test</h1>
            """ + render_template('weather_widget.html') + """
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="/static/js/smart_hydration/direct_fix_weather.js"></script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5001)
