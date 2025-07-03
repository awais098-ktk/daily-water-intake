#!/usr/bin/env python3
"""
Complete API Testing Script for Water Intake Tracker
Run this script to test all available API endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta

class WaterTrackerAPITester:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in = False
        
    def login(self, username="demo", password="demo123"):
        """Login to the application"""
        print("🔐 Testing Login...")
        
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        
        if response.status_code == 200 and "dashboard" in response.url:
            print("✅ Login successful")
            self.logged_in = True
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def test_progress_api(self):
        """Test progress API"""
        print("\n📊 Testing Progress API...")
        
        response = self.session.get(f"{self.base_url}/api/progress")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Progress API successful")
            print(f"   Total intake: {data.get('total_intake', 0)}ml")
            print(f"   Daily goal: {data.get('daily_goal', 0)}ml")
            print(f"   Progress: {data.get('progress_percentage', 0)}%")
            return data
        else:
            print(f"❌ Progress API failed: {response.status_code}")
            return None
    
    def test_water_data_api(self):
        """Test water data API"""
        print("\n📈 Testing Water Data API...")
        
        response = self.session.get(f"{self.base_url}/api/water-data")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Water Data API successful")
            print(f"   Data points: {len(data.get('data', []))}")
            return data
        else:
            print(f"❌ Water Data API failed: {response.status_code}")
            return None
    
    def test_voice_processing_api(self):
        """Test voice processing API"""
        print("\n🎤 Testing Voice Processing API...")
        
        test_phrases = [
            "I drank 500ml of water",
            "Had 250ml coffee",
            "Drank a glass of juice",
            "350ml pepsi can"
        ]
        
        for phrase in test_phrases:
            voice_data = {"text": phrase}
            response = self.session.post(f"{self.base_url}/api/process_voice", json=voice_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    print(f"✅ '{phrase}' → {result.get('volume')} of {result.get('drink_type')}")
                else:
                    print(f"❌ Voice processing failed for '{phrase}'")
            else:
                print(f"❌ Voice API failed: {response.status_code}")
    
    def test_barcode_api(self):
        """Test barcode lookup API"""
        print("\n📱 Testing Barcode API...")
        
        test_barcodes = [
            "8901030895559",  # Example barcode
            "0123456789012",  # Another example
        ]
        
        for barcode in test_barcodes:
            barcode_data = {"barcode": barcode}
            response = self.session.post(f"{self.base_url}/api/lookup_barcode", json=barcode_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Barcode {barcode}: {data.get('message', 'Found')}")
            else:
                print(f"❌ Barcode API failed for {barcode}: {response.status_code}")
    
    def test_export_apis(self):
        """Test data export APIs"""
        print("\n📤 Testing Export APIs...")
        
        # Test export preview
        print("   Testing export preview...")
        export_data = {
            'start_date': '2025-06-01',
            'end_date': '2025-06-16'
        }
        
        response = self.session.post(f"{self.base_url}/api/export/preview", data=export_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                print(f"✅ Export preview successful")
                print(f"   Total volume: {stats.get('total_volume', 0)}ml")
                print(f"   Total logs: {stats.get('total_logs', 0)}")
            else:
                print(f"❌ Export preview failed: {data.get('error')}")
        else:
            print(f"❌ Export preview failed: {response.status_code}")
        
        # Test export debug
        print("   Testing export debug...")
        response = self.session.get(f"{self.base_url}/api/test-export-debug")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Export debug successful")
                print(f"   CSV length: {data.get('csv_length', 0)} bytes")
            else:
                print(f"❌ Export debug failed: {data.get('error')}")
        else:
            print(f"❌ Export debug failed: {response.status_code}")
    
    def test_smart_hydration_apis(self):
        """Test smart hydration APIs"""
        print("\n🌤️ Testing Smart Hydration APIs...")
        
        # Test weather API
        print("   Testing weather API...")
        params = {'city': 'Lahore'}
        response = self.session.get(f"{self.base_url}/smart-hydration/api/weather", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Weather API successful")
            print(f"   Temperature: {data.get('temperature', 'N/A')}°C")
            print(f"   Humidity: {data.get('humidity', 'N/A')}%")
        else:
            print(f"❌ Weather API failed: {response.status_code}")
        
        # Test hydration recommendation
        print("   Testing hydration recommendation...")
        hydration_data = {
            "temperature": 30,
            "humidity": 70,
            "weather_condition": "sunny"
        }
        
        response = self.session.post(f"{self.base_url}/smart-hydration/api/hydration/recommendation", json=hydration_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Hydration recommendation successful")
            print(f"   Recommended: {data.get('total', 0)}ml")
        else:
            print(f"❌ Hydration recommendation failed: {response.status_code}")
    
    def test_wearable_apis(self):
        """Test wearable integration APIs"""
        print("\n🏃‍♂️ Testing Wearable APIs...")
        
        # Test activity data
        print("   Testing activity data...")
        params = {'days': 7}
        response = self.session.get(f"{self.base_url}/wearable/api/activity-data", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                activity_data = data.get('data', [])
                print(f"✅ Activity data successful")
                print(f"   Activity records: {len(activity_data)}")
            else:
                print(f"❌ Activity data failed: {data.get('message')}")
        else:
            print(f"❌ Activity data failed: {response.status_code}")
        
        # Test hydration recommendation
        print("   Testing wearable hydration recommendation...")
        params = {'date': datetime.now().strftime('%Y-%m-%d')}
        response = self.session.get(f"{self.base_url}/wearable/api/hydration-recommendation", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Wearable hydration recommendation successful")
                recommendation = data.get('recommendation', {})
                print(f"   Recommended: {recommendation.get('total_recommendation', 0)}ml")
            else:
                print(f"ℹ️ No activity data available: {data.get('message')}")
        else:
            print(f"❌ Wearable hydration recommendation failed: {response.status_code}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Water Intake Tracker API Tests")
        print("=" * 50)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return
        
        # Run all tests
        self.test_progress_api()
        self.test_water_data_api()
        self.test_voice_processing_api()
        self.test_barcode_api()
        self.test_export_apis()
        self.test_smart_hydration_apis()
        self.test_wearable_apis()
        
        print("\n" + "=" * 50)
        print("🎉 API Testing Complete!")

if __name__ == "__main__":
    # Create tester instance
    tester = WaterTrackerAPITester()
    
    # Run all tests
    tester.run_all_tests()
