"""
Test script for OpenCV-based gesture recognition
This script uses only OpenCV (no MediaPipe) for basic hand detection and gesture recognition
"""

import cv2
import numpy as np
import os
import time

def create_test_image(output_path):
    """Create a test image with a hand silhouette"""
    # Create a blank image
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    img.fill(240)  # Light gray background
    
    # Draw a simple hand silhouette (peace sign)
    # Palm
    cv2.circle(img, (300, 250), 60, (200, 200, 200), -1)
    
    # Fingers (peace sign)
    # Index finger
    cv2.line(img, (300, 200), (250, 100), (200, 200, 200), 20)
    # Middle finger
    cv2.line(img, (300, 200), (350, 100), (200, 200, 200), 20)
    
    # Add text
    cv2.putText(img, "Test Hand (Peace Sign)", (150, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Save the image
    cv2.imwrite(output_path, img)
    print(f"Created test image at {output_path}")
    return img

def detect_hand_simple(image):
    """
    Simple hand detection using color thresholding
    This is a very basic approach and won't work well in real-world scenarios
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Threshold to get hand region (assuming hand is lighter than background)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour (assuming it's the hand)
    if contours:
        hand_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(hand_contour)
        
        # Draw rectangle around hand
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Get convex hull and defects for finger detection
        hull = cv2.convexHull(hand_contour, returnPoints=False)
        
        # Check if hull has enough points
        if len(hull) > 3:
            try:
                defects = cv2.convexityDefects(hand_contour, hull)
                
                # Count fingers based on defects
                finger_count = 0
                
                if defects is not None:
                    for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]
                        start = tuple(hand_contour[s][0])
                        end = tuple(hand_contour[e][0])
                        far = tuple(hand_contour[f][0])
                        
                        # Calculate angle between fingers
                        a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                        b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                        c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                        angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
                        
                        # If angle is less than 90 degrees, it's likely a finger
                        if angle <= np.pi / 2:
                            finger_count += 1
                            # Mark the defect point
                            cv2.circle(image, far, 5, [0, 0, 255], -1)
                
                # Add 1 for the thumb
                finger_count += 1
                
                # Determine gesture based on finger count
                gesture = "Unknown"
                if finger_count == 2:
                    gesture = "Peace Sign"
                elif finger_count == 1:
                    gesture = "Pointing"
                elif finger_count == 5:
                    gesture = "Open Hand"
                
                # Add text to image
                cv2.putText(image, f"Gesture: {gesture} ({finger_count} fingers)", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                return True, image, gesture
            except:
                pass
    
    # If no hand detected or processing failed
    cv2.putText(image, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    return False, image, "None"

def test_with_webcam():
    """Test hand detection with webcam"""
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return False
    
    print("Webcam opened successfully. Press 'q' to quit.")
    
    while True:
        # Read frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Detect hand
        success, processed_frame, gesture = detect_hand_simple(frame)
        
        # Display result
        cv2.imshow('Hand Detection', processed_frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    return True

def test_with_image(image_path):
    """Test hand detection with a static image"""
    # Read image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return False
    
    # Detect hand
    success, processed_image, gesture = detect_hand_simple(image)
    
    # Save result
    output_path = image_path.replace('.jpg', '_processed.jpg')
    cv2.imwrite(output_path, processed_image)
    
    print(f"Processed image saved to {output_path}")
    print(f"Detected gesture: {gesture}")
    
    # Display result
    cv2.imshow('Hand Detection', processed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return success

def main():
    """Main function"""
    print("OpenCV Gesture Recognition Test")
    print("==============================")
    
    # Create test directory
    os.makedirs('test_images', exist_ok=True)
    
    # Create test image
    test_image_path = os.path.join('test_images', 'test_hand.jpg')
    create_test_image(test_image_path)
    
    # Test with static image
    print("\nTesting with static image...")
    test_with_image(test_image_path)
    
    # Test with webcam if available
    print("\nTesting with webcam...")
    try:
        test_with_webcam()
    except Exception as e:
        print(f"Error testing with webcam: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
