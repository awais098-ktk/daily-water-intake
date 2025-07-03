"""
Test the image recognition functionality of the Water Intake Tracker app
"""

import os
from water_tracker.image_processing import ImageProcessor

def test_image_recognition():
    """Test the image recognition functionality"""
    # Create an image processor
    image_processor = ImageProcessor()

    # Test images
    test_images = [
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'pepsi_can.png'),
            'expected_type': 'Pepsi'
        },
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'juice_sample.png'),
            'expected_type': 'Juice'
        },
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'coffee_sample.png'),
            'expected_type': 'Coffee'
        },
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'water_sample.png'),
            'expected_type': 'Water'
        },
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'milk_sample.png'),
            'expected_type': 'Milk'
        },
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'tea_sample.png'),
            'expected_type': 'Tea'
        },
        {
            'path': os.path.join('water_tracker', 'static', 'uploads', 'containers', 'soda_sample.png'),
            'expected_type': 'Soda'
        }
    ]

    # Test each image
    for test_image in test_images:
        path = test_image['path']
        expected_type = test_image['expected_type']

        if not os.path.exists(path):
            print(f"Error: Image not found at {path}")
            continue

        # Detect the drink type
        detected_type, confidence = image_processor.detect_drink_type(path)

        # Print the results
        print(f"Image: {os.path.basename(path)}")
        print(f"Expected type: {expected_type}")
        print(f"Detected type: {detected_type}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Result: {'✓ PASS' if detected_type == expected_type else '✗ FAIL'}")
        print("-" * 50)

if __name__ == "__main__":
    test_image_recognition()
