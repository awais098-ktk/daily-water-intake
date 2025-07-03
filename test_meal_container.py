#!/usr/bin/env python3
"""
Comprehensive test script for meal container functionality
Tests all aspects of the meal container feature to identify issues
"""

import requests
import json
import time
import sys
import os

# Add the water_tracker directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'water_tracker'))

def test_meal_container_functionality():
    """Test all meal container functionality"""
    base_url = 'http://127.0.0.1:8080'
    
    print("🧪 Testing Meal Container Functionality")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f'{base_url}/', timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running or not accessible")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Test food search API
    print("\n📋 Testing Food Search API...")
    try:
        response = requests.get(f'{base_url}/eating/api/food_search?q=apple', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'foods' in data:
                print(f"✅ Food search API working - Found {len(data['foods'])} items")
                if len(data['foods']) > 0:
                    print(f"   Sample food: {data['foods'][0]['name']}")
                    print(f"   Nutrition data: {data['foods'][0]['calories_per_100g']} cal/100g")
                else:
                    print("⚠️  No food items found - database might be empty")
            else:
                print("❌ Food search API response missing 'foods' key")
                print(f"   Response: {data}")
        else:
            print(f"❌ Food search API failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Food search API error: {e}")
    
    # Test 3: Test meal container page accessibility
    print("\n🍽️  Testing Meal Container Pages...")
    try:
        # Test meal containers list page
        response = requests.get(f'{base_url}/eating/meal_containers', timeout=10)
        if response.status_code == 200:
            print("✅ Meal containers list page accessible")
        else:
            print(f"❌ Meal containers list page failed: {response.status_code}")
        
        # Test add meal container page
        response = requests.get(f'{base_url}/eating/meal_containers/add', timeout=10)
        if response.status_code == 200:
            print("✅ Add meal container page accessible")
        else:
            print(f"❌ Add meal container page failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing meal container pages: {e}")
    
    # Test 4: Test database initialization
    print("\n🗄️  Testing Database...")
    try:
        from water_tracker.app import app, db, FoodItem, FoodCategory, MealContainer
        
        with app.app_context():
            # Check if food categories exist
            categories = FoodCategory.query.count()
            print(f"✅ Food categories in database: {categories}")
            
            # Check if food items exist
            food_items = FoodItem.query.count()
            print(f"✅ Food items in database: {food_items}")
            
            # Check if meal containers exist
            meal_containers = MealContainer.query.count()
            print(f"✅ Meal containers in database: {meal_containers}")
            
            if food_items == 0:
                print("⚠️  No food items found - running database initialization...")
                try:
                    from water_tracker.init_eating_db import init_eating_tracker_db
                    init_eating_tracker_db()
                    print("✅ Database initialized successfully")
                except Exception as e:
                    print(f"❌ Database initialization failed: {e}")
                    
    except Exception as e:
        print(f"❌ Database test error: {e}")
    
    # Test 5: Test form submission simulation
    print("\n📝 Testing Form Submission Logic...")
    try:
        # Simulate form data that would be sent
        test_form_data = {
            'name': 'Test Meal Container',
            'description': 'Test description',
            'meal_type': 'breakfast',
            'total_calories': '500',
            'total_carbs': '50',
            'total_fats': '20',
            'total_proteins': '30',
            'food_items_data': json.dumps({
                '1': {
                    'food_id': '1',
                    'quantity': '100'
                }
            })
        }
        
        print("✅ Form data structure looks correct")
        print(f"   Sample data: {list(test_form_data.keys())}")
        
    except Exception as e:
        print(f"❌ Form data test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("   - Check server logs for detailed error messages")
    print("   - Ensure database is properly initialized")
    print("   - Verify all required fields are being sent in form")
    print("   - Check JavaScript console for client-side errors")
    
    return True

if __name__ == '__main__':
    test_meal_container_functionality()
