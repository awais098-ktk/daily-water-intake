#!/usr/bin/env python3
"""
Manually refresh expired Google Fit tokens
"""

import os
import sys
import sqlite3
from datetime import datetime, timezone

# Add the water_tracker directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'water_tracker'))

def refresh_expired_tokens():
    """Refresh all expired Google Fit tokens"""
    
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find expired Google Fit connections with refresh tokens
        cursor.execute("""
            SELECT id, user_id, platform, access_token, refresh_token, token_expires_at, is_active
            FROM wearable_connections 
            WHERE platform = 'google_fit' 
            AND is_active = 1 
            AND refresh_token IS NOT NULL
            AND token_expires_at < datetime('now')
        """)
        
        expired_connections = cursor.fetchall()
        
        if not expired_connections:
            print("✅ No expired Google Fit tokens found")
            return True
        
        print(f"🔄 Found {len(expired_connections)} expired Google Fit connections")
        
        # Import OAuth manager
        from water_tracker.wearable_integration.oauth_manager import OAuthManager
        
        # Create OAuth manager with dummy config (we only need the refresh functionality)
        oauth_config = {
            'GOOGLE_FIT_CLIENT_ID': os.getenv('GOOGLE_FIT_CLIENT_ID', ''),
            'GOOGLE_FIT_CLIENT_SECRET': os.getenv('GOOGLE_FIT_CLIENT_SECRET', ''),
            'FITBIT_CLIENT_ID': os.getenv('FITBIT_CLIENT_ID', ''),
            'FITBIT_CLIENT_SECRET': os.getenv('FITBIT_CLIENT_SECRET', '')
        }
        
        oauth_manager = OAuthManager(oauth_config)
        
        refreshed_count = 0
        failed_count = 0
        
        for connection in expired_connections:
            print(f"\n🔄 Refreshing token for connection ID {connection['id']} (User {connection['user_id']})")
            print(f"   Expired at: {connection['token_expires_at']}")
            
            try:
                # Attempt to refresh the token
                new_token_info = oauth_manager.refresh_access_token('google_fit', connection['refresh_token'])
                
                # Update the database with new token info
                update_query = """
                    UPDATE wearable_connections 
                    SET access_token = ?, 
                        refresh_token = ?, 
                        token_expires_at = ?
                    WHERE id = ?
                """
                
                new_refresh_token = new_token_info.get('refresh_token', connection['refresh_token'])
                new_expires_at = new_token_info.get('expires_at')
                
                cursor.execute(update_query, (
                    new_token_info['access_token'],
                    new_refresh_token,
                    new_expires_at.isoformat() if new_expires_at else None,
                    connection['id']
                ))
                
                conn.commit()
                
                print(f"   ✅ Successfully refreshed token")
                print(f"   New expiry: {new_expires_at}")
                refreshed_count += 1
                
            except Exception as e:
                print(f"   ❌ Failed to refresh token: {e}")
                failed_count += 1
        
        conn.close()
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Successfully refreshed: {refreshed_count}")
        print(f"   ❌ Failed to refresh: {failed_count}")
        
        if refreshed_count > 0:
            print(f"\n🎉 Token refresh completed! You can now sync your Google Fit data.")
        
        return refreshed_count > 0
        
    except Exception as e:
        print(f"❌ Error refreshing tokens: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_token_status():
    """Check the status of all wearable connections"""
    
    db_path = os.path.join('instance', 'water_tracker.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT wc.id, wc.platform, wc.is_active, wc.token_expires_at, wc.last_sync,
                   u.username
            FROM wearable_connections wc
            JOIN user u ON wc.user_id = u.id
            ORDER BY wc.platform, wc.id
        """)
        
        connections = cursor.fetchall()
        
        print("🔗 Wearable Connection Status:")
        print("=" * 80)
        
        for conn_data in connections:
            status = "🟢 Active" if conn_data['is_active'] else "🔴 Inactive"
            
            # Check if token is expired
            token_status = "✅ Valid"
            if conn_data['token_expires_at']:
                expires_at = datetime.fromisoformat(conn_data['token_expires_at'].replace('Z', '+00:00'))
                if datetime.now(timezone.utc) >= expires_at:
                    token_status = "⚠️ Expired"
            
            print(f"ID {conn_data['id']}: {conn_data['platform']} ({conn_data['username']})")
            print(f"  Status: {status}")
            print(f"  Token: {token_status}")
            print(f"  Expires: {conn_data['token_expires_at'] or 'N/A'}")
            print(f"  Last Sync: {conn_data['last_sync'] or 'Never'}")
            print("-" * 60)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking token status: {e}")
        return False

if __name__ == "__main__":
    print("🚰 Google Fit Token Refresh Tool")
    print("=" * 50)
    
    # Check current status
    print("\n1️⃣ Checking current token status...")
    check_token_status()
    
    # Refresh expired tokens
    print("\n2️⃣ Refreshing expired tokens...")
    success = refresh_expired_tokens()
    
    if success:
        print("\n3️⃣ Updated token status:")
        check_token_status()
    
    print("\n✅ Token refresh process completed!")
    print("\nNext steps:")
    print("1. Go to http://localhost:5201/wearable/")
    print("2. Try syncing your Google Fit data")
    print("3. If sync still fails, try reconnecting Google Fit")
