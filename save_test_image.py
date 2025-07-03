"""
Script to save a test image for OCR testing
"""

import os
import shutil
from PIL import Image

# Create the directory if it doesn't exist
os.makedirs("static/uploads", exist_ok=True)

# Create a simple orange juice bottle image
# This is just a placeholder - we'll use the actual image from the UI
img = Image.new('RGB', (300, 500), color=(255, 165, 0))  # Orange color
img.save("static/uploads/orange_juice_test.jpg")

print("Test image saved to static/uploads/orange_juice_test.jpg")
print("Please replace this with the actual orange juice image from the UI")
