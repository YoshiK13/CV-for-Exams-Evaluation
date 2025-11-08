"""Example: Complete exam evaluation workflow

This example demonstrates:
1. Generate an exam template
2. Simulate a filled exam (you would normally scan this)
3. Process the exam to detect marked answers

Run from repo root:
    python3 examples/demo_complete_workflow.py
"""
import os
import sys
import cv2
import numpy as np

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

OUT_DIR = os.path.dirname(__file__)


def main():
    recognizer = PatternRecognizer()
    
    print("=" * 60)
    print("STEP 1: Generate exam template")
    print("=" * 60)
    
    # Generate template
    num_questions = 10
    choices_per_question = 4
    
    template = recognizer.generate_exam_sheet_template(
        title="Sample Exam",
        num_questions=num_questions,
        choices_per_question=choices_per_question,
        sheet_size=(800, 1000),
        margin=40,
        alignment_square_size=40
    )
    
    template_path = os.path.join(OUT_DIR, 'template.png')
    cv2.imwrite(template_path, template)
    print(f"✓ Template generated: {template_path}")
    print(f"  Questions: {num_questions}, Choices: {choices_per_question}")
    
    print("\n" + "=" * 60)
    print("STEP 2: Simulate filled exam (marking some answers)")
    print("=" * 60)
    
    # Simulate a student filling out the exam
    # Mark answers: Q1=A, Q2=C, Q3=B, Q4=D, Q5=A, Q6=B, Q7=C, Q8=A, Q9=D, Q10=B
    filled_exam = template.copy()
    
    # Get cell coordinates
    cells = recognizer.extract_answer_cells(
        filled_exam, num_questions, choices_per_question,
        template_size=(800, 1000), margin=40, alignment_square_size=40
    )
    
    # Simulate marking (fill in some cells)
    marked_answers = [0, 2, 1, 3, 0, 1, 2, 0, 3, 1]  # A, C, B, D, A, B, C, A, D, B
    
    for q_idx, answer_idx in enumerate(marked_answers):
        if q_idx < len(cells) and answer_idx < len(cells[q_idx]):
            x, y, w, h = cells[q_idx][answer_idx]
            # Draw a filled circle to simulate student marking
            center_x = x + w // 2
            center_y = y + h // 2
            radius = min(w, h) // 2 - 2  # Larger mark
            cv2.circle(filled_exam, (center_x, center_y), radius, (0, 0, 0), -1)
    
    filled_path = os.path.join(OUT_DIR, 'filled_exam.png')
    cv2.imwrite(filled_path, filled_exam)
    print(f"✓ Filled exam created: {filled_path}")
    print(f"  Marked answers: {['ABCD'[i] for i in marked_answers]}")
    
    print("\n" + "=" * 60)
    print("STEP 3: Process exam sheet (detect answers)")
    print("=" * 60)
    
    # Process the filled exam
    result = recognizer.process_exam_sheet(
        filled_path,
        num_questions=num_questions,
        choices_per_question=choices_per_question,
        template_size=(800, 1000),
        margin=40,
        alignment_square_size=40,
        mark_threshold=0.15
    )
    
    if result['success']:
        print(f"✓ Processing successful!")
        print(f"\nDetected answers:")
        detected = result['answers']
        for i, answer in enumerate(detected):
            question_num = i + 1
            if answer is not None:
                answer_letter = 'ABCD'[answer]
                expected_letter = 'ABCD'[marked_answers[i]]
                match = "✓" if answer == marked_answers[i] else "✗"
                print(f"  Q{question_num}: {answer_letter} (expected: {expected_letter}) {match}")
            else:
                print(f"  Q{question_num}: INVALID (no answer or multiple answers marked)")
        
        # Save aligned image
        aligned_path = os.path.join(OUT_DIR, 'aligned_exam.png')
        cv2.imwrite(aligned_path, result['aligned_image'])
        print(f"\n✓ Aligned image saved: {aligned_path}")
        
        # Also save binary version for inspection
        binary = recognizer.convert_to_black_and_white(result['aligned_image'])
        binary_path = os.path.join(OUT_DIR, 'binary_exam.png')
        cv2.imwrite(binary_path, binary)
        print(f"✓ Binary image saved: {binary_path}")
        
    else:
        print(f"✗ Processing failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
