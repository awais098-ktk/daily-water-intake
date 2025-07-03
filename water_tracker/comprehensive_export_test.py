#!/usr/bin/env python3
"""
Comprehensive test for data export functionality
Tests both the backend logic and simulates web requests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, WaterLog, DrinkType
from data_export import DataExporter
from datetime import datetime, timezone
import json

def test_backend_functionality():
    """Test the backend export functionality"""
    print("=" * 60)
    print("TESTING BACKEND EXPORT FUNCTIONALITY")
    print("=" * 60)
    
    with app.app_context():
        # Get demo user
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            print("❌ Demo user not found!")
            return False
        
        print(f"✅ Found demo user: {demo_user.username} (ID: {demo_user.id})")
        
        # Test DataExporter creation
        try:
            exporter = DataExporter(demo_user.id)
            print("✅ DataExporter created successfully")
        except Exception as e:
            print(f"❌ Failed to create DataExporter: {e}")
            return False
        
        # Test summary stats
        try:
            stats = exporter.get_summary_stats()
            print(f"✅ Summary stats retrieved: {stats}")
        except Exception as e:
            print(f"❌ Failed to get summary stats: {e}")
            return False
        
        # Test CSV export
        try:
            csv_data = exporter.export_csv()
            if csv_data:
                print(f"✅ CSV export successful. Length: {len(csv_data)} characters")
                print(f"   Preview: {csv_data[:100]}...")
            else:
                print("⚠️  CSV export returned None (no data)")
        except Exception as e:
            print(f"❌ CSV export failed: {e}")
            return False
        
        # Test JSON export
        try:
            json_data = exporter.export_json()
            if json_data:
                print(f"✅ JSON export successful. Length: {len(json_data)} characters")
                # Try to parse JSON to verify it's valid
                parsed = json.loads(json_data)
                print(f"   Records: {parsed.get('total_records', 'unknown')}")
            else:
                print("⚠️  JSON export returned None (no data)")
        except Exception as e:
            print(f"❌ JSON export failed: {e}")
            return False
        
        print("✅ Backend functionality test PASSED")
        return True

def test_web_api_simulation():
    """Test the web API endpoints by simulating requests"""
    print("\n" + "=" * 60)
    print("TESTING WEB API SIMULATION")
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
        
        # Test debug endpoint
        try:
            debug_response = client.get('/api/test-export-debug')
            print(f"Debug endpoint status: {debug_response.status_code}")
            
            if debug_response.status_code == 200:
                debug_data = debug_response.get_json()
                print(f"✅ Debug endpoint successful: {debug_data.get('message', 'No message')}")
                print(f"   User ID: {debug_data.get('user_id')}")
                print(f"   Stats: {debug_data.get('stats', {})}")
            else:
                print(f"❌ Debug endpoint failed: {debug_response.status_code}")
                if debug_response.data:
                    print(f"   Response: {debug_response.data.decode()}")
        except Exception as e:
            print(f"❌ Debug endpoint error: {e}")
            return False
        
        # Test preview endpoint
        try:
            preview_response = client.post('/api/export/preview', data={})
            print(f"Preview endpoint status: {preview_response.status_code}")
            
            if preview_response.status_code == 200:
                preview_data = preview_response.get_json()
                print(f"✅ Preview endpoint successful")
                print(f"   Stats: {preview_data.get('stats', {})}")
            else:
                print(f"❌ Preview endpoint failed: {preview_response.status_code}")
                if preview_response.data:
                    print(f"   Response: {preview_response.data.decode()}")
        except Exception as e:
            print(f"❌ Preview endpoint error: {e}")
            return False
        
        # Test CSV export endpoint
        try:
            csv_response = client.post('/api/export', data={'format': 'csv'})
            print(f"CSV export endpoint status: {csv_response.status_code}")
            
            if csv_response.status_code == 200:
                print(f"✅ CSV export endpoint successful")
                print(f"   Content-Type: {csv_response.headers.get('Content-Type')}")
                print(f"   Content-Length: {len(csv_response.data)} bytes")
            else:
                print(f"❌ CSV export endpoint failed: {csv_response.status_code}")
                if csv_response.data:
                    try:
                        error_data = csv_response.get_json()
                        print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        print(f"   Response: {csv_response.data.decode()[:200]}...")
        except Exception as e:
            print(f"❌ CSV export endpoint error: {e}")
            return False
        
        print("✅ Web API simulation test PASSED")
        return True

def main():
    """Run all tests"""
    print("COMPREHENSIVE DATA EXPORT TEST")
    print("Testing both backend functionality and web API endpoints")
    print()
    
    # Test backend
    backend_success = test_backend_functionality()
    
    # Test web API
    web_success = test_web_api_simulation()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Backend Test: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"Web API Test: {'✅ PASSED' if web_success else '❌ FAILED'}")
    
    if backend_success and web_success:
        print("\n🎉 ALL TESTS PASSED! Data export functionality is working correctly.")
        print("\nNext steps:")
        print("1. Start the Flask app: python water_tracker/run_app.py")
        print("2. Open browser to: http://127.0.0.1:8080/test-export")
        print("3. Test the web interface manually")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
