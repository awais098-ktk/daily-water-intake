"""
Fix container image paths in the Water Intake Tracker database
"""

import os
import sys
import sqlite3
import shutil
from PIL import Image, ImageDraw, ImageFont

def fix_container_images():
    """
    Fix container image paths in the database and create missing images
    """
    # Database path
    db_path = os.path.join('instance', 'water_tracker.db')
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    print(f"Fixing container image paths in database at {db_path}...")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all containers with image paths
        cursor.execute("SELECT id, name, image_path FROM container WHERE image_path IS NOT NULL")
        containers = cursor.fetchall()
        
        # Create the containers directory if it doesn't exist
        containers_dir = os.path.join('water_tracker', 'static', 'uploads', 'containers')
        os.makedirs(containers_dir, exist_ok=True)
        
        # Create a pepsi can image
        pepsi_image_path = os.path.join(containers_dir, 'pepsi_can.png')
        if not os.path.exists(pepsi_image_path):
            try:
                create_pepsi_can_image(pepsi_image_path)
                print(f"Created Pepsi can image at {pepsi_image_path}")
            except Exception as e:
                print(f"Error creating Pepsi can image: {e}")
        
        # Fix container image paths
        for container_id, name, image_path in containers:
            if 'pepsi' in name.lower():
                # For Pepsi containers, use the pepsi_can.png image
                new_path = 'uploads/containers/pepsi_can.png'
                cursor.execute("UPDATE container SET image_path = ? WHERE id = ?", (new_path, container_id))
                print(f"Updated container {container_id} ({name}) to use {new_path}")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print("Container image paths fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error fixing container image paths: {e}")
        return False

def create_pepsi_can_image(output_path):
    """
    Create a Pepsi can image
    """
    # Create a more realistic Pepsi can
    img = Image.new('RGB', (200, 400), color=(0, 0, 150))  # Blue background
    draw = ImageDraw.Draw(img)
    
    # Can shape
    draw.rectangle((50, 50, 150, 350), fill=(0, 0, 150), outline=(200, 200, 200), width=2)
    
    # Pepsi logo (simplified)
    draw.ellipse((60, 80, 140, 160), fill=(255, 255, 255))  # White circle
    draw.arc((70, 90, 130, 150), start=0, end=180, fill=(255, 0, 0), width=10)  # Red arc
    draw.arc((70, 110, 130, 170), start=180, end=360, fill=(0, 0, 150), width=10)  # Blue arc
    
    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                
        draw.text((70, 200), "PEPSI", fill=(255, 255, 255), font=font)
        draw.text((60, 240), "350ml", fill=(255, 255, 255), font=font)
    except:
        # If font handling fails, use simple text
        draw.text((70, 200), "PEPSI", fill=(255, 255, 255))
        draw.text((60, 240), "350ml", fill=(255, 255, 255))
    
    # Add some details
    draw.rectangle((50, 280, 150, 300), fill=(200, 200, 200))  # Silver band
    
    # Save the image
    img.save(output_path)

if __name__ == "__main__":
    success = fix_container_images()
    if success:
        print("Operation completed successfully.")
        sys.exit(0)
    else:
        print("Operation failed.")
        sys.exit(1)
