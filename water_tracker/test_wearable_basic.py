#!/usr/bin/env python3
"""
Basic test for wearable integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_basic_functionality():
    """Test basic wearable integration functionality"""
    print("=" * 60)
    print("TESTING BASIC WEARABLE INTEGRATION")
    print("=" * 60)
    
    with app.app_context():
        # Test 1: Check if models are available
        try:
            from app import WearableConnection, ActivityData, HydrationRecommendation
            print("✅ Wearable models imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import wearable models: {e}")
            return False
        
        # Test 2: Check if database tables can be created
        try:
            from app import db
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Failed to create database tables: {e}")
            return False
        
        # Test 3: Test fitness APIs
        try:
            from wearable_integration.fitness_apis import MockFitnessAPI
            from wearable_integration.activity_calculator import ActivityHydrationCalculator
            
            mock_api = MockFitnessAPI()
            if mock_api.test_connection():
                print("✅ Mock fitness API working")
            else:
                print("❌ Mock fitness API failed")
                return False
                
            calculator = ActivityHydrationCalculator()
            base_hydration = calculator.calculate_base_hydration()
            print(f"✅ Activity calculator working: {base_hydration} ml base hydration")
            
        except Exception as e:
            print(f"❌ Fitness API test failed: {e}")
            return False
        
        print("✅ Basic functionality test PASSED!")
        return True

def test_web_access():
    """Test basic web access to wearable pages"""
    print("\n" + "=" * 60)
    print("TESTING WEB ACCESS")
    print("=" * 60)
    
    with app.test_client() as client:
        # Login as demo user
        login_response = client.post('/login', data={
            'username': 'demo',
            'password': 'demo123'
        }, follow_redirects=True)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed. Status: {login_response.status_code}")
            return False
        
        print("✅ Successfully logged in as demo user")
        
        # Test connect page (should work since it doesn't use models)
        try:
            connect_response = client.get('/wearable/connect')
            print(f"Connect page status: {connect_response.status_code}")
            
            if connect_response.status_code == 200:
                print("✅ Connect page accessible")
                return True
            else:
                print(f"❌ Connect page failed: {connect_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connect page test failed: {e}")
            return False

def main():
    """Run basic wearable integration tests"""
    print("BASIC WEARABLE INTEGRATION TEST")
    print("Testing core functionality and basic web access")
    print()
    
    # Test basic functionality
    basic_success = test_basic_functionality()
    
    # Test web access
    web_success = test_web_access()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Basic Functionality: {'✅ PASSED' if basic_success else '❌ FAILED'}")
    print(f"Web Access: {'✅ PASSED' if web_success else '❌ FAILED'}")
    
    if basic_success and web_success:
        print("\n🎉 BASIC WEARABLE INTEGRATION IS WORKING!")
        print("\nNext steps:")
        print("1. The wearable integration models are properly defined")
        print("2. The connect page is accessible")
        print("3. You can now work on fixing the remaining route issues")
        return True
    else:
        print("\n❌ Some basic functionality is not working.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
