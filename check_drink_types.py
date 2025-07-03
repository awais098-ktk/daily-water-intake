"""
Check drink types in the Water Intake Tracker database
"""

import os
import sys
import sqlite3

def check_drink_types():
    """
    Check the drink types in the database
    """
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    print(f"Checking drink types in database at {db_path}...")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all drink types
        cursor.execute("SELECT id, name, hydration_factor, color, icon FROM drink_type ORDER BY id")
        drink_types = cursor.fetchall()
        
        print("Drink types in the database:")
        print("ID | Name | Hydration Factor | Color | Icon")
        print("-" * 60)
        for drink_type in drink_types:
            print(f"{drink_type[0]} | {drink_type[1]} | {drink_type[2]} | {drink_type[3]} | {drink_type[4]}")
        
        # Check containers using each drink type
        print("\nContainers by drink type:")
        for drink_type in drink_types:
            cursor.execute("""
                SELECT c.id, c.name, c.volume, c.image_path
                FROM container c
                WHERE c.drink_type_id = ?
            """, (drink_type[0],))
            containers = cursor.fetchall()
            
            print(f"\nDrink Type: {drink_type[1]} (ID: {drink_type[0]})")
            if containers:
                print("ID | Name | Volume | Image Path")
                print("-" * 60)
                for container in containers:
                    print(f"{container[0]} | {container[1]} | {container[2]} | {container[3]}")
            else:
                print("No containers using this drink type")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error checking drink types: {e}")
        return False

if __name__ == "__main__":
    success = check_drink_types()
    if success:
        print("\nDrink type check completed successfully.")
        sys.exit(0)
    else:
        print("\nDrink type check failed.")
        sys.exit(1)
