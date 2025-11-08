# Quick Start Guide

Get started with CV Exam Evaluator in minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/YoshiK13/CV-for-Exams-Evaluation.git
cd CV-for-Exams-Evaluation

# Install dependencies
pip install -r requirements.txt
```

## Run Your First Example

```bash
python examples/basic_pattern_recognition.py
```

This will:
- ✓ Create a sample exam image with answer bubbles
- ✓ Detect circles (answer bubbles) 
- ✓ Apply various pattern recognition techniques
- ✓ Generate visualizations in the `examples/` folder

## Basic Usage

### 1. Initialize the Pattern Recognizer

```python
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()
```

### 2. Load an Exam Image

```python
image = recognizer.load_image('path/to/exam.jpg')
```

### 3. Detect Answer Bubbles

```python
gray = recognizer.convert_to_grayscale(image)
circles = recognizer.detect_circles(gray, min_radius=10, max_radius=30)

if circles is not None:
    print(f"Found {len(circles[0])} answer bubbles!")
```

### 4. Preprocess for Analysis

```python
# Complete preprocessing pipeline
preprocessed = recognizer.preprocess_exam_image('path/to/exam.jpg')
```

## Common Use Cases

### Multiple Choice Exam Evaluation

```python
from exam_evaluator import PatternRecognizer
import cv2

recognizer = PatternRecognizer()

# Load the exam
image = recognizer.load_image('exam.jpg')
gray = recognizer.convert_to_grayscale(image)

# Find all answer bubbles
circles = recognizer.detect_circles(gray, min_radius=10, max_radius=30)

# Process each bubble
for circle in circles[0]:
    x, y, r = circle
    # Extract bubble region and check if filled
    bubble_region = gray[y-r:y+r, x-r:x+r]
    # Add logic to determine if bubble is marked
```

### Finding Form Boundaries

```python
recognizer = PatternRecognizer()

# Load and preprocess
image = recognizer.load_image('exam.jpg')
gray = recognizer.convert_to_grayscale(image)

# Detect edges
edges = recognizer.detect_edges(gray)

# Find contours (potential form boundaries)
contours, _ = recognizer.find_contours(edges)

# Process largest contours as form boundaries
contours = sorted(contours, key=cv2.contourArea, reverse=True)
```

### Template Matching for Checkmarks

```python
recognizer = PatternRecognizer()

# Load exam and checkmark template
exam = recognizer.load_image('exam.jpg')
template = recognizer.load_image('checkmark_template.jpg')

# Convert both to grayscale
exam_gray = recognizer.convert_to_grayscale(exam)
template_gray = recognizer.convert_to_grayscale(template)

# Find all checkmarks
matches = recognizer.template_matching(exam_gray, template_gray, threshold=0.8)

print(f"Found {len(matches)} checkmarks")
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Next Steps

- Read [PATTERN_RECOGNITION.md](PATTERN_RECOGNITION.md) for detailed technique explanations
- Explore the `examples/` directory for more advanced use cases
- Check out the full [README.md](../README.md) for complete documentation

## Troubleshooting

### Import Error

If you get an import error, make sure you're in the project directory and dependencies are installed:

```bash
pip install -r requirements.txt
```

### Image Not Loading

Ensure your image path is correct and the file exists:

```python
import os
print(os.path.exists('path/to/image.jpg'))  # Should print True
```

### Circle Detection Not Working

Try adjusting the radius parameters based on your exam format:

```python
# For smaller bubbles
circles = recognizer.detect_circles(gray, min_radius=5, max_radius=20)

# For larger bubbles
circles = recognizer.detect_circles(gray, min_radius=20, max_radius=50)
```

## Support

For issues and questions, please open an issue on GitHub.
