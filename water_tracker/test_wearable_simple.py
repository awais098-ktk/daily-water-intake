#!/usr/bin/env python3
"""
Simple test for wearable integration web routes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_wearable_routes():
    """Test the wearable integration web routes"""
    print("=" * 60)
    print("TESTING WEARABLE INTEGRATION WEB ROUTES")
    print("=" * 60)
    
    with app.test_client() as client:
        # Login as demo user
        print("Logging in as demo user...")
        login_response = client.post('/login', data={
            'username': 'demo',
            'password': 'demo123'
        }, follow_redirects=True)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed. Status: {login_response.status_code}")
            return False
        
        print("✅ Successfully logged in as demo user")
        
        # Test wearable dashboard
        try:
            print("Testing wearable dashboard...")
            dashboard_response = client.get('/wearable/')
            print(f"Wearable dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Wearable dashboard accessible")
                
                # Check if the response contains expected content
                response_text = dashboard_response.data.decode('utf-8')
                if 'Wearable Integration' in response_text:
                    print("✅ Dashboard contains wearable integration content")
                else:
                    print("⚠️  Dashboard missing expected content")
                    
            elif dashboard_response.status_code == 500:
                print("❌ Wearable dashboard failed with server error")
                # Try to get error details
                response_text = dashboard_response.data.decode('utf-8')
                if 'User' in response_text and 'failed to locate' in response_text:
                    print("   Error: SQLAlchemy relationship issue with User model")
                return False
            else:
                print(f"❌ Wearable dashboard failed: {dashboard_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Wearable dashboard test failed: {e}")
            return False
        
        # Test connect page
        try:
            print("Testing connect page...")
            connect_response = client.get('/wearable/connect')
            print(f"Connect page status: {connect_response.status_code}")
            
            if connect_response.status_code == 200:
                print("✅ Connect page accessible")
            else:
                print(f"❌ Connect page failed: {connect_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connect page test failed: {e}")
            return False
        
        print("✅ All web route tests PASSED!")
        return True

def main():
    """Run the simple wearable integration test"""
    print("SIMPLE WEARABLE INTEGRATION TEST")
    print("Testing web routes only")
    print()
    
    success = test_wearable_routes()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Web Routes Test: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 WEARABLE INTEGRATION IS WORKING!")
        print("\nYou can now:")
        print("1. Access the wearable dashboard at: http://127.0.0.1:8080/wearable/")
        print("2. Connect demo devices for testing")
        print("3. View activity-based hydration recommendations")
        return True
    else:
        print("\n❌ Wearable integration has issues. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
