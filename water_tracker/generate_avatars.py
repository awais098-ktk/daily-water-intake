"""
Avatar generator for Water Intake Tracker
Creates default avatar images for user profiles
"""

import os
import random
import cairosvg
from io import BytesIO

# Define colors
BACKGROUND_COLORS = [
    "#4DA6FF",  # Blue
    "#FF6B6B",  # Red
    "#4CAF50",  # Green
    "#9C27B0",  # Purple
    "#FF9800",  # Orange
    "#00BCD4",  # Cyan
]

SKIN_TONES = [
    "#FFDBAC",  # Light
    "#F1C27D",  # Medium-light
    "#E0AC69",  # Medium
    "#C68642",  # Medium-dark
    "#8D5524",  # Dark
]

HAIR_COLORS = [
    "#090806",  # Black
    "#71491E",  # Brown
    "#FFF5E1",  # Blonde
    "#B38867",  # Light brown
    "#50312F",  # Dark brown
    "#A7A7A7",  # Grey
    "#D73B3E",  # Red
]

# Define avatar templates
MALE_AVATAR_TEMPLATE = """
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <circle cx="100" cy="100" r="100" fill="{background_color}" />
    
    <!-- Body -->
    <rect x="70" y="120" width="60" height="80" fill="{skin_tone}" />
    
    <!-- Head -->
    <circle cx="100" cy="80" r="40" fill="{skin_tone}" />
    
    <!-- Hair -->
    <path d="M60 80 Q 100 10 140 80 L 140 70 Q 100 0 60 70 Z" fill="{hair_color}" />
    
    <!-- Eyes -->
    <circle cx="85" cy="75" r="5" fill="#FFFFFF" />
    <circle cx="115" cy="75" r="5" fill="#FFFFFF" />
    <circle cx="85" cy="75" r="2" fill="#000000" />
    <circle cx="115" cy="75" r="2" fill="#000000" />
    
    <!-- Mouth -->
    <path d="M90 95 Q 100 105 110 95" stroke="#000000" stroke-width="2" fill="none" />
</svg>
"""

FEMALE_AVATAR_TEMPLATE = """
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <circle cx="100" cy="100" r="100" fill="{background_color}" />
    
    <!-- Body -->
    <path d="M70 120 L 100 180 L 130 120 Z" fill="{skin_tone}" />
    
    <!-- Head -->
    <circle cx="100" cy="80" r="40" fill="{skin_tone}" />
    
    <!-- Hair -->
    <path d="M60 80 Q 100 0 140 80 L 140 90 Q 100 20 60 90 Z" fill="{hair_color}" />
    <path d="M60 80 Q 60 120 80 130 L 70 80 Z" fill="{hair_color}" />
    <path d="M140 80 Q 140 120 120 130 L 130 80 Z" fill="{hair_color}" />
    
    <!-- Eyes -->
    <circle cx="85" cy="75" r="5" fill="#FFFFFF" />
    <circle cx="115" cy="75" r="5" fill="#FFFFFF" />
    <circle cx="85" cy="75" r="2" fill="#000000" />
    <circle cx="115" cy="75" r="2" fill="#000000" />
    
    <!-- Mouth -->
    <path d="M90 95 Q 100 105 110 95" stroke="#000000" stroke-width="2" fill="none" />
</svg>
"""

CUSTOM_AVATAR_TEMPLATE = """
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <circle cx="100" cy="100" r="100" fill="{background_color}" />
    
    <!-- Body -->
    <rect x="80" y="120" width="40" height="60" rx="20" fill="{skin_tone}" />
    
    <!-- Head -->
    <circle cx="100" cy="80" r="40" fill="{skin_tone}" />
    
    <!-- Hair -->
    <path d="M70 60 Q 100 20 130 60 L 130 80 Q 100 40 70 80 Z" fill="{hair_color}" />
    
    <!-- Eyes -->
    <circle cx="85" cy="75" r="5" fill="#FFFFFF" />
    <circle cx="115" cy="75" r="5" fill="#FFFFFF" />
    <circle cx="85" cy="75" r="2" fill="#000000" />
    <circle cx="115" cy="75" r="2" fill="#000000" />
    
    <!-- Mouth -->
    <path d="M90 95 Q 100 105 110 95" stroke="#000000" stroke-width="2" fill="none" />
</svg>
"""

def generate_avatar(gender, output_path):
    """Generate an avatar based on gender and save to output_path"""
    # Select random colors
    background_color = random.choice(BACKGROUND_COLORS)
    skin_tone = random.choice(SKIN_TONES)
    hair_color = random.choice(HAIR_COLORS)
    
    # Select template based on gender
    if gender == 'male':
        template = MALE_AVATAR_TEMPLATE
    elif gender == 'female':
        template = FEMALE_AVATAR_TEMPLATE
    else:
        template = CUSTOM_AVATAR_TEMPLATE
    
    # Fill in the template
    svg_content = template.format(
        background_color=background_color,
        skin_tone=skin_tone,
        hair_color=hair_color
    )
    
    # Convert SVG to PNG
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    
    # Save to file
    with open(output_path, 'wb') as f:
        f.write(png_data)
    
    return output_path

def generate_default_avatars(output_dir):
    """Generate a set of default avatars"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate male avatars
    for i in range(1, 3):
        output_path = os.path.join(output_dir, f'avatar{i}.png')
        generate_avatar('male', output_path)
    
    # Generate female avatars
    for i in range(3, 5):
        output_path = os.path.join(output_dir, f'avatar{i}.png')
        generate_avatar('female', output_path)
    
    print(f"Generated default avatars in {output_dir}")

if __name__ == '__main__':
    # Generate avatars in the static/images/avatars directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    avatars_dir = os.path.join(script_dir, 'static', 'images', 'avatars')
    generate_default_avatars(avatars_dir)
