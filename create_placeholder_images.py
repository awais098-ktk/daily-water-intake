"""
Create placeholder images for the Water Intake Tracker app
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_container_placeholder():
    """Create a placeholder image for containers"""
    # Create a new image with a light gray background
    img = Image.new('RGB', (300, 300), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a cup shape
    # Cup outline
    draw.rectangle((100, 80, 200, 220), outline=(100, 100, 100), width=3)
    # Cup base
    draw.rectangle((90, 220, 210, 230), fill=(100, 100, 100), outline=(100, 100, 100))
    # Cup handle
    draw.arc((200, 120, 240, 180), start=270, end=90, fill=(100, 100, 100), width=3)
    
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
                
        draw.text((80, 250), "Container Image", fill=(100, 100, 100), font=font)
    except:
        # If font handling fails, use simple text
        draw.text((80, 250), "Container Image", fill=(100, 100, 100))
    
    # Save the image
    static_folder = os.path.join('water_tracker', 'static')
    images_folder = os.path.join(static_folder, 'images')
    os.makedirs(images_folder, exist_ok=True)
    
    img.save(os.path.join(images_folder, 'container_placeholder.png'))
    print(f"Created container placeholder image at {os.path.join(images_folder, 'container_placeholder.png')}")

if __name__ == "__main__":
    create_container_placeholder()
