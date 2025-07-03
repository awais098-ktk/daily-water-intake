#!/usr/bin/env python3
"""
Enhanced Database Viewer for Water Intake Tracker
Includes wearable integration data and better formatting
"""

import os
import sqlite3
import sys
import json
from datetime import datetime
from tabulate import tabulate

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

        print("\n" + "="*80)
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

        conn.close()
        return True

    except Exception as e:
        print(f"Error viewing wearable data: {e}")
        return False

def view_summary_stats():
    """View summary statistics"""
    db_path = os.path.join('instance', 'water_tracker.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n" + "="*80)
        print("📈 DATABASE SUMMARY STATISTICS")
        print("="*80)

        # Get table counts
        tables = [
            'user', 'drink_type', 'container', 'water_log', 
            'wearable_connections', 'activity_data', 'hydration_recommendations',
            'food_categories', 'food_items', 'meal_containers', 'meal_logs'
        ]
        
        stats = []
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats.append([table.replace('_', ' ').title(), count])
            except:
                stats.append([table.replace('_', ' ').title(), "N/A"])

        print(tabulate(stats, headers=['Table', 'Records'], tablefmt='grid'))

        # Recent activity summary
        print(f"\n📊 RECENT ACTIVITY (Last 7 Days)")
        print("-" * 40)
        
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as logs, SUM(amount) as total_ml
            FROM water_log 
            WHERE timestamp >= date('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """)
        recent_logs = cursor.fetchall()
        
        if recent_logs:
            log_stats = []
            for log in recent_logs:
                log_stats.append([log[0], log[1], f"{log[2]:,} ml"])
            print(tabulate(log_stats, headers=['Date', 'Logs', 'Total Volume'], tablefmt='grid'))
        else:
            print("No recent water logs found.")

        conn.close()
        return True

    except Exception as e:
        print(f"Error viewing summary stats: {e}")
        return False

def interactive_query():
    """Interactive SQL query interface"""
    db_path = os.path.join('instance', 'water_tracker.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("\n" + "="*80)
        print("🔍 INTERACTIVE SQL QUERY")
        print("="*80)
        print("Enter SQL queries (type 'exit' to quit, 'tables' to see all tables)")
        print("Example: SELECT * FROM user LIMIT 5")
        print("-" * 80)

        while True:
            query = input("\nSQL> ").strip()
            
            if query.lower() == 'exit':
                break
            elif query.lower() == 'tables':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print("\nAvailable tables:")
                for table in tables:
                    print(f"  - {table[0]}")
                continue
            elif not query:
                continue

            try:
                cursor.execute(query)
                results = cursor.fetchall()
                
                if results:
                    # Convert to list of lists for tabulate
                    headers = [description[0] for description in cursor.description]
                    data = [list(row) for row in results]
                    print(f"\nResults ({len(results)} rows):")
                    print(tabulate(data, headers=headers, tablefmt='grid'))
                else:
                    print("Query executed successfully. No results returned.")
                    
            except Exception as e:
                print(f"Error executing query: {e}")

        conn.close()
        return True

    except Exception as e:
        print(f"Error in interactive query: {e}")
        return False

def main():
    """Main function with menu"""
    print("🗄️  Enhanced Database Viewer for Water Intake Tracker")
    print("="*60)
    
    while True:
        print("\nChoose an option:")
        print("1. View basic database data (existing script)")
        print("2. View wearable integration data")
        print("3. View summary statistics")
        print("4. Interactive SQL query")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            os.system('python view_db_data.py')
        elif choice == '2':
            view_wearable_data()
        elif choice == '3':
            view_summary_stats()
        elif choice == '4':
            interactive_query()
        elif choice == '5':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
