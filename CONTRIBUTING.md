# Contributing to CV Exam Evaluator

Thank you for your interest in contributing to CV Exam Evaluator! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CV-for-Exams-Evaluation.git
   cd CV-for-Exams-Evaluation
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

Always run tests before submitting a pull request:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise

Example of good documentation:

```python
def detect_circles(self, image: np.ndarray, min_radius: int = 10, 
                   max_radius: int = 100) -> Optional[np.ndarray]:
    """
    Detect circles in an image using Hough Circle Transform.
    
    Args:
        image: Input grayscale image
        min_radius: Minimum circle radius
        max_radius: Maximum circle radius
        
    Returns:
        Array of detected circles (x, y, radius) or None
    """
```

### Adding New Features

1. **Write Tests First**: Create tests for your new feature in `tests/`
2. **Implement Feature**: Add your code in the appropriate module
3. **Document**: Add docstrings and update relevant documentation
4. **Test**: Ensure all tests pass
5. **Example**: Add an example in `examples/` if applicable

### Project Structure

```
CV-for-Exams-Evaluation/
├── src/exam_evaluator/    # Main source code
├── tests/                  # Unit tests
├── examples/              # Usage examples
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
└── setup.py              # Package configuration
```

## Submitting Changes

1. Commit your changes with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: circle detection improvements"
   ```

2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub with:
   - Clear title describing the change
   - Description of what was changed and why
   - Reference to any related issues

## Pull Request Guidelines

- **One Feature Per PR**: Keep pull requests focused on a single feature or fix
- **Tests Required**: All new code must include tests
- **Documentation**: Update docs if you change functionality
- **Clean History**: Squash commits if necessary before submitting
- **CI Passes**: Ensure all automated checks pass

## Reporting Issues

When reporting issues, please include:

- Python version
- OpenCV version
- Operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages or screenshots if applicable

## Feature Requests

Feature requests are welcome! Please:

1. Check if the feature has already been requested
2. Describe the feature and its use case
3. Explain how it would benefit users
4. Consider if you'd be willing to implement it

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing opinions and experiences

## Questions?

If you have questions, feel free to:

- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review the examples in `examples/`

Thank you for contributing to CV Exam Evaluator!
