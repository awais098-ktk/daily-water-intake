#!/usr/bin/env python3
"""
Password Reset Script for Water Intake Tracker
This script allows you to reset a user's password directly in the database.
"""

import sys
import os
import sqlite3
from werkzeug.security import generate_password_hash

def list_users():
    """List all users in the database"""
    conn = sqlite3.connect('instance/water_tracker.db')
    cursor = conn.cursor()
    
    print("\n=== CURRENT USERS ===")
    cursor.execute('SELECT id, username, email FROM user ORDER BY id')
    users = cursor.fetchall()
    
    if users:
        print("ID | Username | Email")
        print("-" * 40)
        for user in users:
            print(f"{user[0]:2} | {user[1]:10} | {user[2]}")
    else:
        print("No users found")
    
    conn.close()
    return users

def reset_password(username, new_password):
    """Reset password for a specific user"""
    conn = sqlite3.connect('instance/water_tracker.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id, username FROM user WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ User '{username}' not found!")
        conn.close()
        return False
    
    # Generate password hash using the same method as the app
    password_hash = generate_password_hash(new_password)
    
    # Update the password
    cursor.execute('UPDATE user SET password_hash = ? WHERE username = ?', 
                   (password_hash, username))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Password successfully reset for user '{username}'")
        print(f"   New password: {new_password}")
        conn.close()
        return True
    else:
        print(f"❌ Failed to update password for user '{username}'")
        conn.close()
        return False

def main():
    """Main function"""
    print("🔐 Water Intake Tracker - Password Reset Tool")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('instance/water_tracker.db'):
        print("❌ Database file not found at 'instance/water_tracker.db'")
        print("   Make sure you're running this script from the project root directory.")
        return
    
    # List current users
    users = list_users()
    if not users:
        return
    
    print("\n" + "=" * 50)
    
    # Get username to reset
    while True:
        username = input("\nEnter username to reset password (or 'quit' to exit): ").strip()
        
        if username.lower() == 'quit':
            print("👋 Goodbye!")
            return
        
        if not username:
            print("❌ Please enter a valid username")
            continue
        
        # Get new password
        new_password = input(f"Enter new password for '{username}': ").strip()
        
        if not new_password:
            print("❌ Password cannot be empty")
            continue
        
        if len(new_password) < 3:
            print("❌ Password should be at least 3 characters long")
            continue
        
        # Confirm the action
        confirm = input(f"\n⚠️  Are you sure you want to reset password for '{username}'? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            if reset_password(username, new_password):
                print(f"\n🎉 You can now login with:")
                print(f"   Username: {username}")
                print(f"   Password: {new_password}")
                break
            else:
                print("❌ Password reset failed. Please try again.")
        else:
            print("❌ Password reset cancelled.")
        
        # Ask if they want to try again
        try_again = input("\nTry again? (yes/no): ").strip().lower()
        if try_again not in ['yes', 'y']:
            break

if __name__ == '__main__':
    main()
