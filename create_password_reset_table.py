#!/usr/bin/env python3
"""
Create Password Reset Token Table using direct SQL
This script creates the password reset table without using SQLAlchemy to avoid database lock issues.
"""

import sqlite3
import os
from datetime import datetime

def create_password_reset_table():
    """Create the password reset token table using direct SQL"""
    
    db_path = 'instance/water_tracker_backup.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔐 Creating password reset token table...")
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='password_reset_tokens'
        """)
        
        if cursor.fetchone():
            print("ℹ️  Table 'password_reset_tokens' already exists")
            
            # Show existing structure
            cursor.execute("PRAGMA table_info(password_reset_tokens)")
            columns = cursor.fetchall()
            print("\n📋 Existing table structure:")
            for column in columns:
                print(f"   - {column[1]}: {column[2]}")
        else:
            # Create the table
            cursor.execute("""
                CREATE TABLE password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token VARCHAR(100) UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES user (id)
                )
            """)
            
            print("✅ Password reset token table created successfully!")
            
            # Verify the table was created
            cursor.execute("PRAGMA table_info(password_reset_tokens)")
            columns = cursor.fetchall()
            print("\n📋 New table structure:")
            for column in columns:
                print(f"   - {column[1]}: {column[2]}")
        
        # Create index for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token 
            ON password_reset_tokens(token)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id 
            ON password_reset_tokens(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at 
            ON password_reset_tokens(expires_at)
        """)
        
        print("✅ Database indexes created successfully!")
        
        # Commit changes
        conn.commit()
        
        # Show all tables to confirm
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n📊 Total tables in database: {len(tables)}")
        
        # Check if our table is there
        table_names = [table[0] for table in tables]
        if 'password_reset_tokens' in table_names:
            print("✅ Password reset token table confirmed in database")
        else:
            print("❌ Password reset token table not found after creation")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("🔐 Password Reset Table Setup")
    print("=" * 40)
    
    success = create_password_reset_table()
    
    if success:
        print("\n🎉 Password reset functionality is now ready!")
        print("\nNext steps:")
        print("1. Configure email settings in your environment variables:")
        print("   - MAIL_SERVER (default: smtp.gmail.com)")
        print("   - MAIL_PORT (default: 587)")
        print("   - MAIL_USERNAME (your email)")
        print("   - MAIL_PASSWORD (your email password or app password)")
        print("   - MAIL_DEFAULT_SENDER (sender email)")
        print("\n2. For Gmail, you may need to:")
        print("   - Enable 2-factor authentication")
        print("   - Generate an app-specific password")
        print("   - Use the app password instead of your regular password")
        print("\n3. Test the password reset functionality:")
        print("   - Start your Flask app")
        print("   - Go to /forgot-password")
        print("   - Enter a valid email address")
        print("   - Check your email for the reset link")
        print("\n4. Available routes:")
        print("   - /forgot-password (request reset)")
        print("   - /reset-password/<token> (reset with token)")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        exit(1)
