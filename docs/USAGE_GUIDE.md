# Usage Guide: Exam Answer Sheet Evaluation System

This guide explains how to use the CV-based exam evaluation system.

## Overview

The system uses OpenCV to:
1. Generate printable exam answer sheet templates
2. Process scanned/photographed exams
3. Automatically detect and validate student answers

## Features

- **Compact Templates**: Small, efficient answer sheets (800x1000 pixels default)
- **Alignment Markers**: Four corner markers for automatic image alignment
- **Multiple Choice Support**: Configurable number of questions and choices
- **Answer Validation**: Detects invalid answers (no marks or multiple marks per question)
- **Black & White Processing**: Robust detection using binary image processing

## Quick Start

### 1. Generate an Exam Template

```python
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()

# Generate a template for 10 questions with 4 choices each
template = recognizer.generate_exam_sheet_template(
    title="Midterm Exam",
    num_questions=10,
    choices_per_question=4,
    sheet_size=(800, 1000),  # width, height in pixels
    margin=40,
    alignment_square_size=40
)

# Save as image
import cv2
cv2.imwrite('exam_template.png', template)
```

### 2. Process a Filled Exam

```python
# Process a scanned/photographed exam
result = recognizer.process_exam_sheet(
    'scanned_exam.png',
    num_questions=10,
    choices_per_question=4,
    template_size=(800, 1000),
    margin=40,
    alignment_square_size=40,
    mark_threshold=0.15  # 15% of cell must be marked
)

if result['success']:
    answers = result['answers']
    for i, answer in enumerate(answers):
        if answer is not None:
            print(f"Q{i+1}: {'ABCD'[answer]}")
        else:
            print(f"Q{i+1}: INVALID")
else:
    print(f"Error: {result['error']}")
```

## Template Structure

The generated template includes:

1. **Title** - Exam name at the top
2. **Student Information** - Name and student code fields
3. **Alignment Markers** - Four corner markers (nested squares) for alignment
4. **Answer Grid** - Questions as columns, choices as rows
   - Question numbers in header row
   - Choice labels (A, B, C, D) in left column
   - Empty cells for students to mark their answers

## Processing Pipeline

The `process_exam_sheet` method performs these steps:

1. **Load Image** - Read the scanned exam image
2. **Find Alignment Markers** - Detect the four corner markers
3. **Align Image** - Apply perspective transformation to correct rotation/skew
4. **Convert to Binary** - Create black & white image for detection
5. **Extract Cells** - Calculate coordinates of all answer cells
6. **Detect Marks** - Analyze each cell to determine if it's marked
7. **Validate Answers** - Ensure exactly one answer per question

## Answer Validation Rules

- **Valid**: Exactly one cell marked for the question → Returns answer index (0-3 for A-D)
- **Invalid**: No cells marked → Returns `None`
- **Invalid**: Multiple cells marked → Returns `None`

## Configuration Parameters

### Template Generation

- `title`: Exam title text
- `num_questions`: Number of questions (columns in the grid)
- `choices_per_question`: Number of choices per question (rows, e.g., 4 for A-D)
- `sheet_size`: Tuple of (width, height) in pixels
- `margin`: Outer margin in pixels
- `alignment_square_size`: Size of corner alignment markers

### Mark Detection

- `mark_threshold`: Minimum ratio of black pixels to consider a cell marked (default: 0.15)
  - Lower values (e.g., 0.10) = more sensitive, may detect light marks or noise
  - Higher values (e.g., 0.30) = less sensitive, requires darker/larger marks

## Examples

Run the example scripts to see the system in action:

```bash
# Generate a basic template
python examples/generate_exam_sheet.py

# Complete workflow demonstration
python examples/demo_complete_workflow.py

# Test invalid answer detection
python examples/demo_invalid_answers.py
```

## Tips for Best Results

1. **Scanning**: 
   - Use high contrast (scan in black & white mode)
   - Ensure good lighting
   - Keep the sheet flat to minimize distortion

2. **Marking Instructions for Students**:
   - Fill cells completely with dark marks
   - Use pen or dark pencil (not light pencil)
   - Erase completely if changing answer
   - Mark only ONE answer per question

3. **Template Printing**:
   - Print at high quality (300 DPI or higher)
   - Use white paper with good contrast
   - Avoid resizing that might distort alignment markers

## Troubleshooting

### "Failed to align image"
- Check that all 4 corner markers are visible
- Ensure markers aren't obscured or damaged
- Try improving image quality/lighting

### Answers not detected
- Reduce `mark_threshold` (e.g., from 0.15 to 0.10)
- Check that marks are dark enough
- Verify image isn't too bright/washed out

### False positives (unmarked cells detected as marked)
- Increase `mark_threshold` (e.g., from 0.15 to 0.20)
- Check for dirt/marks on the paper
- Ensure clean scanning

## Advanced Usage

### Custom Cell Detection

```python
# Get cell coordinates for manual processing
cells = recognizer.extract_answer_cells(
    image, 
    num_questions=10, 
    choices_per_question=4,
    template_size=(800, 1000), 
    margin=40, 
    alignment_square_size=40
)

# cells[question_idx][choice_idx] = (x, y, width, height)
```

### Manual Alignment

```python
# Align image manually
aligned = recognizer.align_exam_image(
    image,
    template_size=(800, 1000),
    margin=40,
    alignment_square_size=40
)

# Then process with detect_marked_answers
answers = recognizer.detect_marked_answers(
    aligned,
    num_questions=10,
    choices_per_question=4
)
```

### Binary Conversion Only

```python
# Convert to black & white for inspection
binary = recognizer.convert_to_black_and_white(image)
cv2.imwrite('binary_output.png', binary)
```

## API Reference

See `docs/PATTERN_RECOGNITION.md` for complete API documentation.
