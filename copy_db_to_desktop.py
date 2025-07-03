#!/usr/bin/env python3
"""
Copy database file to desktop for easy access
"""

import os
import shutil
from datetime import datetime

def copy_to_desktop():
    """Copy database to desktop"""
    
    # Source database
    source_db = os.path.join('instance', 'water_tracker.db')
    
    # Desktop path (Windows)
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    desktop_filename = f'water_tracker_database_{timestamp}.db'
    desktop_path = os.path.join(desktop, desktop_filename)
    
    try:
        # Copy to desktop
        shutil.copy2(source_db, desktop_path)
        
        # Get file size
        file_size = os.path.getsize(desktop_path) / 1024
        
        print("✅ Database copied to desktop successfully!")
        print(f"📁 Location: {desktop_path}")
        print(f"💾 File size: {file_size:.1f} KB")
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return desktop_path
        
    except Exception as e:
        print(f"❌ Error copying to desktop: {e}")
        print("Trying alternative location...")
        
        # Try current directory as fallback
        fallback_path = f'water_tracker_database_{timestamp}.db'
        try:
            shutil.copy2(source_db, fallback_path)
            print(f"✅ Database copied to: {os.path.abspath(fallback_path)}")
            return fallback_path
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            return None

if __name__ == "__main__":
    copy_to_desktop()
