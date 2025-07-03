"""
Simple avatar generator for Water Intake Tracker
Creates default avatar images for user profiles using PIL
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Define colors
BACKGROUND_COLORS = [
    (77, 166, 255),    # Blue
    (255, 107, 107),   # Red
    (76, 175, 80),     # Green
    (156, 39, 176),    # Purple
    (255, 152, 0),     # Orange
    (0, 188, 212),     # Cyan
]

def generate_avatar(text, output_path, bg_color, size=(200, 200)):
    """Generate a simple avatar with initials"""
    # Create a new image with the given background color
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text
    draw.text(position, text, fill="white", font=font)
    
    # Save the image
    img.save(output_path)
    
    return output_path

def generate_default_avatars(output_dir):
    """Generate a set of default avatars"""
    os.makedirs(output_dir, exist_ok=True)
    
    avatars = [
        ("M1", BACKGROUND_COLORS[0]),  # Male 1
        ("M2", BACKGROUND_COLORS[1]),  # Male 2
        ("F1", BACKGROUND_COLORS[2]),  # Female 1
        ("F2", BACKGROUND_COLORS[3]),  # Female 2
    ]
    
    for i, (text, color) in enumerate(avatars, 1):
        output_path = os.path.join(output_dir, f'avatar{i}.png')
        generate_avatar(text, output_path, color)
    
    print(f"Generated default avatars in {output_dir}")

if __name__ == '__main__':
    # Generate avatars in the static/images/avatars directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    avatars_dir = os.path.join(script_dir, 'static', 'images', 'avatars')
    generate_default_avatars(avatars_dir)
