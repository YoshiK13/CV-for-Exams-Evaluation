"""
Pattern Recognition Module for Exam Evaluation
This module provides pattern recognition capabilities using OpenCV for exam image analysis.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional


class PatternRecognizer:
    """
    A class for performing pattern recognition on exam images using OpenCV.
    
    This class provides methods for detecting patterns, shapes, and features
    in exam images for automated evaluation.
    """
    
    def __init__(self):
        """Initialize the PatternRecognizer."""
        self.opencv_version = cv2.__version__
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load an image from the specified path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            The loaded image as a numpy array, or None if loading fails
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image from {image_path}")
            return None
        return image
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert a color image to grayscale.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Grayscale image
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def apply_threshold(self, image: np.ndarray, threshold_value: int = 127) -> np.ndarray:
        """
        Apply binary threshold to an image.
        
        Args:
            image: Input grayscale image
            threshold_value: Threshold value (0-255)
            
        Returns:
            Binary thresholded image
        """
        _, binary_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        return binary_image
    
    def detect_edges(self, image: np.ndarray, low_threshold: int = 50, 
                     high_threshold: int = 150) -> np.ndarray:
        """
        Detect edges in an image using Canny edge detection.
        
        Args:
            image: Input grayscale image
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection
            
        Returns:
            Edge-detected image
        """
        edges = cv2.Canny(image, low_threshold, high_threshold)
        return edges
    
    def find_contours(self, binary_image: np.ndarray) -> Tuple[List, np.ndarray]:
        """
        Find contours in a binary image.
        
        Args:
            binary_image: Binary input image
            
        Returns:
            Tuple of (contours, hierarchy)
        """
        contours, hierarchy = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours, hierarchy
    
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
        circles = cv2.HoughCircles(
            image,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        return circles
    
    def template_matching(self, image: np.ndarray, template: np.ndarray, 
                         threshold: float = 0.8) -> List[Tuple[int, int]]:
        """
        Perform template matching to find patterns in an image.
        
        Args:
            image: Input image
            template: Template image to search for
            threshold: Matching threshold (0-1)
            
        Returns:
            List of (x, y) coordinates where template was found
        """
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches = list(zip(*locations[::-1]))
        return matches
    
    def get_image_info(self, image: np.ndarray) -> dict:
        """
        Get information about an image.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary containing image information
        """
        return {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'size': image.size,
            'dimensions': len(image.shape)
        }
    
    def preprocess_exam_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Preprocess an exam image for pattern recognition.
        
        This method applies a standard preprocessing pipeline:
        - Load image
        - Convert to grayscale
        - Apply Gaussian blur for noise reduction
        - Apply adaptive threshold
        
        Args:
            image_path: Path to the exam image
            
        Returns:
            Preprocessed binary image or None if processing fails
        """
        # Load image
        image = self.load_image(image_path)
        if image is None:
            return None
        
        # Convert to grayscale
        gray = self.convert_to_grayscale(image)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive threshold
        processed = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return processed
