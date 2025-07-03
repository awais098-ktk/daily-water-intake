#!/usr/bin/env python3
"""
Verify that the password reset table exists in the main database
"""

import sqlite3

def verify_table():
    conn = sqlite3.connect('instance/water_tracker.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="password_reset_tokens"')
    result = cursor.fetchone()
    
    if result:
        print('✅ Password reset table exists in main database')
        
        # Show table structure
        cursor.execute('PRAGMA table_info(password_reset_tokens)')
        columns = cursor.fetchall()
        print('Table structure:')
        for column in columns:
            print(f'  - {column[1]}: {column[2]}')
            
        # Show indexes
        cursor.execute('SELECT name FROM sqlite_master WHERE type="index" AND tbl_name="password_reset_tokens"')
        indexes = cursor.fetchall()
        if indexes:
            print('Indexes:')
            for index in indexes:
                print(f'  - {index[0]}')
    else:
        print('❌ Password reset table not found')
    
    conn.close()

if __name__ == '__main__':
    verify_table()
