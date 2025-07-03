"""
Create a test image for orange juice detection
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create the directory if it doesn't exist
os.makedirs("water_tracker/static/uploads", exist_ok=True)

# Create a simple orange juice bottle image with text
img = Image.new('RGB', (400, 600), color=(255, 255, 255))  # White background
draw = ImageDraw.Draw(img)

# Draw an orange rectangle to represent the juice
draw.rectangle([(50, 100), (350, 500)], fill=(255, 165, 0))  # Orange color

# Add text to the image
try:
    # Try to load a font
    font = ImageFont.truetype("arial.ttf", 36)
except:
    # Fall back to default font
    font = ImageFont.load_default()

# Draw the text "ORANGE JUICE" and "1L"
draw.text((100, 250), "ORANGE JUICE", fill=(0, 0, 0), font=font)
draw.text((180, 350), "1L", fill=(0, 0, 0), font=font)

# Save the image
img.save("water_tracker/static/uploads/orange_juice_test.jpg")

print("Test image created at water_tracker/static/uploads/orange_juice_test.jpg")
print("You can now test the OCR with this image")
