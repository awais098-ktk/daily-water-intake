#!/bin/bash

# Azure App Service startup script for Flask application
echo "Starting Water Intake Tracker application..."

# Set environment variables for Flask
export FLASK_APP=water_tracker/app.py
export FLASK_ENV=production

# Create instance directory if it doesn't exist
mkdir -p instance

# Initialize database if needed (with error handling)
python -c "
try:
    from water_tracker.app import app, db
    with app.app_context():
        db.create_all()
        print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization skipped: {e}')
" || echo "Database initialization failed, continuing anyway..."

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 water_tracker.app:app
