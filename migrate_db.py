"""
Database migration script for Water Intake Tracker
This script adds the drink_type_id column to the container table
"""

import os
import sqlite3
import sys

def migrate_database():
    """
    Migrate the database to add the drink_type_id column to the container table
    """
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False

    print(f"Migrating database at {db_path}...")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the column already exists
        cursor.execute("PRAGMA table_info(container)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'drink_type_id' in column_names:
            print("Column 'drink_type_id' already exists in the container table.")
            conn.close()
            return True

        # Add the new column
        print("Adding 'drink_type_id' column to the container table...")
        cursor.execute("ALTER TABLE container ADD COLUMN drink_type_id INTEGER")

        # Set default values for existing containers
        # Get the soda drink type ID
        cursor.execute("SELECT id FROM drink_type WHERE name = 'Soda'")
        soda_id = cursor.fetchone()

        if soda_id:
            # Update Pepsi Can containers to use Soda drink type
            cursor.execute("""
                UPDATE container
                SET drink_type_id = ?
                WHERE name LIKE '%Pepsi%' OR name LIKE '%pepsi%'
            """, (soda_id[0],))

            print(f"Updated Pepsi containers to use Soda drink type (ID: {soda_id[0]})")

        # Get the water drink type ID
        cursor.execute("SELECT id FROM drink_type WHERE name = 'Water'")
        water_id = cursor.fetchone()

        if water_id:
            # Update Water Bottle containers to use Water drink type
            cursor.execute("""
                UPDATE container
                SET drink_type_id = ?
                WHERE name LIKE '%Water%' OR name LIKE '%water%'
            """, (water_id[0],))

            print(f"Updated Water containers to use Water drink type (ID: {water_id[0]})")

        # Get the coffee drink type ID
        cursor.execute("SELECT id FROM drink_type WHERE name = 'Coffee'")
        coffee_id = cursor.fetchone()

        if coffee_id:
            # Update Coffee Mug containers to use Coffee drink type
            cursor.execute("""
                UPDATE container
                SET drink_type_id = ?
                WHERE name LIKE '%Coffee%' OR name LIKE '%coffee%'
            """, (coffee_id[0],))

            print(f"Updated Coffee containers to use Coffee drink type (ID: {coffee_id[0]})")

        # Commit the changes
        conn.commit()
        conn.close()

        print("Database migration completed successfully!")
        return True

    except Exception as e:
        print(f"Error migrating database: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("Migration completed successfully.")
        sys.exit(0)
    else:
        print("Migration failed.")
        sys.exit(1)
