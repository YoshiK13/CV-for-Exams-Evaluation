"""Example: Simulate realistic scanned exam with rotation/skew

This demonstrates the alignment correction capability by:
1. Generating a template
2. Filling in some answers
3. Simulating a skewed/rotated scan
4. Processing it to correct alignment and detect answers

Run from repo root:
    python3 examples/demo_alignment_correction.py
"""
import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

OUT_DIR = os.path.dirname(__file__)


def main():
    recognizer = PatternRecognizer()
    
    print("=" * 60)
    print("DEMONSTRATION: Alignment Correction")
    print("=" * 60)
    
    # Generate template
    num_questions = 10
    choices_per_question = 4
    
    template = recognizer.generate_exam_sheet_template(
        title="Test Exam",
        num_questions=num_questions,
        choices_per_question=choices_per_question,
        sheet_size=(800, 1000),
        margin=40,
        alignment_square_size=40
    )
    
    print("\n1. Generated template (800x1000)")
    
    # Get cell coordinates and mark answers
    cells = recognizer.extract_answer_cells(
        template, num_questions, choices_per_question,
        template_size=(800, 1000), margin=40, alignment_square_size=40
    )
    
    filled_exam = template.copy()
    marked_answers = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1]  # A, B, C, D, A, B, C, D, A, B
    
    for q_idx, answer_idx in enumerate(marked_answers):
        if q_idx < len(cells) and answer_idx < len(cells[q_idx]):
            x, y, w, h = cells[q_idx][answer_idx]
            cv2.circle(filled_exam, (x + w//2, y + h//2), min(w, h)//2 - 2, (0, 0, 0), -1)
    
    print(f"2. Filled exam with answers: {['ABCD'[i] for i in marked_answers]}")
    
    # Simulate a skewed scan: rotate and apply perspective transform
    height, width = filled_exam.shape[:2]
    
    # Create a rotation matrix (rotate 5 degrees)
    angle = 5
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calculate new bounding dimensions
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    new_width = int((height * sin) + (width * cos))
    new_height = int((height * cos) + (width * sin))
    
    # Adjust rotation matrix for translation
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
    
    # Apply rotation
    rotated = cv2.warpAffine(filled_exam, rotation_matrix, (new_width, new_height), 
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    
    print(f"3. Simulated skewed scan (rotated 5°, size: {new_width}x{new_height})")
    
    # Save skewed version
    skewed_path = os.path.join(OUT_DIR, 'skewed_exam.png')
    cv2.imwrite(skewed_path, rotated)
    print(f"   Saved: {skewed_path}")
    
    # Now process the skewed exam
    print("\n4. Processing skewed exam...")
    print("   - Finding alignment markers...")
    markers = recognizer.find_alignment_squares(rotated, min_area=800)
    print(f"   - Found {len(markers)} markers")
    
    print("   - Aligning image...")
    aligned = recognizer.align_exam_image(
        rotated, 
        template_size=(800, 1000),
        margin=40,
        alignment_square_size=40
    )
    
    if aligned is None:
        print("   ✗ Alignment failed!")
        return
    
    print("   ✓ Alignment successful!")
    
    # Save aligned version
    aligned_path = os.path.join(OUT_DIR, 'corrected_exam.png')
    cv2.imwrite(aligned_path, aligned)
    print(f"   Saved: {aligned_path}")
    
    # Detect answers from aligned image
    print("\n5. Detecting answers from corrected image...")
    answers = recognizer.detect_marked_answers(
        aligned,
        num_questions=num_questions,
        choices_per_question=choices_per_question,
        template_size=(800, 1000),
        margin=40,
        alignment_square_size=40,
        mark_threshold=0.15
    )
    
    print("\n6. Results:")
    print("-" * 60)
    all_correct = True
    for i, (detected, expected) in enumerate(zip(answers, marked_answers)):
        if detected is not None:
            detected_letter = 'ABCD'[detected]
            expected_letter = 'ABCD'[expected]
            match = "✓" if detected == expected else "✗"
            if detected != expected:
                all_correct = False
            print(f"  Q{i+1}: {detected_letter} (expected: {expected_letter}) {match}")
        else:
            all_correct = False
            print(f"  Q{i+1}: INVALID (expected: {'ABCD'[expected]}) ✗")
    
    print("-" * 60)
    if all_correct:
        print("✓ All answers detected correctly despite rotation!")
    else:
        print("⚠ Some answers were not detected correctly")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey Points:")
    print("- The alignment markers allow automatic correction of rotation/skew")
    print("- The system can handle images that are not perfectly aligned")
    print("- This works with real scanned exams that may be slightly rotated")


if __name__ == '__main__':
    main()
