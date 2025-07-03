import sqlite3
from datetime import datetime, timedelta

# Fresh token
token = "c8ZrJp0NsDNgES9K5WD6huIPW1nOIzSLzFyUI4AopLE"
user_id = 8
created_at = datetime.now()
expires_at = created_at + timedelta(hours=1)

try:
    conn = sqlite3.connect('instance/water_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO password_reset_tokens (user_id, token, created_at, expires_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, token, created_at, expires_at))
    
    conn.commit()
    conn.close()
    
    print("✅ Token created successfully!")
    print(f"Reset URL: http://127.0.0.1:5001/reset-password/{token}")
    
except Exception as e:
    print(f"Error: {e}")
