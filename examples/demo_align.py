"""Example: simulate a scanned rotated/translated page and align it back to template

Run from repo root:
    python3 examples/demo_align.py

This script generates a template, applies a perspective warp to simulate a scan,
then attempts to detect alignment squares and warp it back.
"""
import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import PatternRecognizer

ROOT = os.path.dirname(__file__)
TEMPLATE_PNG = os.path.join(ROOT, 'generated_template.png')
SCANNED_PNG = os.path.join(ROOT, 'simulated_scanned.png')
ALIGNED_PNG = os.path.join(ROOT, 'aligned_template.png')


def simulate_scan(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    # Use the known alignment square centers from the template layout
    margin = 120
    sq = 120
    # centers of the four alignment squares in the template coordinate system
    src = np.float32([
        [margin + sq / 2.0, margin + sq / 2.0],
        [w - margin - sq / 2.0, margin + sq / 2.0],
        [margin + sq / 2.0, h - margin - sq / 2.0],
        [w - margin - sq / 2.0, h - margin - sq / 2.0],
    ])

    # perturb each marker by a small amount to simulate a real scanned page
    rng = np.random.default_rng(42)
    offsets = rng.normal(scale=30.0, size=src.shape).astype(np.float32)
    dst = src + offsets

    # Compute perspective transform that maps template marker positions to perturbed positions
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
    # add slight blur to simulate scanner/phone capture
    warped = cv2.GaussianBlur(warped, (3, 3), 0)
    return warped


def main():
    recognizer = PatternRecognizer()

    if not os.path.exists(TEMPLATE_PNG):
        print("Template not found — generating one first...")
        img = recognizer.generate_exam_sheet_template(title='Demo Exam', num_questions=20)
        cv2.imwrite(TEMPLATE_PNG, img)
    else:
        img = cv2.imread(TEMPLATE_PNG)

    scanned = simulate_scan(img)
    cv2.imwrite(SCANNED_PNG, scanned)
    print(f"Simulated scanned image saved to: {SCANNED_PNG}")

    aligned = recognizer.align_exam_image(scanned)
    if aligned is None:
        print("Alignment failed: could not find 4 markers")
    else:
        cv2.imwrite(ALIGNED_PNG, aligned)
        print(f"Aligned image saved to: {ALIGNED_PNG}")


if __name__ == '__main__':
    main()
