"""Visualize marked cells on template"""
import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()

# Generate template
template = recognizer.generate_exam_sheet_template(
    title="Sample Exam",
    num_questions=10,
    choices_per_question=4,
    sheet_size=(800, 1000),
    margin=40,
    alignment_square_size=40
)

# Get cell coordinates
cells = recognizer.extract_answer_cells(
    template, num_questions=10, choices_per_question=4,
    template_size=(800, 1000), margin=40, alignment_square_size=40
)

# Visualize cells with colored rectangles
debug_img = template.copy()

# Mark the first question's cells with different colors
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Blue, Green, Red, Yellow
for i, (x, y, w, h) in enumerate(cells[0]):
    cv2.rectangle(debug_img, (x, y), (x+w, y+h), colors[i], 2)
    print(f"Q1 Choice {chr(ord('A')+i)}: x={x}, y={y}, w={w}, h={h}")

debug_path = os.path.join(os.path.dirname(__file__), 'debug_cells_visual.png')
cv2.imwrite(debug_path, debug_img)
print(f"\nCell visualization saved: {debug_path}")

# Now mark answer A (first cell)
marked_img = template.copy()
x, y, w, h = cells[0][0]
center_x = x + w // 2
center_y = y + h // 2
radius = min(w, h) // 2 - 2
cv2.circle(marked_img, (center_x, center_y), radius, (0, 0, 0), -1)
print(f"\nMarked cell at center ({center_x}, {center_y}) with radius {radius}")

marked_path = os.path.join(os.path.dirname(__file__), 'debug_marked.png')
cv2.imwrite(marked_path, marked_img)

# Check if it's detected
binary = recognizer.convert_to_black_and_white(marked_img)
is_marked = recognizer.is_cell_marked(binary, (x, y, w, h), 0.30)

cell_region = binary[y:y+h, x:x+w]
black_pixels = np.sum(cell_region == 0)
total_pixels = cell_region.size
ratio = black_pixels / total_pixels

print(f"Detection: marked={is_marked}, black_ratio={ratio:.4f}, threshold=0.30")
print(f"Marked image saved: {marked_path}")
