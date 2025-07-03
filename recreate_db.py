"""
Recreate database for Water Intake Tracker
This script deletes the existing database and creates a new one with the updated schema
"""

import os
import sys
import shutil
from datetime import datetime, timezone

def recreate_database():
    """
    Recreate the database with the updated schema
    """
    # Database path
    db_path = os.path.join('water_tracker', 'instance', 'water_tracker.db')
    
    # Backup the existing database
    if os.path.exists(db_path):
        backup_dir = os.path.join('water_tracker', 'instance', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = os.path.join(backup_dir, f"water_tracker_backup_{timestamp}.db")
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Backed up database to {backup_path}")
            
            # Delete the existing database
            os.remove(db_path)
            print(f"Deleted existing database at {db_path}")
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
    
    # Import the app to create a new database
    try:
        # Add the parent directory to the path so we can import the app
        sys.path.insert(0, os.path.abspath('.'))
        
        # Import the app
        from water_tracker.app import app, db, create_default_drink_types, create_demo_user
        
        # Create the database
        with app.app_context():
            print("Creating new database...")
            db.create_all()
            
            # Create default drink types
            create_default_drink_types()
            
            # Create demo user
            create_demo_user()
            
            print("Database created successfully!")
        
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == "__main__":
    success = recreate_database()
    if success:
        print("Database recreation completed successfully.")
        sys.exit(0)
    else:
        print("Database recreation failed.")
        sys.exit(1)
