# Guía de Uso: Sistema de Evaluación de Hojas de Respuestas

Esta guía explica cómo usar el sistema de evaluación de exámenes basado en CV (Visión por Computadora).

## Descripción General

El sistema utiliza OpenCV para:
1. Generar plantillas imprimibles de hojas de respuestas de exámenes
2. Procesar exámenes escaneados/fotografiados
3. Detectar y validar automáticamente las respuestas de los estudiantes

## Clases Principales

### `GeneradorPlantillas`

Clase para generar plantillas de hojas de respuestas.

```python
from exam_evaluator import GeneradorPlantillas

generador = GeneradorPlantillas()
plantilla = generador.generar_plantilla_hoja_examen(
    titulo="Examen Final",
    num_preguntas=20,
    opciones_por_pregunta=4
)
```

### `ReconocedorRespuestas`

Clase para procesar y reconocer respuestas en hojas de examen.

```python
from exam_evaluator import ReconocedorRespuestas

reconocedor = ReconocedorRespuestas()
resultado = reconocedor.procesar_hoja_examen(
    'examen_escaneado.png',
    num_preguntas=20,
    opciones_por_pregunta=4
)
```

## Inicio Rápido

### 1. Generar una Plantilla de Examen

```python
from exam_evaluator import GeneradorPlantillas
import cv2

generador = GeneradorPlantillas()

# Generar plantilla para 10 preguntas con 4 opciones cada una
plantilla = generador.generar_plantilla_hoja_examen(
    titulo="Examen Parcial",
    num_preguntas=10,
    opciones_por_pregunta=4,
    tamano_hoja=(800, 1000),  # ancho, alto en píxeles
    margen=40,
    tamano_cuadrado_alineacion=40
)

# Guardar como imagen
cv2.imwrite('plantilla_examen.png', plantilla)
```

### 2. Procesar un Examen Rellenado

```python
from exam_evaluator import ReconocedorRespuestas

reconocedor = ReconocedorRespuestas()

# Procesar un examen escaneado/fotografiado
resultado = reconocedor.procesar_hoja_examen(
    'examen_escaneado.png',
    num_preguntas=10,
    opciones_por_pregunta=4,
    tamano_plantilla=(800, 1000),
    margen=40,
    tamano_cuadrado_alineacion=40,
    umbral_marca=0.15  # 15% de la celda debe estar marcada
)

if resultado['exito']:
    respuestas = resultado['respuestas']
    for i, respuesta in enumerate(respuestas):
        if respuesta is not None:
            print(f"P{i+1}: {'ABCD'[respuesta]}")
        else:
            print(f"P{i+1}: INVÁLIDA")
else:
    print(f"Error: {resultado['error']}")
```

## Estructura de la Plantilla

La plantilla generada incluye:

1. **Título** - Nombre del examen en la parte superior
2. **Información del Estudiante** - Campos para nombre y código
3. **Marcadores de Alineación** - Cuatro marcadores en las esquinas (cuadrados anidados)
4. **Cuadrícula de Respuestas** - Preguntas como columnas, opciones como filas
   - Números de pregunta en fila de encabezado
   - Etiquetas de opciones (A, B, C, D) en columna izquierda
   - Celdas vacías para que los estudiantes marquen sus respuestas

## Pipeline de Procesamiento

El método `procesar_hoja_examen` realiza estos pasos:

1. **Cargar Imagen** - Leer la imagen del examen escaneado
2. **Encontrar Marcadores** - Detectar los cuatro marcadores de esquina
3. **Alinear Imagen** - Aplicar transformación de perspectiva para corregir rotación/inclinación
4. **Convertir a Binario** - Crear imagen en blanco y negro para detección
5. **Extraer Celdas** - Calcular coordenadas de todas las celdas de respuesta
6. **Detectar Marcas** - Analizar cada celda para determinar si está marcada
7. **Validar Respuestas** - Asegurar exactamente una respuesta por pregunta

## Reglas de Validación de Respuestas

- **Válida**: Exactamente una celda marcada para la pregunta → Retorna índice de respuesta (0-3 para A-D)
- **Inválida**: Ninguna celda marcada → Retorna `None`
- **Inválida**: Múltiples celdas marcadas → Retorna `None`

## Parámetros de Configuración

### Generación de Plantilla

- `titulo`: Texto del título del examen
- `num_preguntas`: Número de preguntas (columnas en la cuadrícula)
- `opciones_por_pregunta`: Número de opciones por pregunta (filas, ej. 4 para A-D)
- `tamano_hoja`: Tupla de (ancho, alto) en píxeles
- `margen`: Margen exterior en píxeles
- `tamano_cuadrado_alineacion`: Tamaño de los marcadores de alineación de esquina

### Detección de Marcas

- `umbral_marca`: Proporción mínima de píxeles negros para considerar una celda como marcada (predeterminado: 0.15)
  - Valores más bajos (ej. 0.10) = más sensible, puede detectar marcas ligeras o ruido
  - Valores más altos (ej. 0.30) = menos sensible, requiere marcas más oscuras/grandes

## Ejemplos

Ejecutar los scripts de ejemplo para ver el sistema en acción:

```bash
# Flujo de trabajo completo en español
python examples/demo_flujo_completo_espanol.py

# Generar una plantilla básica (inglés)
python examples/generate_exam_sheet.py

# Flujo de trabajo completo (inglés)
python examples/demo_complete_workflow.py
```

## Métodos Principales

### GeneradorPlantillas

#### `generar_plantilla_hoja_examen()`

Genera una plantilla de hoja de respuestas imprimible.

**Parámetros:**
- `titulo` (str): Título del examen
- `num_preguntas` (int): Número de preguntas
- `opciones_por_pregunta` (int): Opciones por pregunta
- `tamano_hoja` (tuple): (ancho, alto) en píxeles
- `margen` (int): Margen en píxeles
- `tamano_cuadrado_alineacion` (int): Tamaño de marcadores

**Retorna:** Imagen numpy (BGR) con la plantilla

### ReconocedorRespuestas

#### `procesar_hoja_examen()`

Pipeline completo para procesar una hoja de examen.

**Parámetros:**
- `ruta_imagen` (str): Ruta al archivo de imagen
- `num_preguntas` (int): Número de preguntas
- `opciones_por_pregunta` (int): Opciones por pregunta
- `tamano_plantilla` (tuple): Tamaño de la plantilla
- `margen` (int): Margen de la plantilla
- `tamano_cuadrado_alineacion` (int): Tamaño de marcadores
- `umbral_marca` (float): Umbral de detección (0-1)

**Retorna:** Diccionario con:
- `exito` (bool): Si el procesamiento fue exitoso
- `respuestas` (list): Lista de respuestas detectadas
- `error` (str): Mensaje de error si falló
- `imagen_alineada` (ndarray): Imagen alineada si fue exitoso

#### Otros Métodos Útiles

- `cargar_imagen(ruta)`: Cargar imagen desde archivo
- `convertir_a_escala_grises(imagen)`: Convertir a escala de grises
- `convertir_a_blanco_y_negro(imagen)`: Convertir a binario
- `alinear_imagen_examen(imagen)`: Alinear usando marcadores
- `extraer_celdas_respuestas(imagen)`: Obtener coordenadas de celdas
- `detectar_respuestas_marcadas(imagen)`: Detectar todas las respuestas

## Consejos para Mejores Resultados

1. **Escaneo**:
   - Usar alto contraste (escanear en modo blanco y negro)
   - Asegurar buena iluminación
   - Mantener la hoja plana para minimizar distorsión

2. **Instrucciones para Estudiantes**:
   - Rellenar celdas completamente con marcas oscuras
   - Usar bolígrafo o lápiz oscuro (no lápiz claro)
   - Borrar completamente si cambian de respuesta
   - Marcar SOLO UNA respuesta por pregunta

3. **Impresión de Plantilla**:
   - Imprimir en alta calidad (300 DPI o superior)
   - Usar papel blanco con buen contraste
   - Evitar redimensionar que pueda distorsionar los marcadores

## Solución de Problemas

### "Falló al alinear imagen"
- Verificar que los 4 marcadores de esquina sean visibles
- Asegurar que los marcadores no estén oscurecidos o dañados
- Intentar mejorar calidad/iluminación de la imagen

### Respuestas no detectadas
- Reducir `umbral_marca` (ej. de 0.15 a 0.10)
- Verificar que las marcas sean suficientemente oscuras
- Verificar que la imagen no esté muy brillante/lavada

### Falsos positivos (celdas sin marcar detectadas como marcadas)
- Aumentar `umbral_marca` (ej. de 0.15 a 0.20)
- Verificar si hay suciedad/marcas en el papel
- Asegurar escaneo limpio

## Compatibilidad

El sistema mantiene compatibilidad con la clase original `PatternRecognizer` en inglés:

```python
# Clase original (inglés) - aún funciona
from exam_evaluator import PatternRecognizer
recognizer = PatternRecognizer()

# Nuevas clases (español)
from exam_evaluator import ReconocedorRespuestas, GeneradorPlantillas
reconocedor = ReconocedorRespuestas()
generador = GeneradorPlantillas()
```

## Estructura del Proyecto

```
src/exam_evaluator/
├── __init__.py                      # Exporta todas las clases
├── pattern_recognition.py           # Clase original en inglés
├── reconocimiento_respuestas.py     # Nueva clase en español (reconocimiento)
└── generador_plantillas.py          # Nueva clase en español (generación)
```

## Referencias

- Documentación completa (inglés): `docs/USAGE_GUIDE.md`
- Ejemplos en español: `examples/demo_flujo_completo_espanol.py`
- Tests: `tests/test_clases_espanol.py`
