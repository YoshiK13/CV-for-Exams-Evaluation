"""Example: generate an exam answer sheet template and save as PNG

Run from repo root:
    python3 examples/generate_exam_sheet.py
"""
import os
import sys
import cv2
import numpy as np

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

OUT = os.path.join(os.path.dirname(__file__), 'generated_template.png')


def main():
    recognizer = PatternRecognizer()
    img = recognizer.generate_exam_sheet_template(
        title="Sample Exam",
        num_questions=10,
        choices_per_question=4,
        sheet_size=(1400, 2000),
    )
    # Save as PNG
    cv2.imwrite(OUT, img)
    print(f"Generated template saved to: {OUT}")


if __name__ == '__main__':
    main()
