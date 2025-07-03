"""
View database data for Water Intake Tracker
"""

import os
import sqlite3
import sys
from datetime import datetime

def view_database_data():
    """
    View the data in the database
    """
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False

    print(f"Viewing database at {db_path}...")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()

        # View users
        print("\n=== USERS ===")
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Password Hash: {user['password_hash']}")
            print(f"Daily Goal: {user['daily_goal']} {user['preferred_unit']}")
            print(f"Theme: {user['theme']}")
            print(f"Accent Color: {user['accent_color']}")
            print(f"Reminder Enabled: {user['reminder_enabled']}")
            print(f"Reminder Interval: {user['reminder_interval']} minutes")
            print(f"Join Date: {user['join_date']}")
            print(f"Gender: {user['gender']}")
            print(f"Avatar Path: {user['avatar_path']}")
            print("-" * 50)

        # View drink types
        print("\n=== DRINK TYPES ===")
        cursor.execute("SELECT * FROM drink_type")
        drink_types = cursor.fetchall()
        
        for drink_type in drink_types:
            print(f"ID: {drink_type['id']}")
            print(f"Name: {drink_type['name']}")
            print(f"Hydration Factor: {drink_type['hydration_factor']}")
            print(f"Color: {drink_type['color']}")
            print(f"Icon: {drink_type['icon']}")
            print("-" * 50)

        # View containers
        print("\n=== CONTAINERS ===")
        cursor.execute("""
            SELECT c.*, u.username, dt.name as drink_type_name 
            FROM container c
            JOIN user u ON c.user_id = u.id
            LEFT JOIN drink_type dt ON c.drink_type_id = dt.id
        """)
        containers = cursor.fetchall()
        
        for container in containers:
            print(f"ID: {container['id']}")
            print(f"Name: {container['name']}")
            print(f"Volume: {container['volume']} ml")
            print(f"Image Path: {container['image_path']}")
            print(f"Created At: {container['created_at']}")
            print(f"User: {container['username']} (ID: {container['user_id']})")
            print(f"Drink Type: {container['drink_type_name']} (ID: {container['drink_type_id']})")
            print("-" * 50)

        # View recent water logs
        print("\n=== RECENT WATER LOGS (Last 10) ===")
        cursor.execute("""
            SELECT wl.*, u.username, dt.name as drink_type_name, c.name as container_name
            FROM water_log wl
            JOIN user u ON wl.user_id = u.id
            LEFT JOIN drink_type dt ON wl.drink_type_id = dt.id
            LEFT JOIN container c ON wl.container_id = c.id
            ORDER BY wl.timestamp DESC
            LIMIT 10
        """)
        logs = cursor.fetchall()
        
        for log in logs:
            print(f"ID: {log['id']}")
            print(f"Amount: {log['amount']} ml")
            print(f"Timestamp: {log['timestamp']}")
            print(f"User: {log['username']} (ID: {log['user_id']})")
            print(f"Drink Type: {log['drink_type_name']} (ID: {log['drink_type_id']})")
            print(f"Container: {log['container_name']} (ID: {log['container_id']})")
            print(f"Input Method: {log['input_method']}")
            print(f"Notes: {log['notes']}")
            print("-" * 50)

        conn.close()
        return True

    except Exception as e:
        print(f"Error viewing database: {e}")
        return False

if __name__ == "__main__":
    success = view_database_data()
    if success:
        print("Database view completed successfully.")
    else:
        print("Failed to view database data.")
        sys.exit(1)
