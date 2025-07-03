#!/usr/bin/env python3
"""
Test script to verify Azure deployment readiness
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print(f"✅ Flask-SQLAlchemy {flask_sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        import flask_login
        print(f"✅ Flask-Login {flask_login.__version__}")
    except ImportError as e:
        print(f"❌ Flask-Login import failed: {e}")
        return False
    
    try:
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import matplotlib
        print(f"✅ Matplotlib {matplotlib.__version__}")
    except ImportError as e:
        print(f"❌ Matplotlib import failed: {e}")
        return False
    
    return True

def test_app_import():
    """Test if the main app can be imported"""
    print("\nTesting app import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        from water_tracker.app import app
        print("✅ App imported successfully")
        
        # Test app configuration
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Azure Deployment Readiness Test")
    print("=" * 40)
    
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    imports_ok = test_imports()
    app_ok = test_app_import()
    
    print("\n" + "=" * 40)
    if imports_ok and app_ok:
        print("🎉 All tests passed! Ready for Azure deployment.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
