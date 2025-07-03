#!/usr/bin/env python3
"""
Generate a fresh password reset token
"""

import sqlite3
import secrets
from datetime import datetime, timedelta

def generate_reset_token():
    try:
        # Generate a fresh token
        token = secrets.token_urlsafe(32)
        user_id = 8  # awais.rehmanktk@gmail.com
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=1)

        # Connect to database
        conn = sqlite3.connect('instance/water_tracker.db')
        cursor = conn.cursor()

        # Insert new token
        cursor.execute('''
            INSERT INTO password_reset_tokens (user_id, token, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, token, created_at, expires_at))

        conn.commit()
        conn.close()

        print('=== FRESH PASSWORD RESET TOKEN CREATED ===')
        print(f'User ID: {user_id}')
        print(f'Token: {token}')
        print(f'Created: {created_at}')
        print(f'Expires: {expires_at}')
        print()
        print('🔗 YOUR RESET URL:')
        print(f'http://127.0.0.1:5001/reset-password/{token}')
        print()
        print('Copy the URL above and paste it into your browser!')
        
        return token
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    generate_reset_token()
