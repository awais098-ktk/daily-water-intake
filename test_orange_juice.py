"""
Test script to debug orange juice OCR detection
"""

import os
import sys
from PIL import Image
import pytesseract
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the orange juice image
# This should be the path to the image that was uploaded in the UI
# You may need to adjust this path
IMAGE_PATH = "water_tracker/static/uploads/orange_juice_test.jpg"

# Set up paths for Tesseract
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\hp\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    r'C:\Users\hp\Tesseract-OCR\tesseract.exe'
]

tesseract_path = None
for path in tesseract_paths:
    if os.path.exists(path):
        tesseract_path = path
        print(f"Found Tesseract at: {path}")
        break

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def test_ocr_extraction():
    """Test OCR extraction on the orange juice image"""
    if not os.path.exists(IMAGE_PATH):
        logger.error(f"Image not found at {IMAGE_PATH}")
        return

    logger.info(f"Processing image: {IMAGE_PATH}")

    # Open the image
    img = Image.open(IMAGE_PATH)
    width, height = img.size
    logger.info(f"Image size: {width}x{height}")

    # Convert to grayscale
    img = img.convert('L')

    # Apply thresholding to make text more visible
    threshold = 150
    img = img.point(lambda p: 255 if p > threshold else 0)

    # Configure Tesseract
    custom_config = r'--oem 3 --psm 6 -l eng'

    # Extract text using Tesseract
    extracted_text = pytesseract.image_to_string(img, config=custom_config)
    extracted_text = extracted_text.strip()

    logger.info(f"Raw OCR text: {extracted_text}")

    # Try to extract volume
    volume = extract_volume(extracted_text)
    logger.info(f"Extracted volume: {volume}ml")

    # Try to extract drink type
    drink_type = extract_drink_type(extracted_text)
    logger.info(f"Extracted drink type: {drink_type}")

    return {
        'text': extracted_text,
        'volume': volume,
        'drink_type': drink_type
    }

def extract_volume(text):
    """Extract volume from text"""
    text_lower = text.lower()

    # Check for common volume patterns
    volume_patterns = {
        "1l": 1000,
        "1 l": 1000,
        "1l.": 1000,
        "1 l.": 1000,
        "1 liter": 1000,
        "1 litre": 1000,
        "1liter": 1000,
        "1litre": 1000,
        "1.0l": 1000,
        "1.0 l": 1000,
        "1000ml": 1000,
        "1000 ml": 1000,
    }

    # Check for exact matches
    for pattern, volume in volume_patterns.items():
        if pattern in text_lower:
            logger.info(f"Found exact volume match: {pattern} = {volume}ml")
            return volume

    # Try regex patterns
    volume_regex = r'(\d+)\s*ml|(\d+)\s*l(?:i?t(?:er|re)?)?|(\d+\.\d+)\s*l(?:i?t(?:er|re)?)?'
    volume_matches = re.findall(volume_regex, text_lower)

    if volume_matches:
        for match in volume_matches:
            for value in match:
                if value:
                    try:
                        # Check if this is a liter value
                        pos = text_lower.find(value)
                        if pos >= 0:
                            after_value = text_lower[pos + len(value):pos + len(value) + 10]
                            if 'l' in after_value or 'liter' in after_value or 'litre' in after_value:
                                # Convert liters to ml
                                volume = int(float(value) * 1000)
                                logger.info(f"Converted {value}L to {volume}ml")
                            else:
                                volume = int(value)
                                logger.info(f"Extracted volume from regex: {volume}ml")
                            return volume
                    except ValueError:
                        pass

    # Check for orange juice specifically
    if 'orange' in text_lower and 'juice' in text_lower:
        logger.info("Detected orange juice, defaulting to 1000ml")
        return 1000

    # Default fallback
    logger.warning("Could not extract volume, defaulting to 500ml")
    return 500

def extract_drink_type(text):
    """Extract drink type from text"""
    text_lower = text.lower()

    if 'orange' in text_lower and 'juice' in text_lower:
        return "Orange Juice"
    elif 'orange' in text_lower:
        return "Orange Juice"
    elif 'juice' in text_lower:
        return "Juice"
    else:
        return "Unknown"

if __name__ == "__main__":
    # Check if Tesseract is installed
    try:
        pytesseract.get_tesseract_version()
        logger.info("Tesseract is installed")
    except Exception as e:
        logger.error(f"Tesseract is not installed or not in PATH: {e}")
        sys.exit(1)

    # Run the test
    result = test_ocr_extraction()

    if result:
        print("\n=== TEST RESULTS ===")
        print(f"OCR Text: {result['text']}")
        print(f"Volume: {result['volume']}ml")
        print(f"Drink Type: {result['drink_type']}")
        print("===================\n")
