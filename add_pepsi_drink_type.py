"""
Add Pepsi drink type to the Water Intake Tracker database
"""

import os
import sys
import sqlite3

def add_pepsi_drink_type():
    """
    Add Pepsi drink type to the database
    """
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    print(f"Adding Pepsi drink type to database at {db_path}...")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if Pepsi drink type already exists
        cursor.execute("SELECT id FROM drink_type WHERE name = 'Pepsi'")
        pepsi_id = cursor.fetchone()
        
        if pepsi_id:
            print(f"Pepsi drink type already exists with ID: {pepsi_id[0]}")
            conn.close()
            return True
        
        # Add Pepsi drink type
        cursor.execute("""
            INSERT INTO drink_type (name, hydration_factor, color, icon)
            VALUES (?, ?, ?, ?)
        """, ('Pepsi', 0.3, '#0000AA', 'bi-cup-straw'))
        
        # Get the ID of the new drink type
        pepsi_id = cursor.lastrowid
        print(f"Added Pepsi drink type with ID: {pepsi_id}")
        
        # Update Pepsi Can containers to use the new drink type
        cursor.execute("""
            UPDATE container 
            SET drink_type_id = ? 
            WHERE name LIKE '%Pepsi%' OR name LIKE '%pepsi%'
        """, (pepsi_id,))
        
        rows_updated = cursor.rowcount
        print(f"Updated {rows_updated} Pepsi containers to use the new drink type")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print("Pepsi drink type added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding Pepsi drink type: {e}")
        return False

if __name__ == "__main__":
    success = add_pepsi_drink_type()
    if success:
        print("Operation completed successfully.")
        sys.exit(0)
    else:
        print("Operation failed.")
        sys.exit(1)
