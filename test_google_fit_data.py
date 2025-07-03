#!/usr/bin/env python3
"""
Test script to debug Google Fit data retrieval
"""

import os
import sys
from datetime import datetime, date, timedelta
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_google_fit_data():
    """Test Google Fit data retrieval with real connection"""
    try:
        # Import after setting up path
        from water_tracker.app import app
        from water_tracker.wearable_integration.fitness_apis import GoogleFitAPI
        from water_tracker.wearable_integration.models import WearableConnection

        print("🔍 Testing Google Fit Data Retrieval")
        print("=" * 50)
        
        with app.app_context():
            # Find an active Google Fit connection
            connection = WearableConnection.query.filter_by(
                platform='google_fit',
                is_active=True
            ).first()
            
            if not connection:
                print("❌ No active Google Fit connection found")
                print("Please connect Google Fit first through the web interface")
                return False
            
            print(f"✅ Found Google Fit connection for user {connection.user_id}")
            print(f"   Platform User ID: {connection.platform_user_id}")
            print(f"   Connected: {connection.connected_at}")
            
            # Create API instance
            api = GoogleFitAPI(connection.access_token, connection.refresh_token)
            
            # Test connection
            print("\n🔗 Testing API Connection...")
            if api.test_connection():
                print("✅ Google Fit API connection successful")
            else:
                print("❌ Google Fit API connection failed")
                return False
            
            # Test user profile
            print("\n👤 Testing User Profile...")
            profile = api.get_user_profile()
            print(f"✅ User Profile: {profile}")
            
            # List available data sources
            print("\n📊 Listing Available Data Sources...")
            data_sources = api.list_data_sources()
            print(f"✅ Found {len(data_sources)} data sources")
            
            # Test activity data for today and yesterday
            print("\n📈 Testing Activity Data Retrieval...")
            test_dates = [
                date.today(),
                date.today() - timedelta(days=1),
                date.today() - timedelta(days=2)
            ]
            
            for test_date in test_dates:
                print(f"\n📅 Testing data for {test_date}...")
                activity_data = api.get_activity_data(datetime.combine(test_date, datetime.min.time()))
                
                if activity_data:
                    print(f"✅ Activity data retrieved:")
                    print(f"   Steps: {activity_data.get('steps', 0)}")
                    print(f"   Distance: {activity_data.get('distance_meters', 0):.1f}m")
                    print(f"   Calories: {activity_data.get('calories_burned', 0)}")
                    print(f"   Active Minutes: {activity_data.get('active_minutes', 0)}")
                    print(f"   Heart Rate Avg: {activity_data.get('heart_rate_avg', 'N/A')}")
                    
                    if activity_data.get('steps', 0) > 0:
                        print("🎉 Real data found!")
                    else:
                        print("⚠️  No steps data - might be no activity or data source issue")
                else:
                    print("❌ No activity data retrieved")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_google_fit_data()
    if success:
        print("\n🎉 Google Fit data test completed!")
    else:
        print("\n💥 Google Fit data test failed!")
