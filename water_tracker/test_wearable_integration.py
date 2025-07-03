#!/usr/bin/env python3
"""
Comprehensive test for wearable integration functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from datetime import datetime, date
import json

def test_wearable_integration():
    """Test the wearable integration functionality"""
    print("=" * 60)
    print("TESTING WEARABLE INTEGRATION FUNCTIONALITY")
    print("=" * 60)
    
    with app.app_context():
        # Test 1: Check if wearable integration module is available
        try:
            from wearable_integration.models import WearableConnection, ActivityData, HydrationRecommendation
            from wearable_integration.fitness_apis import MockFitnessAPI
            from wearable_integration.activity_calculator import ActivityHydrationCalculator
            print("✅ Wearable integration modules imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import wearable integration modules: {e}")
            return False
        
        # Test 2: Check database tables creation
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Failed to create database tables: {e}")
            return False
        
        # Test 3: Test MockFitnessAPI
        try:
            mock_api = MockFitnessAPI()
            connection_test = mock_api.test_connection()
            if connection_test:
                print("✅ Mock fitness API connection test passed")
            else:
                print("❌ Mock fitness API connection test failed")
                return False
        except Exception as e:
            print(f"❌ Mock fitness API test failed: {e}")
            return False
        
        # Test 4: Test activity data generation
        try:
            test_date = datetime.now()
            activity_data = mock_api.get_activity_data(test_date)
            if activity_data and 'steps' in activity_data:
                print(f"✅ Activity data generated successfully: {activity_data['steps']} steps")
            else:
                print("❌ Failed to generate activity data")
                return False
        except Exception as e:
            print(f"❌ Activity data generation failed: {e}")
            return False
        
        # Test 5: Test ActivityHydrationCalculator
        try:
            calculator = ActivityHydrationCalculator(user_weight_kg=70)
            base_hydration = calculator.calculate_base_hydration()
            print(f"✅ Base hydration calculated: {base_hydration} ml")
            
            recommendation = calculator.calculate_total_recommendation(activity_data)
            print(f"✅ Total recommendation: {recommendation['total_recommendation']} ml")
            print(f"   Reasoning: {recommendation['reasoning']}")
            
            tips = calculator.get_hydration_tips(activity_data)
            print(f"✅ Hydration tips generated: {len(tips)} tips")
            for i, tip in enumerate(tips, 1):
                print(f"   {i}. {tip}")
                
        except Exception as e:
            print(f"❌ Activity hydration calculator test failed: {e}")
            return False
        
        # Test 6: Test database operations
        try:
            # Get demo user
            demo_user = User.query.filter_by(username='demo').first()
            if not demo_user:
                print("❌ Demo user not found!")
                return False
            
            # Create a mock wearable connection
            mock_connection = WearableConnection(
                user_id=demo_user.id,
                platform='mock',
                platform_user_id='test_user_123',
                access_token='test_token',
                is_active=True
            )
            db.session.add(mock_connection)
            db.session.commit()
            print("✅ Mock wearable connection created")
            
            # Create activity data
            activity_record = ActivityData(
                user_id=demo_user.id,
                connection_id=mock_connection.id,
                date=date.today(),
                **activity_data
            )
            db.session.add(activity_record)
            db.session.commit()
            print("✅ Activity data record created")
            
            # Create hydration recommendation
            hydration_rec = HydrationRecommendation(
                user_id=demo_user.id,
                activity_data_id=activity_record.id,
                date=date.today(),
                base_recommendation=recommendation['base_recommendation'],
                activity_bonus=recommendation['activity_bonus'],
                total_recommendation=recommendation['total_recommendation'],
                reasoning=recommendation['reasoning']
            )
            db.session.add(hydration_rec)
            db.session.commit()
            print("✅ Hydration recommendation created")
            
        except Exception as e:
            print(f"❌ Database operations test failed: {e}")
            return False
        
        print("✅ All wearable integration tests PASSED!")
        return True

def test_web_routes():
    """Test the wearable integration web routes"""
    print("\n" + "=" * 60)
    print("TESTING WEARABLE INTEGRATION WEB ROUTES")
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
        
        # Test wearable dashboard
        try:
            dashboard_response = client.get('/wearable/')
            print(f"Wearable dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Wearable dashboard accessible")
            else:
                print(f"❌ Wearable dashboard failed: {dashboard_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Wearable dashboard test failed: {e}")
            return False
        
        # Test connect page
        try:
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
        
        # Test mock connection
        try:
            mock_connect_response = client.get('/wearable/connect/mock', follow_redirects=True)
            print(f"Mock connection status: {mock_connect_response.status_code}")
            
            if mock_connect_response.status_code == 200:
                print("✅ Mock connection successful")
            else:
                print(f"❌ Mock connection failed: {mock_connect_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Mock connection test failed: {e}")
            return False
        
        # Test API endpoints
        try:
            activity_api_response = client.get('/wearable/api/activity-data?days=7')
            print(f"Activity API status: {activity_api_response.status_code}")
            
            if activity_api_response.status_code == 200:
                activity_data = activity_api_response.get_json()
                print(f"✅ Activity API successful: {len(activity_data.get('data', []))} records")
            else:
                print(f"❌ Activity API failed: {activity_api_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Activity API test failed: {e}")
            return False
        
        # Test hydration recommendation API
        try:
            hydration_api_response = client.get('/wearable/api/hydration-recommendation')
            print(f"Hydration API status: {hydration_api_response.status_code}")
            
            if hydration_api_response.status_code == 200:
                hydration_data = hydration_api_response.get_json()
                if hydration_data.get('success'):
                    print(f"✅ Hydration API successful: {hydration_data.get('recommendation', {}).get('total_recommendation', 'N/A')} ml recommended")
                else:
                    print(f"⚠️  Hydration API returned no data: {hydration_data.get('message', 'Unknown')}")
            else:
                print(f"❌ Hydration API failed: {hydration_api_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Hydration API test failed: {e}")
            return False
        
        print("✅ All web route tests PASSED!")
        return True

def test_dashboard_integration():
    """Test that wearable integration appears on the main dashboard"""
    print("\n" + "=" * 60)
    print("TESTING DASHBOARD INTEGRATION")
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
        
        # Check dashboard for wearable integration
        try:
            dashboard_response = client.get('/dashboard')
            dashboard_html = dashboard_response.data.decode('utf-8')
            
            if 'Wearable Integration' in dashboard_html:
                print("✅ Wearable Integration feature card found on dashboard")
            else:
                print("❌ Wearable Integration feature card not found on dashboard")
                return False
            
            if 'bi-smartwatch' in dashboard_html:
                print("✅ Smartwatch icon found on dashboard")
            else:
                print("❌ Smartwatch icon not found on dashboard")
                return False
                
        except Exception as e:
            print(f"❌ Dashboard integration test failed: {e}")
            return False
        
        print("✅ Dashboard integration test PASSED!")
        return True

def main():
    """Run all wearable integration tests"""
    print("COMPREHENSIVE WEARABLE INTEGRATION TEST")
    print("Testing backend functionality, web routes, and dashboard integration")
    print()
    
    # Test backend functionality
    backend_success = test_wearable_integration()
    
    # Test web routes
    web_success = test_web_routes()
    
    # Test dashboard integration
    dashboard_success = test_dashboard_integration()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Backend Test: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    print(f"Web Routes Test: {'✅ PASSED' if web_success else '❌ FAILED'}")
    print(f"Dashboard Integration: {'✅ PASSED' if dashboard_success else '❌ FAILED'}")
    
    if backend_success and web_success and dashboard_success:
        print("\n🎉 ALL TESTS PASSED! Wearable integration is working correctly.")
        print("\nNext steps:")
        print("1. Start the Flask app: python water_tracker/run_app.py")
        print("2. Open browser to: http://127.0.0.1:8080/dashboard")
        print("3. Click on 'Wearables' feature card")
        print("4. Connect a demo device and test the functionality")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
