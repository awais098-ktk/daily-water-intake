#!/usr/bin/env python3
"""
Test script to verify minimal Flask app works
"""

import sys
import os

def test_minimal_flask():
    """Test if basic Flask functionality works"""
    print("Testing minimal Flask setup...")
    
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        import requests

        # Test gunicorn import (optional for local testing)
        try:
            import gunicorn
            print("✅ Gunicorn available")
        except ImportError:
            print("⚠️  Gunicorn not available locally (OK for development)")
        
        print("✅ All minimal dependencies imported successfully")
        
        # Create a test Flask app
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        db = SQLAlchemy(app)
        login_manager = LoginManager(app)
        
        @app.route('/')
        def hello():
            return "Hello from Water Tracker!"
        
        print("✅ Basic Flask app created successfully")
        print("✅ SQLAlchemy initialized")
        print("✅ Flask-Login initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal Flask test failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("🧪 Minimal Deployment Test")
    print("=" * 30)
    
    print(f"Python version: {sys.version}")
    print()
    
    success = test_minimal_flask()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 Minimal setup works! Ready for basic deployment.")
        return 0
    else:
        print("❌ Minimal setup failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
