"""
Basic Pattern Recognition Example
Demonstrates how to use the PatternRecognizer class for exam image analysis.
"""

import sys
import os
import cv2
import numpy as np

# Add parent directory to path to import exam_evaluator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exam_evaluator import PatternRecognizer


def create_sample_exam_image(output_path: str):
    """
    Create a sample exam image with circles (answer bubbles) for testing.
    
    Args:
        output_path: Path where the sample image will be saved
    """
    # Create a white canvas
    height, width = 600, 800
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add title text
    cv2.putText(image, "Sample Exam - Multiple Choice", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Draw sample questions with answer bubbles
    y_start = 120
    questions = 5
    
    for i in range(questions):
        y_pos = y_start + (i * 80)
        
        # Question number
        cv2.putText(image, f"Question {i+1}:", (50, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        # Draw answer bubbles (A, B, C, D)
        for j, letter in enumerate(['A', 'B', 'C', 'D']):
            x_pos = 250 + (j * 100)
            
            # Draw circle (answer bubble)
            cv2.circle(image, (x_pos, y_pos - 10), 15, (0, 0, 0), 2)
            
            # Add letter label
            cv2.putText(image, letter, (x_pos - 8, y_pos + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Fill some bubbles as "marked" answers
            if (i == 0 and j == 1) or (i == 2 and j == 2) or (i == 4 and j == 0):
                cv2.circle(image, (x_pos, y_pos - 10), 10, (0, 0, 0), -1)
    
    # Save the image
    cv2.imwrite(output_path, image)
    print(f"Sample exam image created: {output_path}")


def main():
    """Main function demonstrating pattern recognition capabilities."""
    
    print("=" * 60)
    print("OpenCV Pattern Recognition Demo for Exam Evaluation")
    print("=" * 60)
    
    # Initialize the pattern recognizer
    recognizer = PatternRecognizer()
    print(f"\n✓ OpenCV version: {recognizer.opencv_version}")
    
    # Create a sample exam image
    sample_image_path = os.path.join(os.path.dirname(__file__), 'sample_exam.png')
    create_sample_exam_image(sample_image_path)
    
    # Load and process the image
    print(f"\n1. Loading image: {sample_image_path}")
    image = recognizer.load_image(sample_image_path)
    
    if image is None:
        print("Error: Failed to load image")
        return
    
    # Display image information
    print("\n2. Image Information:")
    info = recognizer.get_image_info(image)
    for key, value in info.items():
        print(f"   - {key}: {value}")
    
    # Convert to grayscale
    print("\n3. Converting to grayscale...")
    gray = recognizer.convert_to_grayscale(image)
    print(f"   ✓ Grayscale image shape: {gray.shape}")
    
    # Detect edges
    print("\n4. Detecting edges using Canny edge detection...")
    edges = recognizer.detect_edges(gray, low_threshold=50, high_threshold=150)
    edge_count = np.count_nonzero(edges)
    print(f"   ✓ Edge pixels detected: {edge_count}")
    
    # Apply threshold
    print("\n5. Applying binary threshold...")
    binary = recognizer.apply_threshold(gray, threshold_value=127)
    print(f"   ✓ Binary image created")
    
    # Find contours
    print("\n6. Finding contours...")
    contours, hierarchy = recognizer.find_contours(binary)
    print(f"   ✓ Number of contours found: {len(contours)}")
    
    # Detect circles (answer bubbles)
    print("\n7. Detecting circles (answer bubbles)...")
    circles = recognizer.detect_circles(gray, min_radius=10, max_radius=30)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"   ✓ Number of circles detected: {len(circles[0])}")
        
        # Draw detected circles on the image
        output_image = image.copy()
        for circle in circles[0, :]:
            center = (circle[0], circle[1])
            radius = circle[2]
            # Draw circle outline
            cv2.circle(output_image, center, radius, (0, 255, 0), 2)
            # Draw center point
            cv2.circle(output_image, center, 2, (0, 0, 255), 3)
        
        output_path = os.path.join(os.path.dirname(__file__), 'detected_circles.png')
        cv2.imwrite(output_path, output_image)
        print(f"   ✓ Circles visualization saved: {output_path}")
    else:
        print("   ✗ No circles detected")
    
    # Preprocess the exam image
    print("\n8. Preprocessing exam image (complete pipeline)...")
    preprocessed = recognizer.preprocess_exam_image(sample_image_path)
    if preprocessed is not None:
        preprocessed_path = os.path.join(os.path.dirname(__file__), 'preprocessed_exam.png')
        cv2.imwrite(preprocessed_path, preprocessed)
        print(f"   ✓ Preprocessed image saved: {preprocessed_path}")
    
    print("\n" + "=" * 60)
    print("✓ Pattern Recognition Demo Completed Successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  - {sample_image_path}")
    print(f"  - {output_path}")
    print(f"  - {preprocessed_path}")
    print("\nThe PatternRecognizer class is ready for exam evaluation tasks.")


if __name__ == "__main__":
    main()
