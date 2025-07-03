#!/usr/bin/env python3
"""
Test database access
"""

import sqlite3

try:
    conn = sqlite3.connect('instance/water_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM user')
    count = cursor.fetchone()[0]
    print(f'✅ Database accessible. Current user count: {count}')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
