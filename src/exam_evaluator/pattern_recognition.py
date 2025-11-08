"""
Pattern Recognition Module for Exam Evaluation

This module provides pattern recognition capabilities using OpenCV for exam image analysis.

OPTIMIZATIONS IMPLEMENTED:
- Direct use of OpenCV functions for maximum performance
- Smart grayscale conversion (avoids redundant conversions)
- Efficient preprocessing pipeline with native OpenCV operations
- Removal of duplicate code and unnecessary wrapper methods
- Optimized morphology for shadow removal
- Internal helper methods (_to_gray) for efficient code reuse
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
    
    def _to_gray(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale if needed (optimized helper method).
        
        Optimization: Avoids redundant conversion if image is already grayscale.
        
        Args:
            image: Input image (BGR or already grayscale)
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Public methods for API compatibility
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert a color image to grayscale (optimized OpenCV wrapper).
        
        Args:
            image: Input image (BGR format or already grayscale)
            
        Returns:
            Grayscale image
        """
        return self._to_gray(image)
    
    def apply_threshold(self, image: np.ndarray, threshold_value: int = 127) -> np.ndarray:
        """
        Apply binary threshold to an image using OpenCV directly.
        
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
    
    def find_contours(self, binary_image: np.ndarray) -> Tuple:
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
        
        # Optimized pipeline using OpenCV directly
        gray = self._to_gray(image)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        processed = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return processed

    # ------------------------------------------------------------------
    # Exam sheet template generation and alignment utilities
    # ------------------------------------------------------------------
    def generate_exam_sheet_template(
        self,
        title: str = "Exam",
        num_questions: int = 10,
        choices_per_question: int = 4,
        sheet_size: Tuple[int, int] = (800, 1000),
        margin: int = 40,
        alignment_square_size: int = 40,
        qr_size: int = 200,
    ) -> np.ndarray:
        """
        Generate a printable blank exam answer sheet template.

        The template contains:
        - A centered title at the top
        - A student name/code box under the title
        - A QR-code placeholder (top-right by default)
        - Four filled alignment squares placed near the corners (used to detect
          and correct rotation/scale of scanned images)
        - A questions area with numbered rows and circular bubbles for multiple-choice

        Args:
            title: Exam title text
            num_questions: Number of multiple-choice questions
            choices_per_question: Number of choices per question (e.g., 4 for A-D)
            sheet_size: (width, height) in pixels for the generated image
            margin: Outer margin in pixels
            alignment_square_size: Pixel size of corner alignment squares
            qr_size: Pixel size of the QR placeholder square

        Returns:
            A BGR (uint8) numpy image with the drawn template
        """
        width, height = sheet_size
        img = np.ones((height, width, 3), dtype=np.uint8) * 255

        # Title
        title_scale = 1.2
        title_thickness = 2
        title_font = cv2.FONT_HERSHEY_SIMPLEX
        (t_w, t_h), _ = cv2.getTextSize(title, title_font, title_scale, title_thickness)
        title_x = (width - t_w) // 2
        title_y = margin + t_h
        cv2.putText(img, title, (title_x, title_y), title_font, title_scale, (0, 0, 0), title_thickness, cv2.LINE_AA)

        # Draw QR-style finder alignment markers (nested squares) in the four corners
        def draw_finder(x, y, size):
            # outer black
            cv2.rectangle(img, (int(x), int(y)), (int(x + size), int(y + size)), (0, 0, 0), -1)
            # inner white
            inset1 = int(size * 0.18)
            cv2.rectangle(img, (int(x + inset1), int(y + inset1)), (int(x + size - inset1), int(y + size - inset1)), (255, 255, 255), -1)
            # center black
            inset2 = int(size * 0.36)
            cv2.rectangle(img, (int(x + inset2), int(y + inset2)), (int(x + size - inset2), int(y + size - inset2)), (0, 0, 0), -1)

        sq = alignment_square_size
        # place them at margins but ensure table area avoids them
        draw_finder(margin, margin, sq)  # top-left
        draw_finder(width - margin - sq, margin, sq)  # top-right
        draw_finder(margin, height - margin - sq, sq)  # bottom-left
        draw_finder(width - margin - sq, height - margin - sq, sq)  # bottom-right

        # Student Name and Code cells (individual cells) under title
        box_top = title_y + 15
        box_height = 50
        # Leave horizontal space for alignment markers by keeping inside margins + sq
        content_left = margin + sq + 15
        content_right = width - margin - sq - 15
        # split into two cells: Name (70%) and Student Code (30%)
        total_w = content_right - content_left
        name_w = int(total_w * 0.7)
        code_w = total_w - name_w - 8

        name_left = content_left
        name_right = name_left + name_w
        code_left = name_right + 8
        code_right = code_left + code_w

        cv2.rectangle(img, (name_left, box_top), (name_right, box_top + box_height), (0, 0, 0), 2)
        cv2.putText(img, "Name:", (name_left + 8, box_top + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        cv2.rectangle(img, (code_left, box_top), (code_right, box_top + box_height), (0, 0, 0), 2)
        cv2.putText(img, "Code:", (code_left + 8, box_top + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Questions table: choices are rows, questions are columns
        table_top = box_top + box_height + 20
        # shrink table width and center it between content_left and content_right
        content_w = content_right - content_left
        table_w = int(content_w * 0.95)
        table_left = content_left + (content_w - table_w) // 2
        table_right = table_left + table_w
        # reduce overall table height to keep sheet compact (smaller than before)
        available_height = height - table_top - margin - sq - 20
        table_height = int(available_height * 0.85)  # use 85% of available
        table_bottom = table_top + table_height

        # Compute cell sizes. Add one header row for question numbers
        n_cols = max(1, num_questions)
        n_choice_rows = max(1, choices_per_question)
        header_h = max(18, int(table_height * 0.10))
        remaining_h = table_height - header_h
        # compact choice row height
        choice_row_h = max(15, int(remaining_h / n_choice_rows))
        # recompute table_bottom to fit header + choice rows
        table_height = header_h + choice_row_h * n_choice_rows
        table_bottom = table_top + table_height

        # Reserve a small left column for choice labels
        label_col_w = max(30, int(table_w * 0.08))
        q_area_w = table_w - label_col_w
        cell_w = q_area_w / n_cols

        # Draw table: first draw header row with question numbers. We draw the label column first.
        # Draw label column header (empty)
        lbl_x1 = table_left
        lbl_x2 = table_left + label_col_w
        cv2.rectangle(img, (lbl_x1, table_top), (lbl_x2, table_top + header_h), (0, 0, 0), 1)

        for col in range(n_cols):
            col_x1 = int(table_left + label_col_w + col * cell_w)
            col_x2 = int(table_left + label_col_w + (col + 1) * cell_w)
            # header cell
            header_y1 = table_top
            header_y2 = table_top + header_h
            cv2.rectangle(img, (col_x1, header_y1), (col_x2, header_y2), (0, 0, 0), 1)
            qnum = col + 1
            # center question number in header cell
            (qw, qh), _ = cv2.getTextSize(str(qnum), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            qx = col_x1 + (col_x2 - col_x1 - qw) // 2
            qy = header_y1 + (header_h + qh) // 2
            cv2.putText(img, str(qnum), (qx, qy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # draw choice rows
            for row in range(n_choice_rows):
                row_y1 = header_y2 + row * choice_row_h
                row_y2 = header_y2 + (row + 1) * choice_row_h
                cv2.rectangle(img, (col_x1, row_y1), (col_x2, row_y2), (0, 0, 0), 1)

                # No circle: students can mark cells in different ways; leave cell empty
                # Optionally draw a very light inner guide box (disabled by default)
                # cx = int((col_x1 + col_x2) / 2)
                # cy = int((row_y1 + row_y2) / 2)
                # cv2.rectangle(img, (cx-8, cy-8), (cx+8, cy+8), (0,0,0), 1)

        # Draw label column rows and labels
        for row in range(n_choice_rows):
            row_y1 = table_top + header_h + row * choice_row_h
            row_y2 = table_top + header_h + (row + 1) * choice_row_h
            cv2.rectangle(img, (lbl_x1, row_y1), (lbl_x2, row_y2), (0, 0, 0), 1)
            label = chr(ord('A') + row) if row < 26 else str(row + 1)
            cy = int((row_y1 + row_y2) / 2)
            cv2.putText(img, label, (lbl_x1 + 8, cy + int(choice_row_h * 0.15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        return img

    def find_alignment_squares(self, image: np.ndarray, min_area: int = 2000) -> List[Tuple[int, int]]:
        """
        Detect filled square alignment markers in an image.

        Args:
            image: Input image (BGR or grayscale)
            min_area: Minimum contour area to consider as an alignment square

        Returns:
            List of (x, y) centers for detected square markers. Returns an empty
            list if none are found.
        """
        # Optimization: use helper method for grayscale conversion
        gray = self._to_gray(image)
        _, thr = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        # Use morphological closing to reduce small holes/blur effects
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        markers = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < max(800, min_area * 0.2):
                continue

            # bounding rect and aspect ratio
            x, y, w, h = cv2.boundingRect(cnt)
            if h == 0:
                continue
            ar = float(w) / float(h)

            # solidity: how much of bounding box is covered by contour
            rect_area = float(w * h)
            solidity = area / rect_area if rect_area > 0 else 0

            # Accept roughly-square, fairly-solid contours
            if 0.5 <= ar <= 2.0 and solidity > 0.4 and area > min_area * 0.1:
                cx = x + w // 2
                cy = y + h // 2
                markers.append((cx, cy))

        return markers

    def _expected_marker_positions(self, template_size: Tuple[int, int], margin: int, alignment_square_size: int) -> np.ndarray:
        """Return expected marker center positions for a given template size.

        Order: top-left, top-right, bottom-left, bottom-right.
        """
        w, h = template_size
        sq = float(alignment_square_size)
        return np.array([
            [margin + sq / 2.0, margin + sq / 2.0],
            [w - margin - sq / 2.0, margin + sq / 2.0],
            [margin + sq / 2.0, h - margin - sq / 2.0],
            [w - margin - sq / 2.0, h - margin - sq / 2.0],
        ], dtype=np.float32)

    def _select_nearest_markers(self, candidates: List[Tuple[int, int]], expected: np.ndarray) -> Optional[np.ndarray]:
        """Select the nearest candidate to each expected corner.

        Returns an array of shape (4,2) with float32 coordinates or None if not enough candidates.
        """
        if len(candidates) < 4:
            return None
        cand = [(float(x), float(y)) for x, y in candidates]
        src_pts = []
        # For each expected point, pick the nearest remaining candidate
        for ex in expected:
            dists = [((cx - ex[0])**2 + (cy - ex[1])**2, i) for i, (cx, cy) in enumerate(cand)]
            if not dists:
                return None
            dists.sort()
            best_idx = dists[0][1]
            best = cand.pop(best_idx)
            src_pts.append(best)
        return np.array(src_pts, dtype=np.float32)

    def align_exam_image(self, image: np.ndarray, template_size: Tuple[int, int] = (800, 1000), margin: int = 40, alignment_square_size: int = 40) -> Optional[np.ndarray]:
        """
        Attempt to deskew/resize a scanned exam image using the four corner
        alignment squares. If four markers are found, a perspective transform
        is computed to map the scanned markers to ideal template corners.

        Args:
            image: Input BGR image of a scanned exam
            template_size: Desired output (width, height) in pixels
            margin: Margin used when template was generated
            alignment_square_size: Size of alignment squares used in template

        Returns:
            Warped image aligned to the template coordinate system, or None if
            alignment failed (e.g., fewer than 4 markers detected)
        """
        candidates = self.find_alignment_squares(image)
        if len(candidates) < 4:
            return None

        h_img, w_img = image.shape[:2]
        # expected positions in the scanned image coordinate system
        expected_img = self._expected_marker_positions((w_img, h_img), margin, alignment_square_size)
        src = self._select_nearest_markers(candidates, expected_img)
        if src is None:
            return None

        # destination positions in the template coordinate system
        dst = self._expected_marker_positions(template_size, margin, alignment_square_size)

        M = cv2.getPerspectiveTransform(src, dst)
        w, h = template_size
        warped = cv2.warpPerspective(image, M, (w, h), flags=cv2.INTER_LINEAR)
        return warped

    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """
        Remove shadows from an image to improve detection.
        
        This method uses morphological operations to eliminate uneven lighting
        and shadows that can affect mark detection.
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            Shadow-removed image (grayscale, 8-bit)
        """
        # Optimization: use helper method for conversion
        gray = self._to_gray(image)
        
        # Optimized pipeline using OpenCV directly
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        background = cv2.morphologyEx(blurred, cv2.MORPH_DILATE, kernel, iterations=3)
        shadow_removed = cv2.divide(blurred, background, scale=255)
        
        return cv2.equalizeHist(shadow_removed)

    def convert_to_black_and_white(self, image: np.ndarray, use_adaptive: bool = False, remove_shadows: bool = False) -> np.ndarray:
        """
        Convert image to binary (pure black and white) using optimized OpenCV pipeline.
        
        Optimizations:
        - Smart grayscale conversion (avoids redundancy)
        - Optional shadow removal with morphology
        - Direct OpenCV thresholding (adaptive or simple)
        
        Args:
            image: Input image (BGR or grayscale)
            use_adaptive: If True, use adaptive threshold (better for variable lighting)
            remove_shadows: If True, remove shadows first (useful if not done previously)
            
        Returns:
            Binary (black and white) image where black=0, white=255
        """
        # Optimization: efficient grayscale conversion
        gray = self._to_gray(image)
        
        # Remove shadows only if explicitly requested
        if remove_shadows:
            gray = self.remove_shadows(gray)
        
        # Optimized thresholding pipeline with OpenCV
        if use_adaptive:
            # Blur + adaptive threshold for variable lighting
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            return cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        else:
            # Simple threshold (optimal for preprocessed images)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            return binary

    def extract_answer_cells(
        self,
        image: np.ndarray,
        num_questions: int = 10,
        choices_per_question: int = 4,
        template_size: Tuple[int, int] = (800, 1000),
        margin: int = 40,
        alignment_square_size: int = 40,
    ) -> List[List[Tuple[int, int, int, int]]]:
        """
        Extract the coordinates of answer cells from an aligned exam sheet.
        
        Returns a list where each element represents a question, and contains
        a list of (x, y, w, h) tuples for each choice cell.
        
        Args:
            image: Aligned exam sheet image
            num_questions: Number of questions in the exam
            choices_per_question: Number of choices per question
            template_size: Template size (width, height)
            margin: Template margin
            alignment_square_size: Size of alignment squares
            
        Returns:
            List of lists containing cell coordinates (x, y, width, height)
        """
        width, height = template_size
        sq = alignment_square_size
        
        # Calculate table position (must match template generation)
        # Title and name box calculations
        title_scale = 1.2
        title_thickness = 2
        title_font = cv2.FONT_HERSHEY_SIMPLEX
        (t_w, t_h), _ = cv2.getTextSize("Exam", title_font, title_scale, title_thickness)
        title_y = margin + t_h
        
        box_top = title_y + 15
        box_height = 50
        
        table_top = box_top + box_height + 20
        
        content_left = margin + sq + 15
        content_right = width - margin - sq - 15
        content_w = content_right - content_left
        table_w = int(content_w * 0.95)
        table_left = content_left + (content_w - table_w) // 2
        
        available_height = height - table_top - margin - sq - 20
        table_height = int(available_height * 0.85)
        
        n_cols = max(1, num_questions)
        n_choice_rows = max(1, choices_per_question)
        header_h = max(18, int(table_height * 0.10))
        remaining_h = table_height - header_h
        choice_row_h = max(15, int(remaining_h / n_choice_rows))
        
        label_col_w = max(30, int(table_w * 0.08))
        q_area_w = table_w - label_col_w
        cell_w = q_area_w / n_cols
        
        # Extract cell coordinates
        cells = []
        for col in range(n_cols):
            question_cells = []
            col_x1 = int(table_left + label_col_w + col * cell_w)
            col_x2 = int(table_left + label_col_w + (col + 1) * cell_w)
            
            for row in range(n_choice_rows):
                row_y1 = table_top + header_h + row * choice_row_h
                row_y2 = table_top + header_h + (row + 1) * choice_row_h
                
                # Add small padding to avoid borders
                padding = 3
                x = col_x1 + padding
                y = row_y1 + padding
                w = (col_x2 - col_x1) - 2 * padding
                h = (row_y2 - row_y1) - 2 * padding
                
                question_cells.append((x, y, w, h))
            
            cells.append(question_cells)
        
        return cells

    def is_cell_marked(
        self,
        binary_image: np.ndarray,
        cell_coords: Tuple[int, int, int, int],
        threshold: float = 0.30
    ) -> bool:
        """
        Determine if a cell is marked by analyzing the ratio of black pixels.
        
        Args:
            binary_image: Binary (black and white) image
            cell_coords: Tuple of (x, y, width, height) for the cell
            threshold: Minimum ratio of black pixels to consider cell as marked (0-1)
            
        Returns:
            True if cell is marked, False otherwise
        """
        x, y, w, h = cell_coords
        
        # Ensure coordinates are within image bounds
        img_h, img_w = binary_image.shape[:2]
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))
        
        # Extract cell region
        cell = binary_image[y:y+h, x:x+w]
        
        if cell.size == 0:
            return False
        
        # Count black pixels (value 0 in binary image)
        black_pixels = np.sum(cell == 0)
        total_pixels = cell.size
        
        # Calculate ratio
        black_ratio = black_pixels / total_pixels
        
        return black_ratio >= threshold

    def detect_marked_answers(
        self,
        image: np.ndarray,
        num_questions: int = 10,
        choices_per_question: int = 4,
        template_size: Tuple[int, int] = (800, 1000),
        margin: int = 40,
        alignment_square_size: int = 40,
        mark_threshold: float = 0.15
    ) -> List[Optional[int]]:
        """
        Detect marked answers from an exam sheet image.
        
        This method performs the complete pipeline:
        1. Converts image to black and white
        2. Extracts answer cell coordinates
        3. Detects which cells are marked
        4. Validates that only one answer per question is marked
        
        Args:
            image: Input exam sheet image (should be aligned)
            num_questions: Number of questions
            choices_per_question: Number of choices per question
            template_size: Template size
            margin: Template margin
            alignment_square_size: Alignment square size
            mark_threshold: Threshold for detecting marked cells
            
        Returns:
            List of detected answers (0-indexed), None for invalid/unmarked questions
            Example: [0, 2, 1, None, 3, ...] means Q1=A, Q2=C, Q3=B, Q4=invalid, Q5=D
        """
        # Convert to black and white
        binary = self.convert_to_black_and_white(image)
        
        # Extract cell coordinates
        cells = self.extract_answer_cells(
            image, num_questions, choices_per_question,
            template_size, margin, alignment_square_size
        )
        
        # Detect marked answers
        answers = []
        for question_idx, question_cells in enumerate(cells):
            marked_choices = []
            
            for choice_idx, cell_coords in enumerate(question_cells):
                if self.is_cell_marked(binary, cell_coords, mark_threshold):
                    marked_choices.append(choice_idx)
            
            # Validate: exactly one answer should be marked
            if len(marked_choices) == 1:
                answers.append(marked_choices[0])
            else:
                # Invalid: either no answer or multiple answers marked
                answers.append(None)
        
        return answers

    def process_exam_sheet(
        self,
        image_path: str,
        num_questions: int = 10,
        choices_per_question: int = 4,
        template_size: Tuple[int, int] = (800, 1000),
        margin: int = 40,
        alignment_square_size: int = 40,
        mark_threshold: float = 0.15,
        remove_shadows: bool = True
    ) -> dict:
        """
        Complete pipeline to process an exam sheet from image file.
        
        This is the main method that combines all steps:
        1. Load image
        2. Remove shadows (optional, improves detection)
        3. Align image using corner markers
        4. Convert to black and white
        5. Detect marked answers
        
        Args:
            image_path: Path to the exam sheet image
            num_questions: Number of questions
            choices_per_question: Number of choices per question
            template_size: Template size
            margin: Template margin
            alignment_square_size: Alignment square size
            mark_threshold: Threshold for detecting marked cells
            remove_shadows: If True, removes shadows before processing (recommended)
            
        Returns:
            Dictionary containing:
                - 'success': bool indicating if processing succeeded
                - 'answers': List of detected answers (if successful)
                - 'error': Error message (if failed)
                - 'aligned_image': Aligned image (if successful)
                - 'shadow_removed_image': Shadow-removed image (if remove_shadows=True)
        """
        # Load image
        image = self.load_image(image_path)
        if image is None:
            return {
                'success': False,
                'error': f'Failed to load image: {image_path}',
                'answers': None,
                'aligned_image': None,
                'shadow_removed_image': None
            }
        
        # Remove shadows if requested (improves marker and mark detection)
        processed_image = image
        shadow_removed_image = None
        if remove_shadows:
            # Convert to grayscale and remove shadows
            gray_no_shadows = self.remove_shadows(image)
            # Convert back to BGR for alignment
            shadow_removed_image = cv2.cvtColor(gray_no_shadows, cv2.COLOR_GRAY2BGR)
            processed_image = shadow_removed_image
        
        # Align image
        aligned = self.align_exam_image(
            processed_image, template_size, margin, alignment_square_size
        )
        if aligned is None:
            return {
                'success': False,
                'error': 'Failed to align image (could not find 4 alignment markers)',
                'answers': None,
                'aligned_image': None,
                'shadow_removed_image': shadow_removed_image
            }
        
        # Detect answers (black and white conversion happens inside)
        answers = self.detect_marked_answers(
            aligned, num_questions, choices_per_question,
            template_size, margin, alignment_square_size, mark_threshold
        )
        
        return {
            'success': True,
            'answers': answers,
            'error': None,
            'aligned_image': aligned,
            'shadow_removed_image': shadow_removed_image
        }
