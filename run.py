"""
Launcher script for Water Intake Tracker
"""

import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app and required components
from water_tracker.app import app, db, create_default_drink_types, create_demo_user

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs(os.path.join('water_tracker', 'static', 'uploads'), exist_ok=True)
    os.makedirs(os.path.join('water_tracker', 'static', 'uploads', 'containers'), exist_ok=True)
    os.makedirs(os.path.join('water_tracker', 'static', 'uploads', 'avatars'), exist_ok=True)

    # Initialize the database if it doesn't exist
    with app.app_context():
        db_path = os.path.join('water_tracker', 'water_tracker.db')
        if not os.path.exists(db_path):
            print("Initializing database...")
            db.create_all()
            create_default_drink_types()
            create_demo_user()
            print("Database initialized successfully!")

    # Run the app
    app.run(debug=True, host='127.0.0.1', port=8080)
