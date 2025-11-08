"""Debug script to check cell detection"""
import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()

# Load filled exam
filled_path = os.path.join(os.path.dirname(__file__), 'filled_exam.png')
image = cv2.imread(filled_path)

# Convert to binary
binary = recognizer.convert_to_black_and_white(image)

# Get cells
cells = recognizer.extract_answer_cells(
    image, num_questions=10, choices_per_question=4,
    template_size=(800, 1000), margin=40, alignment_square_size=40
)

# Check first question cells
print("Checking Question 1 cells:")
for i, (x, y, w, h) in enumerate(cells[0]):
    cell = binary[y:y+h, x:x+w]
    black_pixels = np.sum(cell == 0)
    total_pixels = cell.size
    ratio = black_pixels / total_pixels if total_pixels > 0 else 0
    is_marked = recognizer.is_cell_marked(binary, (x, y, w, h), 0.30)
    print(f"  Choice {i} (x={x}, y={y}, w={w}, h={h}): black_ratio={ratio:.4f}, marked={is_marked}")
    
    # Save cell for inspection
    cell_path = os.path.join(os.path.dirname(__file__), f'debug_cell_q1_c{i}.png')
    cv2.imwrite(cell_path, cell)

print(f"\nBinary image shape: {binary.shape}")
print(f"Binary unique values: {np.unique(binary)}")
