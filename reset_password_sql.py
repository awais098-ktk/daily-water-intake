#!/usr/bin/env python3
"""
Quick Password Reset - Generate SQL Commands
This script generates the SQL commands to reset passwords manually.
"""

from werkzeug.security import generate_password_hash

def generate_reset_sql(username, new_password):
    """Generate SQL command to reset password"""
    password_hash = generate_password_hash(new_password)
    
    sql_command = f"""
-- Reset password for user '{username}'
UPDATE user 
SET password_hash = '{password_hash}' 
WHERE username = '{username}';

-- Verify the update
SELECT id, username, email, 'Password Updated' as status 
FROM user 
WHERE username = '{username}';
"""
    
    return sql_command

def main():
    print("🔐 SQL Password Reset Generator")
    print("=" * 40)
    
    # Common users and their new passwords
    reset_requests = [
        ("demo", "demo123"),
        ("khattak", "khattak123"),
        ("farhan", "farhan123"),
        ("awais2", "awais123"),
        ("ahamd", "ahmad123"),
        ("basit", "basit123"),
        ("atif", "atif123")
    ]
    
    print("Generated SQL commands for password reset:")
    print("=" * 50)
    
    for username, password in reset_requests:
        print(f"\n-- Reset password for {username}")
        sql = generate_reset_sql(username, password)
        print(sql)
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCTIONS:")
    print("1. Copy the SQL commands above")
    print("2. Open DB Browser for SQLite")
    print("3. Open your database: instance/water_tracker.db")
    print("4. Go to 'Execute SQL' tab")
    print("5. Paste and run the SQL commands")
    print("6. Click 'Execute' to run the commands")
    
    print("\n🔑 DEFAULT PASSWORDS:")
    for username, password in reset_requests:
        print(f"   {username}: {password}")

if __name__ == '__main__':
    main()
