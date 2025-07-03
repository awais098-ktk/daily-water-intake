import os
import sys
from PIL import Image
from water_tracker.ocr import OCRProcessor

def test_ocr_with_image(image_path):
    """Test the OCR processor with a specific image"""
    print(f"\n===== Testing OCR with image: {os.path.basename(image_path)} =====")
    
    # Create OCR processor
    ocr = OCRProcessor()
    
    # Process the image
    result = ocr.process_label(image_path)
    
    # Print the results
    if result['success']:
        print(f"Detected drink type: {result['drink_type']}")
        print(f"Detected volume: {result['volume_ml']}ml")
        print(f"Extracted text: {result['text']}")
        if 'confidence' in result:
            print(f"Confidence: {result['confidence']}%")
    else:
        print(f"Error processing image: {result.get('error', 'Unknown error')}")
    
    print("=" * 50)
    return result

def main():
    """Main test function"""
    # Get the test images directory
    test_dir = os.path.join('water_tracker', 'static', 'uploads')
    
    # Check if a specific image was provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if not os.path.exists(image_path):
            # Try to find it in the test directory
            image_path = os.path.join(test_dir, os.path.basename(image_path))
        
        if os.path.exists(image_path):
            test_ocr_with_image(image_path)
        else:
            print(f"Error: Image not found: {image_path}")
        return
    
    # Test with all images in the test directory
    if os.path.exists(test_dir):
        image_files = [f for f in os.listdir(test_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        if not image_files:
            print(f"No image files found in {test_dir}")
            return
        
        print(f"Found {len(image_files)} image files to test")
        
        for image_file in image_files:
            image_path = os.path.join(test_dir, image_file)
            test_ocr_with_image(image_path)
    else:
        print(f"Test directory not found: {test_dir}")

if __name__ == "__main__":
    main()
