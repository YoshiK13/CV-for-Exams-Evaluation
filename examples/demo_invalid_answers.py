"""Example: Test invalid answer detection (multiple marks)

This example demonstrates the system correctly handling invalid cases
where a student marks more than one answer for a question.

Run from repo root:
    python3 examples/demo_invalid_answers.py
"""
import os
import sys
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

OUT_DIR = os.path.dirname(__file__)


def main():
    recognizer = PatternRecognizer()
    
    print("=" * 60)
    print("TEST: Invalid Answer Detection")
    print("=" * 60)
    
    # Generate template
    num_questions = 5
    choices_per_question = 4
    
    template = recognizer.generate_exam_sheet_template(
        title="Test Exam",
        num_questions=num_questions,
        choices_per_question=choices_per_question,
        sheet_size=(800, 1000),
        margin=40,
        alignment_square_size=40
    )
    
    # Get cell coordinates
    cells = recognizer.extract_answer_cells(
        template, num_questions, choices_per_question,
        template_size=(800, 1000), margin=40, alignment_square_size=40
    )
    
    # Create test cases:
    # Q1: Valid (only A marked)
    # Q2: Invalid (both A and C marked)
    # Q3: Valid (only D marked)
    # Q4: Invalid (no answer marked)
    # Q5: Invalid (all answers marked)
    
    filled_exam = template.copy()
    
    # Q1: Mark A only
    x, y, w, h = cells[0][0]
    cv2.circle(filled_exam, (x + w//2, y + h//2), min(w, h)//2 - 2, (0, 0, 0), -1)
    
    # Q2: Mark both A and C
    x, y, w, h = cells[1][0]
    cv2.circle(filled_exam, (x + w//2, y + h//2), min(w, h)//2 - 2, (0, 0, 0), -1)
    x, y, w, h = cells[1][2]
    cv2.circle(filled_exam, (x + w//2, y + h//2), min(w, h)//2 - 2, (0, 0, 0), -1)
    
    # Q3: Mark D only
    x, y, w, h = cells[2][3]
    cv2.circle(filled_exam, (x + w//2, y + h//2), min(w, h)//2 - 2, (0, 0, 0), -1)
    
    # Q4: Don't mark anything (already blank)
    
    # Q5: Mark all answers
    for choice_idx in range(choices_per_question):
        x, y, w, h = cells[4][choice_idx]
        cv2.circle(filled_exam, (x + w//2, y + h//2), min(w, h)//2 - 2, (0, 0, 0), -1)
    
    # Save filled exam
    filled_path = os.path.join(OUT_DIR, 'test_invalid.png')
    cv2.imwrite(filled_path, filled_exam)
    print(f"\nTest exam created: {filled_path}")
    
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
    
    print("\nResults:")
    print("-" * 60)
    
    if result['success']:
        answers = result['answers']
        
        test_cases = [
            ("Q1", "A only", True, 0),
            ("Q2", "A and C (invalid)", False, None),
            ("Q3", "D only", True, 3),
            ("Q4", "No marks (invalid)", False, None),
            ("Q5", "All marked (invalid)", False, None),
        ]
        
        for i, (q_label, description, should_be_valid, expected) in enumerate(test_cases):
            detected = answers[i]
            is_valid = detected is not None
            
            status = "✓" if is_valid == should_be_valid else "✗"
            
            if detected is not None:
                answer_letter = 'ABCD'[detected]
                result_str = f"{answer_letter}"
            else:
                result_str = "INVALID"
            
            print(f"{status} {q_label}: {description}")
            print(f"   Expected: {'valid' if should_be_valid else 'invalid'}")
            print(f"   Detected: {result_str}")
            
            if should_be_valid and expected is not None:
                match = "✓" if detected == expected else "✗"
                print(f"   Answer match: {match}")
            print()
    else:
        print(f"✗ Processing failed: {result['error']}")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
