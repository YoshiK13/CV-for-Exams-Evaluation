"""Debug alignment markers"""
import os
import sys
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()

# Load filled exam
filled_path = os.path.join(os.path.dirname(__file__), 'filled_exam.png')
image = cv2.imread(filled_path)

# Find markers
markers = recognizer.find_alignment_squares(image, min_area=800)
print(f"Found {len(markers)} alignment markers:")
for i, (x, y) in enumerate(markers):
    print(f"  Marker {i+1}: ({x}, {y})")

# Draw markers on image for visualization
debug_img = image.copy()
for (x, y) in markers:
    cv2.circle(debug_img, (x, y), 10, (0, 255, 0), -1)
    cv2.circle(debug_img, (x, y), 15, (0, 255, 0), 2)

debug_path = os.path.join(os.path.dirname(__file__), 'debug_markers.png')
cv2.imwrite(debug_path, debug_img)
print(f"\nMarkers visualization saved: {debug_path}")
