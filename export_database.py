#!/usr/bin/env python3
"""
Export database file for external SQLite viewer access
"""

import os
import shutil
import sqlite3
from datetime import datetime

def export_database():
    """Export the database file with metadata"""
    
    # Source database path
    source_db = os.path.join('instance', 'water_tracker.db')
    
    # Create export directory if it doesn't exist
    export_dir = 'database_export'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export filename
    export_filename = f'water_tracker_db_{timestamp}.db'
    export_path = os.path.join(export_dir, export_filename)
    
    try:
        # Copy the database file
        shutil.copy2(source_db, export_path)
        
        # Get database info
        conn = sqlite3.connect(source_db)
        cursor = conn.cursor()
        
        # Get table counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_info = []
        total_records = 0
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_info.append(f"  - {table_name}: {count:,} records")
            total_records += count
        
        conn.close()
        
        # Create info file
        info_filename = f'water_tracker_db_info_{timestamp}.txt'
        info_path = os.path.join(export_dir, info_filename)
        
        with open(info_path, 'w') as f:
            f.write("Water Intake Tracker Database Export\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database File: {export_filename}\n")
            f.write(f"Total Records: {total_records:,}\n\n")
            f.write("Tables and Record Counts:\n")
            f.write("\n".join(table_info))
            f.write("\n\n")
            f.write("How to Use:\n")
            f.write("1. Download a SQLite browser like DB Browser for SQLite\n")
            f.write("2. Open the .db file in your SQLite browser\n")
            f.write("3. Browse tables, run queries, and analyze data\n\n")
            f.write("Recommended SQLite Browsers:\n")
            f.write("- DB Browser for SQLite (https://sqlitebrowser.org/)\n")
            f.write("- SQLite Studio (https://sqlitestudio.pl/)\n")
            f.write("- DBeaver (https://dbeaver.io/)\n")
            f.write("- SQLiteOnline (https://sqliteonline.com/)\n")
        
        print(f"✅ Database exported successfully!")
        print(f"📁 Export location: {os.path.abspath(export_path)}")
        print(f"📄 Info file: {os.path.abspath(info_path)}")
        print(f"📊 Total records: {total_records:,}")
        print(f"💾 File size: {os.path.getsize(export_path) / 1024:.1f} KB")
        
        return export_path, info_path
        
    except Exception as e:
        print(f"❌ Error exporting database: {e}")
        return None, None

def create_sample_queries():
    """Create a file with useful SQL queries"""
    
    export_dir = 'database_export'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    queries_filename = f'useful_queries_{timestamp}.sql'
    queries_path = os.path.join(export_dir, queries_filename)
    
    queries = """-- Water Intake Tracker - Useful SQL Queries
-- Copy and paste these into your SQLite browser

-- 1. View all users and their daily goals
SELECT id, username, email, daily_goal, preferred_unit, theme, gender
FROM user
ORDER BY join_date DESC;

-- 2. Recent water logs with user and drink type info
SELECT 
    wl.timestamp,
    u.username,
    wl.amount,
    dt.name as drink_type,
    c.name as container_name,
    wl.input_method,
    wl.notes
FROM water_log wl
JOIN user u ON wl.user_id = u.id
LEFT JOIN drink_type dt ON wl.drink_type_id = dt.id
LEFT JOIN container c ON wl.container_id = c.id
ORDER BY wl.timestamp DESC
LIMIT 50;

-- 3. Daily water intake summary by user
SELECT 
    u.username,
    DATE(wl.timestamp) as date,
    SUM(wl.amount) as total_ml,
    COUNT(*) as log_count,
    u.daily_goal,
    ROUND((SUM(wl.amount) * 100.0 / u.daily_goal), 1) as goal_percentage
FROM water_log wl
JOIN user u ON wl.user_id = u.id
GROUP BY u.id, DATE(wl.timestamp)
ORDER BY date DESC, u.username;

-- 4. Most popular drink types
SELECT 
    dt.name,
    dt.hydration_factor,
    COUNT(wl.id) as log_count,
    SUM(wl.amount) as total_volume_ml,
    AVG(wl.amount) as avg_amount_per_log
FROM drink_type dt
LEFT JOIN water_log wl ON dt.id = wl.drink_type_id
GROUP BY dt.id
ORDER BY log_count DESC;

-- 5. Container usage statistics
SELECT 
    c.name,
    c.volume,
    u.username as owner,
    dt.name as default_drink_type,
    COUNT(wl.id) as times_used,
    SUM(wl.amount) as total_volume_logged
FROM container c
JOIN user u ON c.user_id = u.id
LEFT JOIN drink_type dt ON c.drink_type_id = dt.id
LEFT JOIN water_log wl ON c.id = wl.container_id
GROUP BY c.id
ORDER BY times_used DESC;

-- 6. Google Fit wearable connections status
SELECT 
    u.username,
    wc.platform,
    wc.platform_user_id,
    wc.is_active,
    wc.connected_at,
    wc.last_sync,
    wc.token_expires_at
FROM wearable_connections wc
JOIN user u ON wc.user_id = u.id
ORDER BY wc.connected_at DESC;

-- 7. Activity data from wearables
SELECT 
    ad.date,
    u.username,
    wc.platform,
    ad.steps,
    ad.distance_meters,
    ad.calories_burned,
    ad.active_minutes,
    ad.heart_rate_avg,
    ad.heart_rate_max
FROM activity_data ad
JOIN user u ON ad.user_id = u.id
JOIN wearable_connections wc ON ad.connection_id = wc.id
ORDER BY ad.date DESC;

-- 8. Weekly water intake trends
SELECT 
    u.username,
    strftime('%Y-W%W', wl.timestamp) as week,
    SUM(wl.amount) as weekly_total_ml,
    COUNT(*) as weekly_logs,
    AVG(wl.amount) as avg_per_log,
    (SUM(wl.amount) / 7.0) as daily_average
FROM water_log wl
JOIN user u ON wl.user_id = u.id
GROUP BY u.id, strftime('%Y-W%W', wl.timestamp)
ORDER BY week DESC, u.username;

-- 9. Input method analysis
SELECT 
    input_method,
    COUNT(*) as usage_count,
    SUM(amount) as total_volume,
    AVG(amount) as avg_amount,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM water_log)), 2) as percentage
FROM water_log
GROUP BY input_method
ORDER BY usage_count DESC;

-- 10. User activity correlation (water vs steps)
SELECT 
    u.username,
    DATE(wl.timestamp) as date,
    SUM(wl.amount) as water_ml,
    ad.steps,
    ad.calories_burned,
    ad.active_minutes
FROM water_log wl
JOIN user u ON wl.user_id = u.id
LEFT JOIN activity_data ad ON u.id = ad.user_id AND DATE(wl.timestamp) = ad.date
GROUP BY u.id, DATE(wl.timestamp)
HAVING ad.steps IS NOT NULL
ORDER BY date DESC;

-- 11. Food logging data (if available)
SELECT 
    ml.timestamp,
    u.username,
    ml.food_name,
    ml.quantity_g,
    ml.calories,
    ml.meal_type,
    ml.input_method
FROM meal_logs ml
JOIN user u ON ml.user_id = u.id
ORDER BY ml.timestamp DESC
LIMIT 50;

-- 12. Database overview - record counts
SELECT 
    'Users' as table_name, COUNT(*) as record_count FROM user
UNION ALL SELECT 'Water Logs', COUNT(*) FROM water_log
UNION ALL SELECT 'Drink Types', COUNT(*) FROM drink_type
UNION ALL SELECT 'Containers', COUNT(*) FROM container
UNION ALL SELECT 'Wearable Connections', COUNT(*) FROM wearable_connections
UNION ALL SELECT 'Activity Data', COUNT(*) FROM activity_data
UNION ALL SELECT 'Food Items', COUNT(*) FROM food_items
UNION ALL SELECT 'Meal Logs', COUNT(*) FROM meal_logs
ORDER BY record_count DESC;
"""
    
    try:
        with open(queries_path, 'w') as f:
            f.write(queries)
        
        print(f"📝 Sample queries created: {os.path.abspath(queries_path)}")
        return queries_path
        
    except Exception as e:
        print(f"❌ Error creating queries file: {e}")
        return None

if __name__ == "__main__":
    print("🗄️  Water Tracker Database Export Tool")
    print("=" * 50)
    
    # Export database
    db_path, info_path = export_database()
    
    if db_path:
        # Create sample queries
        queries_path = create_sample_queries()
        
        print("\n" + "=" * 50)
        print("📋 NEXT STEPS:")
        print("=" * 50)
        print("1. Navigate to the 'database_export' folder")
        print("2. Download a SQLite browser:")
        print("   • DB Browser for SQLite: https://sqlitebrowser.org/")
        print("   • SQLite Studio: https://sqlitestudio.pl/")
        print("   • Online: https://sqliteonline.com/")
        print("3. Open the .db file in your SQLite browser")
        print("4. Use the provided SQL queries to explore your data")
        print("\n✅ Export completed successfully!")
    else:
        print("\n❌ Export failed!")
