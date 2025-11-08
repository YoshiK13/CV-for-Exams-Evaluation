# CV for Exams Evaluation

A repository for the development of automated exam assessments using OpenCV, with the aim of facilitating the work of teachers and streamlining student grading.

## Features

- � **Template Generation**: Create compact, printable exam answer sheet templates
- 🎯 **Automatic Alignment**: Use corner markers to automatically align and deskew scanned images
- 🖼️ **Image Processing**: Convert images to black and white for robust detection
- 🔍 **Answer Detection**: Automatically detect marked answers in multiple-choice exams
- ✅ **Answer Validation**: Identify invalid answers (no marks or multiple marks per question)
- 📊 **Pattern Recognition**: Detect patterns, shapes, and features in exam images
- 🎨 **Contour Detection**: Find and analyze shapes and regions of interest
- 🔧 **Configurable**: Adjust cell sizes, question counts, and detection thresholds

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YoshiK13/CV-for-Exams-Evaluation.git
   cd CV-for-Exams-Evaluation
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Complete Workflow Example

See the full exam evaluation workflow in action:

```bash
python examples/demo_complete_workflow.py
```

This demonstrates:

- Generating an exam template
- Simulating a filled exam (marking answers)
- Processing the exam to detect marked answers
- Validating answers (detecting invalid/multiple marks)

### Generate an Exam Template

```bash
python examples/generate_exam_sheet.py
```

### Test Invalid Answer Detection

```bash
python examples/demo_invalid_answers.py
```

### Using the PatternRecognizer Class

```python
from exam_evaluator import PatternRecognizer
import cv2

# Initialize the recognizer
recognizer = PatternRecognizer()

# 1. Generate an exam template
template = recognizer.generate_exam_sheet_template(
    title="Midterm Exam",
    num_questions=10,
    choices_per_question=4,
    sheet_size=(800, 1000)
)
cv2.imwrite('exam_template.png', template)

# 2. Process a filled exam (complete pipeline)
result = recognizer.process_exam_sheet(
    'scanned_exam.png',
    num_questions=10,
    choices_per_question=4
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

# 3. Low-level operations
# Load and preprocess
image = recognizer.load_image('path/to/exam.jpg')
gray = recognizer.convert_to_grayscale(image)
binary = recognizer.convert_to_black_and_white(gray)

# Align using corner markers
aligned = recognizer.align_exam_image(image)

# Detect edges and contours
edges = recognizer.detect_edges(gray)
contours, hierarchy = recognizer.find_contours(edges)
```

For more details, see the [Usage Guide](docs/USAGE_GUIDE.md).

## Project Structure

```
CV-for-Exams-Evaluation/
├── src/
│   └── exam_evaluator/
│       ├── __init__.py
│       └── pattern_recognition.py    # Core pattern recognition module
├── tests/
│   ├── __init__.py
│   └── test_pattern_recognition.py   # Unit tests
├── examples/
│   └── basic_pattern_recognition.py  # Example usage
├── docs/                              # Documentation
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## Running Tests

Run the test suite to verify the installation:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Dependencies

Core dependencies:
- **opencv-python** (4.10.0.84): Computer vision library
- **opencv-contrib-python** (4.10.0.84): Additional OpenCV modules
- **numpy** (1.26.4): Numerical computing
- **Pillow** (10.4.0): Image processing
- **scikit-image** (0.24.0): Advanced image processing
- **scikit-learn** (1.5.2): Machine learning algorithms
- **pandas** (2.2.3): Data manipulation
- **matplotlib** (3.9.2): Visualization

Development dependencies:
- **pytest** (8.3.3): Testing framework
- **pytest-cov** (5.0.0): Test coverage

## Development

### Adding New Features

1. Create feature modules in `src/exam_evaluator/`
2. Add corresponding tests in `tests/`
3. Update documentation in `docs/`
4. Add examples in `examples/`

### Code Style

Follow PEP 8 guidelines for Python code style.

## Use Cases

This project can be used for:
- Automated grading of multiple-choice exams
- Answer bubble detection and marking
- Handwriting recognition preparation
- Exam form alignment and correction
- Quality control of scanned exam papers
- Pattern matching for specific answer formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for educational purposes.

## Acknowledgments

Built with OpenCV, the leading open-source computer vision library.
