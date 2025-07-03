#!/usr/bin/env python3
"""
Test script for data export functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, WaterLog, DrinkType
from data_export import DataExporter
from datetime import datetime, timezone

def test_export():
    """Test the data export functionality"""
    with app.app_context():
        # Get the demo user
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            print("Demo user not found. Please create a demo user first.")
            return False
        
        print(f"Testing export for user: {demo_user.username} (ID: {demo_user.id})")

        # Add some test data if none exists
        existing_logs = WaterLog.query.filter_by(user_id=demo_user.id).count()
        if existing_logs == 0:
            print("No existing data found. Adding test data...")

            # Get water drink type
            water_type = DrinkType.query.filter_by(name='Water').first()
            if not water_type:
                print("Water drink type not found!")
                return False

            # Add some test water logs
            test_logs = [
                WaterLog(
                    user_id=demo_user.id,
                    amount=500,
                    drink_type_id=water_type.id,
                    timestamp=datetime.now(timezone.utc),
                    input_method='manual'
                ),
                WaterLog(
                    user_id=demo_user.id,
                    amount=250,
                    drink_type_id=water_type.id,
                    timestamp=datetime.now(timezone.utc),
                    input_method='manual'
                ),
                WaterLog(
                    user_id=demo_user.id,
                    amount=350,
                    drink_type_id=water_type.id,
                    timestamp=datetime.now(timezone.utc),
                    input_method='manual'
                )
            ]

            for log in test_logs:
                db.session.add(log)

            db.session.commit()
            print(f"Added {len(test_logs)} test water logs")
        else:
            print(f"Found {existing_logs} existing water logs")

        try:
            # Create exporter
            exporter = DataExporter(demo_user.id)
            print("DataExporter created successfully")
            
            # Test getting summary stats
            stats = exporter.get_summary_stats()
            print(f"Summary stats: {stats}")
            
            # Test CSV export
            csv_data = exporter.export_csv()
            if csv_data:
                print(f"CSV export successful. Length: {len(csv_data)} characters")
                print("First 200 characters of CSV:")
                print(csv_data[:200])
            else:
                print("CSV export returned None (no data)")
            
            # Test JSON export
            json_data = exporter.export_json()
            if json_data:
                print(f"JSON export successful. Length: {len(json_data)} characters")
            else:
                print("JSON export returned None (no data)")
            
            print("All tests passed!")
            return True
            
        except Exception as e:
            print(f"Error during export test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_export()
    sys.exit(0 if success else 1)
