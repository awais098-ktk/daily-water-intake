"""
Check database tables for Water Intake Tracker
"""

import os
import sqlite3
import sys

def check_database():
    """
    Check the database tables
    """
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False

    print(f"Checking database at {db_path}...")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("Tables in the database:")
        for table in tables:
            print(f"- {table[0]}")

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()

            print("  Columns:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            row_count = cursor.fetchone()[0]
            print(f"  Row count: {row_count}")
            print()

        conn.close()
        return True

    except Exception as e:
        print(f"Error checking database: {e}")
        return False

if __name__ == "__main__":
    success = check_database()
    if success:
        print("Database check completed successfully.")
        sys.exit(0)
    else:
        print("Database check failed.")
        sys.exit(1)
