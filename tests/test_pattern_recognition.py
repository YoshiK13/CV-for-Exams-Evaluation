"""
Tests for Pattern Recognition Module
"""

import sys
import os
import pytest
import numpy as np
import cv2

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exam_evaluator import PatternRecognizer


class TestPatternRecognizer:
    """Test suite for PatternRecognizer class."""
    
    @pytest.fixture
    def recognizer(self):
        """Create a PatternRecognizer instance for testing."""
        return PatternRecognizer()
    
    @pytest.fixture
    def sample_image(self):
        """Create a simple test image."""
        # Create a white image with a black rectangle
        image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(image, (25, 25), (75, 75), (0, 0, 0), -1)
        return image
    
    @pytest.fixture
    def sample_gray_image(self):
        """Create a simple grayscale test image."""
        image = np.ones((100, 100), dtype=np.uint8) * 255
        cv2.rectangle(image, (25, 25), (75, 75), 0, -1)
        return image
    
    def test_initialization(self, recognizer):
        """Test that PatternRecognizer initializes correctly."""
        assert recognizer is not None
        assert hasattr(recognizer, 'opencv_version')
        assert isinstance(recognizer.opencv_version, str)
    
    def test_convert_to_grayscale(self, recognizer, sample_image):
        """Test grayscale conversion."""
        gray = recognizer.convert_to_grayscale(sample_image)
        assert gray is not None
        assert len(gray.shape) == 2  # Grayscale images are 2D
        assert gray.dtype == np.uint8
    
    def test_apply_threshold(self, recognizer, sample_gray_image):
        """Test binary threshold application."""
        binary = recognizer.apply_threshold(sample_gray_image, threshold_value=127)
        assert binary is not None
        assert len(binary.shape) == 2
        # Binary image should only have 0 and 255 values
        unique_values = np.unique(binary)
        assert all(v in [0, 255] for v in unique_values)
    
    def test_detect_edges(self, recognizer, sample_gray_image):
        """Test edge detection."""
        edges = recognizer.detect_edges(sample_gray_image, low_threshold=50, high_threshold=150)
        assert edges is not None
        assert len(edges.shape) == 2
        assert edges.dtype == np.uint8
    
    def test_find_contours(self, recognizer, sample_gray_image):
        """Test contour detection."""
        binary = recognizer.apply_threshold(sample_gray_image, threshold_value=127)
        contours, hierarchy = recognizer.find_contours(binary)
        assert contours is not None
        assert hierarchy is not None
        assert len(contours) > 0  # Should find at least the rectangle
    
    def test_get_image_info(self, recognizer, sample_image):
        """Test getting image information."""
        info = recognizer.get_image_info(sample_image)
        assert info is not None
        assert 'shape' in info
        assert 'dtype' in info
        assert 'size' in info
        assert 'dimensions' in info
        assert info['shape'] == (100, 100, 3)
        assert info['dimensions'] == 3
    
    def test_detect_circles_returns_valid_format(self, recognizer):
        """Test circle detection returns correct format."""
        # Create an image with a circle
        image = np.ones((200, 200), dtype=np.uint8) * 255
        cv2.circle(image, (100, 100), 30, 0, -1)
        
        circles = recognizer.detect_circles(image, min_radius=20, max_radius=40)
        # Note: circles might be None if detection fails, which is acceptable
        if circles is not None:
            assert isinstance(circles, np.ndarray)
    
    def test_template_matching(self, recognizer, sample_gray_image):
        """Test template matching."""
        # Use a small region as template
        template = sample_gray_image[30:45, 30:45]
        matches = recognizer.template_matching(sample_gray_image, template, threshold=0.9)
        assert matches is not None
        assert isinstance(matches, list)
        # Should find at least one match (the template location itself)
        assert len(matches) > 0
    
    def test_load_image_nonexistent_file(self, recognizer):
        """Test loading a non-existent image."""
        result = recognizer.load_image("/nonexistent/path/image.jpg")
        assert result is None
    
    def test_preprocess_exam_image_nonexistent_file(self, recognizer):
        """Test preprocessing a non-existent image."""
        result = recognizer.preprocess_exam_image("/nonexistent/path/image.jpg")
        assert result is None


def test_opencv_import():
    """Test that OpenCV is properly installed and can be imported."""
    assert cv2 is not None
    version = cv2.__version__
    assert version is not None
    assert len(version) > 0
    print(f"OpenCV version: {version}")


def test_numpy_import():
    """Test that NumPy is properly installed."""
    assert np is not None
    version = np.__version__
    assert version is not None
    print(f"NumPy version: {version}")
