#!/usr/bin/env python3
"""
Migration script to add sleep data fields to the activity_data table
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add sleep data columns to activity_data table"""
    
    # Database path
    db_path = 'instance/water_tracker.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Adding sleep data columns to activity_data table...")
        
        # List of new columns to add
        new_columns = [
            ('sleep_duration_minutes', 'INTEGER'),
            ('sleep_efficiency', 'REAL'),
            ('deep_sleep_minutes', 'INTEGER'),
            ('light_sleep_minutes', 'INTEGER'),
            ('rem_sleep_minutes', 'INTEGER'),
            ('awake_minutes', 'INTEGER'),
            ('sleep_start_time', 'DATETIME'),
            ('sleep_end_time', 'DATETIME')
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(activity_data)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add new columns that don't exist
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                sql = f"ALTER TABLE activity_data ADD COLUMN {column_name} {column_type}"
                print(f"Adding column: {column_name}")
                cursor.execute(sql)
            else:
                print(f"Column {column_name} already exists, skipping...")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(activity_data)")
        columns = cursor.fetchall()
        print(f"\nActivity data table now has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Running sleep data migration...")
    success = run_migration()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
