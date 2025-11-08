# CV for Exams Evaluation

A repository for the development of automated exam assessments using OpenCV, with the aim of facilitating the work of teachers and streamlining student grading.

## Features

- 🖼️ **Image Processing**: Load and preprocess exam images for analysis
- 🔍 **Pattern Recognition**: Detect patterns, shapes, and features in exam images
- ⭕ **Circle Detection**: Identify answer bubbles in multiple-choice exams
- 📊 **Contour Detection**: Find and analyze shapes and regions of interest
- 🎯 **Template Matching**: Match and locate specific patterns in exam images
- ✅ **Edge Detection**: Identify boundaries and important features

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

### Running the Basic Example

The repository includes a basic pattern recognition example that demonstrates the core capabilities:

```bash
python examples/basic_pattern_recognition.py
```

This will:
- Create a sample exam image with answer bubbles
- Demonstrate various pattern recognition techniques
- Generate visualizations of detected patterns
- Save processed images in the `examples/` directory

### Using the PatternRecognizer Class

```python
from exam_evaluator import PatternRecognizer

# Initialize the recognizer
recognizer = PatternRecognizer()

# Load an exam image
image = recognizer.load_image('path/to/exam.jpg')

# Convert to grayscale
gray = recognizer.convert_to_grayscale(image)

# Detect edges
edges = recognizer.detect_edges(gray)

# Find contours
contours, hierarchy = recognizer.find_contours(edges)

# Detect circles (answer bubbles)
circles = recognizer.detect_circles(gray, min_radius=10, max_radius=30)

# Preprocess exam image (complete pipeline)
preprocessed = recognizer.preprocess_exam_image('path/to/exam.jpg')
```

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
