#!/usr/bin/env python3
"""
Database initialization script for the eating tracker tables.
Run this script to create all the new eating tracker tables.
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from water_tracker.app import app, db
from water_tracker.app import (
    FoodCategory, FoodItem, NutritionGoals, 
    MealContainer, MealContainerItem, MealLog
)

def init_eating_tracker_db():
    """Initialize the eating tracker database tables and sample data"""
    
    with app.app_context():
        print("Creating eating tracker database tables...")
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if we already have sample data
        if FoodCategory.query.first():
            print("✓ Sample data already exists, skipping initialization")
            return
        
        print("Adding sample food categories...")
        
        # Create food categories
        categories = [
            {'name': 'Fruits', 'color': '#FF6B6B', 'icon': 'apple'},
            {'name': 'Vegetables', 'color': '#4ECDC4', 'icon': 'carrot'},
            {'name': 'Grains', 'color': '#45B7D1', 'icon': 'grain'},
            {'name': 'Proteins', 'color': '#96CEB4', 'icon': 'egg'},
            {'name': 'Dairy', 'color': '#FFEAA7', 'icon': 'milk'},
            {'name': 'Nuts & Seeds', 'color': '#DDA0DD', 'icon': 'nut'},
            {'name': 'Beverages', 'color': '#74B9FF', 'icon': 'cup'},
            {'name': 'Snacks', 'color': '#FD79A8', 'icon': 'cookie'},
            {'name': 'Condiments', 'color': '#FDCB6E', 'icon': 'bottle'},
            {'name': 'Other', 'color': '#6C5CE7', 'icon': 'question-circle'}
        ]
        
        for cat_data in categories:
            category = FoodCategory(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        print("✓ Food categories created!")
        
        print("Adding sample food items...")
        
        # Get category IDs
        fruits_cat = FoodCategory.query.filter_by(name='Fruits').first()
        vegetables_cat = FoodCategory.query.filter_by(name='Vegetables').first()
        grains_cat = FoodCategory.query.filter_by(name='Grains').first()
        proteins_cat = FoodCategory.query.filter_by(name='Proteins').first()
        dairy_cat = FoodCategory.query.filter_by(name='Dairy').first()
        
        # Get more category IDs
        nuts_cat = FoodCategory.query.filter_by(name='Nuts & Seeds').first()
        snacks_cat = FoodCategory.query.filter_by(name='Snacks').first()
        beverages_cat = FoodCategory.query.filter_by(name='Beverages').first()
        other_cat = FoodCategory.query.filter_by(name='Other').first()

        # Create sample food items with more variety
        food_items = [
            # Fruits
            {
                'name': 'Apple',
                'brand': 'Fresh',
                'category_id': fruits_cat.id,
                'calories_per_100g': 52,
                'carbs_per_100g': 14,
                'fats_per_100g': 0.2,
                'proteins_per_100g': 0.3,
                'fiber_per_100g': 2.4,
                'sugar_per_100g': 10.4,
                'sodium_per_100g': 1
            },
            {
                'name': 'Banana',
                'brand': 'Fresh',
                'category_id': fruits_cat.id,
                'calories_per_100g': 89,
                'carbs_per_100g': 23,
                'fats_per_100g': 0.3,
                'proteins_per_100g': 1.1,
                'fiber_per_100g': 2.6,
                'sugar_per_100g': 12.2,
                'sodium_per_100g': 1
            },
            {
                'name': 'Orange',
                'brand': 'Fresh',
                'category_id': fruits_cat.id,
                'calories_per_100g': 47,
                'carbs_per_100g': 12,
                'fats_per_100g': 0.1,
                'proteins_per_100g': 0.9,
                'fiber_per_100g': 2.4,
                'sugar_per_100g': 9.4,
                'sodium_per_100g': 0
            },
            # Vegetables
            {
                'name': 'Broccoli',
                'brand': 'Fresh',
                'category_id': vegetables_cat.id,
                'calories_per_100g': 34,
                'carbs_per_100g': 7,
                'fats_per_100g': 0.4,
                'proteins_per_100g': 2.8,
                'fiber_per_100g': 2.6,
                'sugar_per_100g': 1.5,
                'sodium_per_100g': 33
            },
            {
                'name': 'Carrot',
                'brand': 'Fresh',
                'category_id': vegetables_cat.id,
                'calories_per_100g': 41,
                'carbs_per_100g': 10,
                'fats_per_100g': 0.2,
                'proteins_per_100g': 0.9,
                'fiber_per_100g': 2.8,
                'sugar_per_100g': 4.7,
                'sodium_per_100g': 69
            },
            {
                'name': 'Spinach',
                'brand': 'Fresh',
                'category_id': vegetables_cat.id,
                'calories_per_100g': 23,
                'carbs_per_100g': 3.6,
                'fats_per_100g': 0.4,
                'proteins_per_100g': 2.9,
                'fiber_per_100g': 2.2,
                'sugar_per_100g': 0.4,
                'sodium_per_100g': 79
            },
            # Proteins
            {
                'name': 'Chicken Breast',
                'brand': 'Fresh',
                'category_id': proteins_cat.id,
                'calories_per_100g': 165,
                'carbs_per_100g': 0,
                'fats_per_100g': 3.6,
                'proteins_per_100g': 31,
                'fiber_per_100g': 0,
                'sugar_per_100g': 0,
                'sodium_per_100g': 74
            },
            {
                'name': 'Salmon',
                'brand': 'Fresh',
                'category_id': proteins_cat.id,
                'calories_per_100g': 208,
                'carbs_per_100g': 0,
                'fats_per_100g': 12,
                'proteins_per_100g': 25,
                'fiber_per_100g': 0,
                'sugar_per_100g': 0,
                'sodium_per_100g': 59
            },
            {
                'name': 'Eggs',
                'brand': 'Fresh',
                'category_id': proteins_cat.id,
                'calories_per_100g': 155,
                'carbs_per_100g': 1.1,
                'fats_per_100g': 11,
                'proteins_per_100g': 13,
                'fiber_per_100g': 0,
                'sugar_per_100g': 1.1,
                'sodium_per_100g': 124
            },
            # Grains
            {
                'name': 'Brown Rice',
                'brand': 'Generic',
                'category_id': grains_cat.id,
                'calories_per_100g': 111,
                'carbs_per_100g': 23,
                'fats_per_100g': 0.9,
                'proteins_per_100g': 2.6,
                'fiber_per_100g': 1.8,
                'sugar_per_100g': 0.4,
                'sodium_per_100g': 5
            },
            {
                'name': 'Oats',
                'brand': 'Generic',
                'category_id': grains_cat.id,
                'calories_per_100g': 389,
                'carbs_per_100g': 66,
                'fats_per_100g': 6.9,
                'proteins_per_100g': 17,
                'fiber_per_100g': 10.6,
                'sugar_per_100g': 0.99,
                'sodium_per_100g': 2
            },
            {
                'name': 'Whole Wheat Bread',
                'brand': 'Generic',
                'category_id': grains_cat.id,
                'calories_per_100g': 247,
                'carbs_per_100g': 41,
                'fats_per_100g': 4.2,
                'proteins_per_100g': 13,
                'fiber_per_100g': 6,
                'sugar_per_100g': 5.7,
                'sodium_per_100g': 491
            },
            # Dairy
            {
                'name': 'Greek Yogurt',
                'brand': 'Generic',
                'category_id': dairy_cat.id,
                'calories_per_100g': 59,
                'carbs_per_100g': 3.6,
                'fats_per_100g': 0.4,
                'proteins_per_100g': 10,
                'fiber_per_100g': 0,
                'sugar_per_100g': 3.6,
                'sodium_per_100g': 36
            },
            {
                'name': 'Milk',
                'brand': 'Generic',
                'category_id': dairy_cat.id,
                'calories_per_100g': 42,
                'carbs_per_100g': 5,
                'fats_per_100g': 1,
                'proteins_per_100g': 3.4,
                'fiber_per_100g': 0,
                'sugar_per_100g': 5,
                'sodium_per_100g': 44
            },
            # Nuts & Seeds
            {
                'name': 'Almonds',
                'brand': 'Generic',
                'category_id': nuts_cat.id,
                'calories_per_100g': 579,
                'carbs_per_100g': 22,
                'fats_per_100g': 50,
                'proteins_per_100g': 21,
                'fiber_per_100g': 12,
                'sugar_per_100g': 4.4,
                'sodium_per_100g': 1
            },
            {
                'name': 'Peanut Butter',
                'brand': 'Generic',
                'category_id': nuts_cat.id,
                'calories_per_100g': 588,
                'carbs_per_100g': 20,
                'fats_per_100g': 50,
                'proteins_per_100g': 25,
                'fiber_per_100g': 6,
                'sugar_per_100g': 9.2,
                'sodium_per_100g': 17
            },
            # Potato (should be in vegetables but let's add it)
            {
                'name': 'Potato',
                'brand': 'Fresh',
                'category_id': vegetables_cat.id,
                'calories_per_100g': 77,
                'carbs_per_100g': 17,
                'fats_per_100g': 0.1,
                'proteins_per_100g': 2,
                'fiber_per_100g': 2.2,
                'sugar_per_100g': 0.8,
                'sodium_per_100g': 6
            }
        ]
        
        for food_data in food_items:
            food_item = FoodItem(**food_data)
            db.session.add(food_item)
        
        db.session.commit()
        print("✓ Sample food items created!")
        
        print("\n🎉 Eating tracker database initialization complete!")
        print("You can now use the eating tracker features.")

if __name__ == '__main__':
    init_eating_tracker_db()
