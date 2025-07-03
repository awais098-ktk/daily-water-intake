#!/usr/bin/env python3
"""
Simple script to run the Flask app
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app import app

if __name__ == '__main__':
    print("Starting Water Intake Tracker Flask App...")
    print("Access the app at: http://127.0.0.1:8080")
    print("Test export page at: http://127.0.0.1:8080/test-export")
    print("Debug API at: http://127.0.0.1:8080/api/test-export-debug")
    
    app.run(host='127.0.0.1', port=8080, debug=True)
