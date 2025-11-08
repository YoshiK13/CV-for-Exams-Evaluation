# Shadow Removal Feature

## Overview

The shadow removal feature improves answer detection accuracy when processing exam sheets with uneven lighting, shadows, or illumination gradients. This is particularly useful for scanned documents or photos taken in non-ideal lighting conditions.

## How It Works

The shadow removal algorithm uses morphological operations to normalize the image lighting:

1. **Gaussian Blur**: Smooths the image to reduce noise (5×5 kernel)
2. **Background Estimation**: Uses morphological dilation with a large elliptical kernel (20×20, 3 iterations) to estimate the background illumination
3. **Normalization**: Divides the original image by the estimated background to remove shadows
4. **Histogram Equalization**: Enhances contrast for better marker detection

## Usage

### Spanish API (ReconocedorRespuestas)

```python
from exam_evaluator import ReconocedorRespuestas

reconocedor = ReconocedorRespuestas()

# Process with shadow removal (recommended)
resultado = reconocedor.procesar_hoja_examen(
    'examen.png',
    num_preguntas=10,
    quitar_sombras=True  # ← Enables shadow removal
)

# Access shadow-removed image
if resultado['imagen_sin_sombras'] is not None:
    cv2.imwrite('sin_sombras.png', resultado['imagen_sin_sombras'])
```

### English API (PatternRecognizer)

```python
from exam_evaluator import PatternRecognizer

recognizer = PatternRecognizer()

# Process with shadow removal (recommended)
result = recognizer.process_exam_sheet(
    'exam.png',
    num_questions=10,
    remove_shadows=True  # ← Enables shadow removal
)

# Access shadow-removed image
if result['shadow_removed_image'] is not None:
    cv2.imwrite('no_shadows.png', result['shadow_removed_image'])
```

## When to Use Shadow Removal

### ✅ Recommended for:
- Scanned documents with uneven illumination
- Photos taken under poor lighting conditions
- Images with shadows cast on the paper
- Documents with natural lighting gradients
- Real-world exam sheets (non-ideal conditions)

### ⚠️ May not be needed for:
- Clean digital templates
- High-quality scans with uniform lighting
- Test images generated programmatically

## Performance Impact

- **Processing Time**: Adds ~50-100ms per image (depending on image size)
- **Accuracy Improvement**: Significantly improves detection on shadowed images
- **Default Setting**: Enabled by default (`quitar_sombras=True` / `remove_shadows=True`)

## Technical Details

### Algorithm Parameters
- **Gaussian Blur Kernel**: 5×5 pixels
- **Morphological Kernel**: 20×20 ellipse
- **Dilation Iterations**: 3
- **Output**: 8-bit grayscale image (0-255)

### Pipeline Integration

**Without shadow removal:**
```
Load → Align → Convert to B&W → Detect
```

**With shadow removal (recommended):**
```
Load → Remove Shadows → Align → Convert to B&W → Detect
```

## Example Results

The shadow removal feature processes the image before alignment to ensure that:
1. Alignment markers are clearly visible even under poor lighting
2. Answer cell detection is more reliable
3. The threshold-based mark detection works consistently

See `examples/demo_flujo_completo_espanol.py` for a complete working example.

## Disabling Shadow Removal

If you need to disable shadow removal (e.g., for perfectly lit images):

```python
# Spanish
resultado = reconocedor.procesar_hoja_examen(
    'examen.png',
    quitar_sombras=False
)

# English
result = recognizer.process_exam_sheet(
    'exam.png',
    remove_shadows=False
)
```

## Related Documentation

- [Pattern Recognition Guide](PATTERN_RECOGNITION.md)
- [Quick Start Guide](QUICK_START.md)
- [Spanish Usage Guide](GUIA_USO_ESPANOL.md)
