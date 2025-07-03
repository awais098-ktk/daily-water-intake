"""
Create sample drink images for testing the Water Intake Tracker app
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_juice_image():
    """Create a sample juice image"""
    # Create a new image with an orange background
    img = Image.new('RGB', (300, 500), color=(255, 165, 0))
    draw = ImageDraw.Draw(img)

    # Draw a bottle shape
    # Bottle neck
    draw.rectangle((125, 50, 175, 150), fill=(255, 200, 50), outline=(0, 0, 0), width=2)
    # Bottle cap
    draw.rectangle((120, 30, 180, 50), fill=(50, 50, 50), outline=(0, 0, 0), width=2)
    # Bottle body
    draw.rectangle((100, 150, 200, 400), fill=(255, 200, 50), outline=(0, 0, 0), width=2)

    # Add some juice details
    # Liquid level
    draw.rectangle((100, 250, 200, 400), fill=(255, 140, 0), outline=(0, 0, 0), width=1)
    # Bubbles
    draw.ellipse((120, 270, 130, 280), fill=(255, 220, 150))
    draw.ellipse((150, 290, 165, 305), fill=(255, 220, 150))
    draw.ellipse((130, 330, 145, 345), fill=(255, 220, 150))
    draw.ellipse((170, 350, 180, 360), fill=(255, 220, 150))

    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        draw.text((90, 180), "ORANGE", fill=(0, 0, 0), font=font)
        draw.text((110, 220), "JUICE", fill=(0, 0, 0), font=font)
        draw.text((120, 420), "350ml", fill=(0, 0, 0), font=small_font)
    except:
        # If font handling fails, use simple text
        draw.text((90, 180), "ORANGE", fill=(0, 0, 0))
        draw.text((110, 220), "JUICE", fill=(0, 0, 0))
        draw.text((120, 420), "350ml", fill=(0, 0, 0))

    # Save the image
    containers_folder = os.path.join('water_tracker', 'static', 'uploads', 'containers')
    os.makedirs(containers_folder, exist_ok=True)

    img.save(os.path.join(containers_folder, 'juice_sample.png'))
    print(f"Created juice sample image at {os.path.join(containers_folder, 'juice_sample.png')}")

def create_coffee_image():
    """Create a sample coffee image"""
    # Create a new image with a brown background
    img = Image.new('RGB', (300, 300), color=(139, 69, 19))
    draw = ImageDraw.Draw(img)

    # Draw a coffee mug
    # Mug body
    draw.rectangle((75, 50, 225, 200), fill=(111, 78, 55), outline=(0, 0, 0), width=2)
    # Mug handle
    draw.arc((225, 75, 275, 175), start=270, end=90, fill=(0, 0, 0), width=5)

    # Coffee liquid
    draw.rectangle((75, 50, 225, 150), fill=(80, 40, 20), outline=(0, 0, 0), width=1)
    # Coffee foam
    draw.rectangle((75, 50, 225, 70), fill=(200, 173, 127), outline=(0, 0, 0), width=1)

    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        draw.text((90, 220), "COFFEE", fill=(255, 255, 255), font=font)
        draw.text((120, 260), "200ml", fill=(255, 255, 255), font=small_font)
    except:
        # If font handling fails, use simple text
        draw.text((90, 220), "COFFEE", fill=(255, 255, 255))
        draw.text((120, 260), "200ml", fill=(255, 255, 255))

    # Save the image
    containers_folder = os.path.join('water_tracker', 'static', 'uploads', 'containers')
    os.makedirs(containers_folder, exist_ok=True)

    img.save(os.path.join(containers_folder, 'coffee_sample.png'))
    print(f"Created coffee sample image at {os.path.join(containers_folder, 'coffee_sample.png')}")

def create_water_image():
    """Create a sample water image"""
    # Create a new image with a light blue background
    img = Image.new('RGB', (300, 500), color=(200, 230, 255))
    draw = ImageDraw.Draw(img)

    # Draw a water bottle shape
    # Bottle neck
    draw.rectangle((125, 50, 175, 150), fill=(220, 240, 255), outline=(0, 0, 0), width=2)
    # Bottle cap
    draw.rectangle((120, 30, 180, 50), fill=(0, 120, 200), outline=(0, 0, 0), width=2)
    # Bottle body
    draw.rectangle((100, 150, 200, 400), fill=(220, 240, 255), outline=(0, 0, 0), width=2)

    # Add some water details
    # Water level
    draw.rectangle((100, 250, 200, 400), fill=(180, 220, 255), outline=(0, 0, 0), width=1)
    # Bubbles
    draw.ellipse((120, 270, 130, 280), fill=(240, 250, 255))
    draw.ellipse((150, 290, 165, 305), fill=(240, 250, 255))
    draw.ellipse((130, 330, 145, 345), fill=(240, 250, 255))
    draw.ellipse((170, 350, 180, 360), fill=(240, 250, 255))

    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        draw.text((100, 180), "SPRING", fill=(0, 100, 200), font=font)
        draw.text((100, 220), "WATER", fill=(0, 100, 200), font=font)
        draw.text((120, 420), "500ml", fill=(0, 100, 200), font=small_font)
    except:
        # If font handling fails, use simple text
        draw.text((100, 180), "SPRING", fill=(0, 100, 200))
        draw.text((100, 220), "WATER", fill=(0, 100, 200))
        draw.text((120, 420), "500ml", fill=(0, 100, 200))

    # Save the image
    containers_folder = os.path.join('water_tracker', 'static', 'uploads', 'containers')
    os.makedirs(containers_folder, exist_ok=True)

    img.save(os.path.join(containers_folder, 'water_sample.png'))
    print(f"Created water sample image at {os.path.join(containers_folder, 'water_sample.png')}")

def create_milk_image():
    """Create a sample milk image"""
    # Create a new image with a white background
    img = Image.new('RGB', (300, 400), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    # Draw a milk carton shape
    # Carton body
    draw.rectangle((75, 50, 225, 300), fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    # Carton top
    draw.polygon([(75, 50), (150, 20), (225, 50)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)

    # Add some milk details
    # Milk splash
    draw.ellipse((100, 320, 200, 350), fill=(240, 240, 240), outline=(0, 0, 0), width=1)
    draw.ellipse((120, 310, 180, 330), fill=(240, 240, 240), outline=(0, 0, 0), width=1)

    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        draw.text((120, 120), "MILK", fill=(0, 0, 0), font=font)
        draw.text((110, 220), "250ml", fill=(0, 0, 0), font=small_font)
    except:
        # If font handling fails, use simple text
        draw.text((120, 120), "MILK", fill=(0, 0, 0))
        draw.text((110, 220), "250ml", fill=(0, 0, 0))

    # Save the image
    containers_folder = os.path.join('water_tracker', 'static', 'uploads', 'containers')
    os.makedirs(containers_folder, exist_ok=True)

    img.save(os.path.join(containers_folder, 'milk_sample.png'))
    print(f"Created milk sample image at {os.path.join(containers_folder, 'milk_sample.png')}")

def create_tea_image():
    """Create a sample tea image"""
    # Create a new image with a light brown background
    img = Image.new('RGB', (300, 300), color=(210, 180, 140))
    draw = ImageDraw.Draw(img)

    # Draw a tea cup
    # Cup body
    draw.rectangle((75, 50, 225, 200), fill=(245, 222, 179), outline=(0, 0, 0), width=2)
    # Cup handle
    draw.arc((225, 75, 275, 175), start=270, end=90, fill=(0, 0, 0), width=5)
    # Saucer
    draw.ellipse((50, 200, 250, 230), fill=(245, 222, 179), outline=(0, 0, 0), width=2)

    # Tea liquid
    draw.rectangle((75, 50, 225, 150), fill=(139, 69, 19), outline=(0, 0, 0), width=1)

    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        draw.text((120, 240), "TEA", fill=(0, 0, 0), font=font)
        draw.text((110, 270), "200ml", fill=(0, 0, 0), font=small_font)
    except:
        # If font handling fails, use simple text
        draw.text((120, 240), "TEA", fill=(0, 0, 0))
        draw.text((110, 270), "200ml", fill=(0, 0, 0))

    # Save the image
    containers_folder = os.path.join('water_tracker', 'static', 'uploads', 'containers')
    os.makedirs(containers_folder, exist_ok=True)

    img.save(os.path.join(containers_folder, 'tea_sample.png'))
    print(f"Created tea sample image at {os.path.join(containers_folder, 'tea_sample.png')}")

def create_soda_image():
    """Create a sample soda image"""
    # Create a new image with a red background
    img = Image.new('RGB', (300, 500), color=(200, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a soda can shape
    # Can body
    draw.rectangle((100, 50, 200, 400), fill=(220, 0, 0), outline=(0, 0, 0), width=2)
    # Can top
    draw.ellipse((100, 30, 200, 70), fill=(200, 200, 200), outline=(0, 0, 0), width=2)
    # Can tab
    draw.rectangle((140, 40, 160, 50), fill=(150, 150, 150), outline=(0, 0, 0), width=1)

    # Add some soda details
    # Bubbles
    draw.ellipse((120, 100, 130, 110), fill=(255, 255, 255))
    draw.ellipse((150, 120, 165, 135), fill=(255, 255, 255))
    draw.ellipse((130, 160, 145, 175), fill=(255, 255, 255))
    draw.ellipse((170, 200, 180, 210), fill=(255, 255, 255))

    # Add text
    try:
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # If Arial is not available, try a different font
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", 36)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 24)
            except:
                # If no TrueType fonts are available, use the default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

        draw.text((120, 150), "SODA", fill=(255, 255, 255), font=font)
        draw.text((120, 350), "330ml", fill=(255, 255, 255), font=small_font)
    except:
        # If font handling fails, use simple text
        draw.text((120, 150), "SODA", fill=(255, 255, 255))
        draw.text((120, 350), "330ml", fill=(255, 255, 255))

    # Save the image
    containers_folder = os.path.join('water_tracker', 'static', 'uploads', 'containers')
    os.makedirs(containers_folder, exist_ok=True)

    img.save(os.path.join(containers_folder, 'soda_sample.png'))
    print(f"Created soda sample image at {os.path.join(containers_folder, 'soda_sample.png')}")

if __name__ == "__main__":
    create_juice_image()
    create_coffee_image()
    create_water_image()
    create_milk_image()
    create_tea_image()
    create_soda_image()
