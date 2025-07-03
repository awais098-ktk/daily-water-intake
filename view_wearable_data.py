#!/usr/bin/env python3
"""
View wearable integration data from the database
"""

import os
import sqlite3
import json
from datetime import datetime

def view_wearable_data():
    """View wearable integration data"""
    db_path = os.path.join('instance', 'water_tracker.db')
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("="*80)
        print("🔗 WEARABLE CONNECTIONS")
        print("="*80)
        
        cursor.execute("""
            SELECT wc.*, u.username 
            FROM wearable_connections wc
            JOIN user u ON wc.user_id = u.id
            ORDER BY wc.connected_at DESC
        """)
        connections = cursor.fetchall()
        
        if connections:
            for conn_data in connections:
                print(f"📱 Connection ID: {conn_data['id']}")
                print(f"   User: {conn_data['username']} (ID: {conn_data['user_id']})")
                print(f"   Platform: {conn_data['platform']}")
                print(f"   Platform User ID: {conn_data['platform_user_id']}")
                print(f"   Active: {'✅ Yes' if conn_data['is_active'] else '❌ No'}")
                print(f"   Connected: {conn_data['connected_at']}")
                print(f"   Last Sync: {conn_data['last_sync'] or 'Never'}")
                print(f"   Token Expires: {conn_data['token_expires_at'] or 'N/A'}")
                print("-" * 60)
        else:
            print("No wearable connections found.")

        print("\n" + "="*80)
        print("🏃 ACTIVITY DATA")
        print("="*80)
        
        cursor.execute("""
            SELECT ad.*, u.username, wc.platform 
            FROM activity_data ad
            JOIN user u ON ad.user_id = u.id
            JOIN wearable_connections wc ON ad.connection_id = wc.id
            ORDER BY ad.date DESC
            LIMIT 20
        """)
        activities = cursor.fetchall()
        
        if activities:
            for activity in activities:
                print(f"📊 Date: {activity['date']}")
                print(f"   User: {activity['username']} | Platform: {activity['platform']}")
                print(f"   Steps: {activity['steps']:,} | Distance: {activity['distance_meters']:.1f}m")
                print(f"   Calories: {activity['calories_burned']} | Active Minutes: {activity['active_minutes']}")
                print(f"   Heart Rate: Avg {activity['heart_rate_avg']} | Max {activity['heart_rate_max']}")
                
                # Parse exercise sessions if available
                if activity['exercise_sessions']:
                    try:
                        sessions = json.loads(activity['exercise_sessions'])
                        if sessions:
                            print(f"   Exercise Sessions:")
                            for session in sessions:
                                print(f"     - {session.get('name', 'Unknown')}: {session.get('duration_minutes', 0)} min, {session.get('calories', 0)} cal")
                    except:
                        pass
                
                print(f"   Created: {activity['created_at']}")
                print("-" * 60)
        else:
            print("No activity data found.")

        print("\n" + "="*80)
        print("💧 HYDRATION RECOMMENDATIONS")
        print("="*80)
        
        cursor.execute("""
            SELECT hr.*, u.username 
            FROM hydration_recommendations hr
            JOIN user u ON hr.user_id = u.id
            ORDER BY hr.date DESC
            LIMIT 10
        """)
        recommendations = cursor.fetchall()
        
        if recommendations:
            for rec in recommendations:
                print(f"📅 Date: {rec['date']}")
                print(f"   User: {rec['username']}")
                print(f"   Base Recommendation: {rec['base_recommendation']} ml")
                print(f"   Activity Bonus: {rec['activity_bonus']} ml")
                print(f"   Total Recommendation: {rec['total_recommendation']} ml")
                print(f"   Reasoning: {rec['reasoning']}")
                print(f"   Created: {rec['created_at']}")
                print("-" * 60)
        else:
            print("No hydration recommendations found.")

        # Summary statistics
        print("\n" + "="*80)
        print("📈 SUMMARY STATISTICS")
        print("="*80)
        
        cursor.execute("SELECT COUNT(*) FROM wearable_connections WHERE is_active = 1")
        active_connections = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM activity_data")
        total_activity_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM wearable_connections")
        users_with_wearables = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(date) FROM activity_data")
        latest_activity = cursor.fetchone()[0]
        
        print(f"Active Connections: {active_connections}")
        print(f"Total Activity Records: {total_activity_records}")
        print(f"Users with Wearables: {users_with_wearables}")
        print(f"Latest Activity Date: {latest_activity or 'None'}")

        conn.close()
        return True

    except Exception as e:
        print(f"Error viewing wearable data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = view_wearable_data()
    if success:
        print("\n✅ Wearable data view completed successfully.")
    else:
        print("\n❌ Failed to view wearable data.")
