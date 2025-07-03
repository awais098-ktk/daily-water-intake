import sqlite3
from datetime import datetime
 
# Connect to SQLite database (or create it if not exists)
conn = sqlite3.connect("data/water_logs.db")
cursor = conn.cursor()
 
# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS water_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    )
''')
conn.commit()
 
# Function to insert water log
def insert_log(amount):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO water_log (amount, timestamp) VALUES (?, ?)", (amount, timestamp))
    conn.commit()
 
# Function to fetch today's total intake
def get_today_total():
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(amount) FROM water_log WHERE date(timestamp) = ?", (today,))
    result = cursor.fetchone()[0]
    return result if result else 0
def get_last_7_days():
    cursor.execute("""
        SELECT DATE(timestamp) as day, SUM(amount)
        FROM water_log
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    """)
    data = cursor.fetchall()
    data.reverse()  # Show oldest to newest
    return data