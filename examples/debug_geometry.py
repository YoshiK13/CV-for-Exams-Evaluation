"""Debug cell geometry calculation"""
import os
import sys
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()

# Load template
template_path = os.path.join(os.path.dirname(__file__), 'template.png')
image = cv2.imread(template_path)

height, width = image.shape[:2]
print(f"Image size: {width}x{height}")

# Manually calculate what the code should produce
margin = 40
sq = 40

title_scale = 1.2
title_thickness = 2
title_font = cv2.FONT_HERSHEY_SIMPLEX
(t_w, t_h), _ = cv2.getTextSize("Exam", title_font, title_scale, title_thickness)
title_y = margin + t_h
print(f"Title y: {title_y}, t_h: {t_h}")

box_top = title_y + 15
box_height = 50
print(f"Box top: {box_top}, box height: {box_height}")

table_top = box_top + box_height + 20
print(f"Table top: {table_top}")

content_left = margin + sq + 15
content_right = width - margin - sq - 15
content_w = content_right - content_left
print(f"Content: left={content_left}, right={content_right}, width={content_w}")

table_w = int(content_w * 0.95)
table_left = content_left + (content_w - table_w) // 2
print(f"Table: left={table_left}, width={table_w}")

available_height = height - table_top - margin - sq - 20
table_height = int(available_height * 0.85)
print(f"Available height: {available_height}, table height: {table_height}")

n_cols = 10
n_choice_rows = 4
header_h = max(18, int(table_height * 0.10))
remaining_h = table_height - header_h
choice_row_h = max(15, int(remaining_h / n_choice_rows))
print(f"Header height: {header_h}, choice row height: {choice_row_h}")
print(f"Remaining height: {remaining_h}, calculated per row: {remaining_h / n_choice_rows}")

label_col_w = max(30, int(table_w * 0.08))
q_area_w = table_w - label_col_w
cell_w = q_area_w / n_cols
print(f"Label col width: {label_col_w}, question area: {q_area_w}, cell width: {cell_w}")

# Now check actual cell coordinates
cells = recognizer.extract_answer_cells(
    image, num_questions=10, choices_per_question=4,
    template_size=(800, 1000), margin=40, alignment_square_size=40
)

print(f"\nQ1 cells:")
for i, (x, y, w, h) in enumerate(cells[0]):
    print(f"  Choice {chr(ord('A')+i)}: x={x}, y={y}, w={w}, h={h}")
