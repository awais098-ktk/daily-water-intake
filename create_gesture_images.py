"""
Create placeholder images for gesture examples
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_peace_sign_image():
    """Create a placeholder image for the peace sign gesture"""
    img = Image.new('RGB', (200, 200), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a hand outline
    draw.ellipse((50, 100, 150, 200), outline=(100, 100, 100), width=2)  # Palm
    
    # Draw fingers (peace sign)
    draw.line((100, 150, 70, 50), fill=(100, 100, 100), width=8)  # Index finger
    draw.line((100, 150, 130, 50), fill=(100, 100, 100), width=8)  # Middle finger
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        draw.text((60, 20), "Peace Sign ✌️", fill=(0, 0, 0), font=font)
    except:
        # If font not available, use default
        draw.text((60, 20), "Peace Sign", fill=(0, 0, 0))
    
    return img

def create_thumbs_up_image():
    """Create a placeholder image for the thumbs up gesture"""
    img = Image.new('RGB', (200, 200), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw a hand outline
    draw.ellipse((75, 100, 150, 175), outline=(100, 100, 100), width=2)  # Palm
    
    # Draw thumb
    draw.line((100, 125, 50, 75), fill=(100, 100, 100), width=10)  # Thumb
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        draw.text((60, 20), "Thumbs Up 👍", fill=(0, 0, 0), font=font)
    except:
        # If font not available, use default
        draw.text((60, 20), "Thumbs Up", fill=(0, 0, 0))
    
    return img

def main():
    """Create and save the gesture images"""
    # Create the directory if it doesn't exist
    images_dir = os.path.join('water_tracker', 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Create and save the peace sign image
    peace_sign_img = create_peace_sign_image()
    peace_sign_path = os.path.join(images_dir, 'peace_sign.png')
    peace_sign_img.save(peace_sign_path)
    print(f"Created peace sign image at {peace_sign_path}")
    
    # Create and save the thumbs up image
    thumbs_up_img = create_thumbs_up_image()
    thumbs_up_path = os.path.join(images_dir, 'thumbs_up.png')
    thumbs_up_img.save(thumbs_up_path)
    print(f"Created thumbs up image at {thumbs_up_path}")

if __name__ == "__main__":
    main()
