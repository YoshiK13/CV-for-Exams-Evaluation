# Exam Answer Sheet Format

This document describes the visual format used for printable exam answer sheets and how the evaluator identifies and aligns scanned images.

## Overview

The exam answer sheet is a single-page table-like layout with:

- A centered exam title at the top.
- A student name / student code box under the title.
- A QR code placeholder in the top-right area (used to store metadata like exam id, student id, etc.).
- Four solid black alignment squares near each corner (top-left, top-right, bottom-left, bottom-right).
- A questions area containing numbered rows and circular bubbles for multiple-choice answers (A, B, C, ...).

These corner alignment squares plus the QR position are used to locate the sheet within a scanned image, correct perspective distortion (rotation/scale/skew), and crop/warp the scanned image into a canonical template coordinate system.

## Alignment markers

- Markers are square, filled black boxes placed a fixed distance from the page margins. In the code we use a default `alignment_square_size` of 120 pixels and a `margin` of 120 pixels for an A4/300DPI-like template (2480x3508 px). For other sizes, keep the same relative placement.
- The detection algorithm searches for large, approximately-square filled contours and uses their centers to determine the page corners.
- When exactly four markers are detected, a perspective transform (homography) is computed to map the detected marker positions to the expected marker positions on the template. The scanned image is then warped to the template size.

## QR code

- A QR code placeholder is placed in the top-right area of the template to encode exam-specific data (optional). During processing, the QR region can be cropped from the aligned image and decoded using any QR decoding library (e.g., OpenCV's QRCodeDetector or python-qrcode on generation side).
- The placeholder is a simple square drawn on the template; you can replace it with an actual QR image before printing.

## Questions area

- Questions are laid out in one or two columns depending on the number of questions. Each question has circular bubbles drawn horizontally for each choice (A, B, ...).
- Bubble sizes and spacing are chosen for typical OMR-style marking. When detecting filled bubbles, thresholding and contour or circle detection (Hough transform) is recommended.

## Using the provided utilities

The `PatternRecognizer` class includes convenience methods:

- `generate_exam_sheet_template(title, num_questions, choices_per_question, sheet_size, margin, alignment_square_size, qr_size)`
  - Returns a BGR numpy image of the blank template.

- `find_alignment_squares(image, min_area)`
  - Scans an image (BGR or grayscale) and returns a list of centers of detected square markers.

- `align_exam_image(image, template_size, margin, alignment_square_size)`
  - If four markers are detected, computes a perspective transform and returns the warped image aligned to the canonical template.

## Notes and tips

- For robust detection at scan time, ensure the printed markers are fully black and not dithered.
- Use a high DPI (>=300) when printing to keep bubbles and markers sharp.
- If lighting/scan introduces noise, tweak the thresholding parameters or use morphological operations before contour detection.

## Example workflow

1. Print templates generated with `generate_exam_sheet_template` (optionally embed an actual QR code image into the QR placeholder).
2. Students fill answers by darkening the bubbles.
3. Scan the filled sheets.
4. Use `find_alignment_squares` and `align_exam_image` to align each scanned image.
5. Crop the QR region and decode (if used) and run bubble detection on the aligned image to extract answers.

