"""
Módulo de Generación de Plantillas para Evaluación de Exámenes
Este módulo proporciona capacidades de generación de plantillas de hojas de respuestas.
"""

import cv2
import numpy as np
from typing import Tuple


class GeneradorPlantillas:
    """
    Una clase para generar plantillas de hojas de respuestas de exámenes.
    
    Esta clase proporciona métodos para crear plantillas imprimibles de hojas
    de respuestas con marcadores de alineación y cuadrículas de respuestas.
    """
    
    def __init__(self):
        """Inicializar el GeneradorPlantillas."""
        self.opencv_version = cv2.__version__
    
    def generar_plantilla_hoja_examen(
        self,
        titulo: str = "Examen",
        num_preguntas: int = 10,
        opciones_por_pregunta: int = 4,
        tamano_hoja: Tuple[int, int] = (800, 1000),
        margen: int = 40,
        tamano_cuadrado_alineacion: int = 40,
        tamano_qr: int = 200,
    ) -> np.ndarray:
        """
        Generar una plantilla de hoja de respuestas de examen imprimible en blanco.

        La plantilla contiene:
        - Un título centrado en la parte superior
        - Un cuadro para nombre del estudiante/código bajo el título
        - Un marcador de posición para código QR (superior derecho por defecto)
        - Cuatro cuadrados de alineación rellenos ubicados cerca de las esquinas
          (usados para detectar y corregir rotación/escala de imágenes escaneadas)
        - Un área de preguntas con filas numeradas y burbujas circulares para opción múltiple

        Args:
            titulo: Texto del título del examen
            num_preguntas: Número de preguntas de opción múltiple
            opciones_por_pregunta: Número de opciones por pregunta (ej., 4 para A-D)
            tamano_hoja: (ancho, alto) en píxeles para la imagen generada
            margen: Margen exterior en píxeles
            tamano_cuadrado_alineacion: Tamaño en píxeles de los cuadrados de alineación
            tamano_qr: Tamaño en píxeles del cuadrado marcador de posición QR

        Returns:
            Una imagen numpy BGR (uint8) con la plantilla dibujada
        """
        ancho, alto = tamano_hoja
        img = np.ones((alto, ancho, 3), dtype=np.uint8) * 255

        # Título
        escala_titulo = 1.2
        grosor_titulo = 2
        fuente_titulo = cv2.FONT_HERSHEY_SIMPLEX
        (t_w, t_h), _ = cv2.getTextSize(titulo, fuente_titulo, escala_titulo, grosor_titulo)
        titulo_x = (ancho - t_w) // 2
        titulo_y = margen + t_h
        cv2.putText(img, titulo, (titulo_x, titulo_y), fuente_titulo, escala_titulo, (0, 0, 0), grosor_titulo, cv2.LINE_AA)

        # Dibujar marcadores de alineación estilo buscador QR (cuadrados anidados) en las cuatro esquinas
        def dibujar_buscador(x, y, size):
            # exterior negro
            cv2.rectangle(img, (int(x), int(y)), (int(x + size), int(y + size)), (0, 0, 0), -1)
            # interior blanco
            inset1 = int(size * 0.18)
            cv2.rectangle(img, (int(x + inset1), int(y + inset1)), (int(x + size - inset1), int(y + size - inset1)), (255, 255, 255), -1)
            # centro negro
            inset2 = int(size * 0.36)
            cv2.rectangle(img, (int(x + inset2), int(y + inset2)), (int(x + size - inset2), int(y + size - inset2)), (0, 0, 0), -1)

        sq = tamano_cuadrado_alineacion
        # colocarlos en los márgenes pero asegurar que el área de la tabla los evite
        dibujar_buscador(margen, margen, sq)  # superior-izquierda
        dibujar_buscador(ancho - margen - sq, margen, sq)  # superior-derecha
        dibujar_buscador(margen, alto - margen - sq, sq)  # inferior-izquierda
        dibujar_buscador(ancho - margen - sq, alto - margen - sq, sq)  # inferior-derecha

        # Celdas de Nombre del Estudiante y Código (celdas individuales) bajo el título
        parte_superior_cuadro = titulo_y + 15
        altura_cuadro = 50
        # Dejar espacio horizontal para los marcadores de alineación manteniendo dentro de márgenes + sq
        izquierda_contenido = margen + sq + 15
        derecha_contenido = ancho - margen - sq - 15
        # dividir en dos celdas: Nombre (70%) y Código de Estudiante (30%)
        total_w = derecha_contenido - izquierda_contenido
        nombre_w = int(total_w * 0.7)
        codigo_w = total_w - nombre_w - 8

        izquierda_nombre = izquierda_contenido
        derecha_nombre = izquierda_nombre + nombre_w
        izquierda_codigo = derecha_nombre + 8
        derecha_codigo = izquierda_codigo + codigo_w

        cv2.rectangle(img, (izquierda_nombre, parte_superior_cuadro), (derecha_nombre, parte_superior_cuadro + altura_cuadro), (0, 0, 0), 2)
        cv2.putText(img, "Nombre:", (izquierda_nombre + 8, parte_superior_cuadro + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        cv2.rectangle(img, (izquierda_codigo, parte_superior_cuadro), (derecha_codigo, parte_superior_cuadro + altura_cuadro), (0, 0, 0), 2)
        cv2.putText(img, "Código:", (izquierda_codigo + 8, parte_superior_cuadro + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Tabla de preguntas: las opciones son filas, las preguntas son columnas
        parte_superior_tabla = parte_superior_cuadro + altura_cuadro + 20
        # reducir ancho de tabla y centrarla entre izquierda_contenido y derecha_contenido
        contenido_w = derecha_contenido - izquierda_contenido
        tabla_w = int(contenido_w * 0.95)
        izquierda_tabla = izquierda_contenido + (contenido_w - tabla_w) // 2
        derecha_tabla = izquierda_tabla + tabla_w
        # reducir altura total de la tabla para mantener la hoja compacta (más pequeña que antes)
        altura_disponible = alto - parte_superior_tabla - margen - sq - 20
        altura_tabla = int(altura_disponible * 0.85)  # usar 85% del disponible
        parte_inferior_tabla = parte_superior_tabla + altura_tabla

        # Calcular tamaños de celda. Agregar una fila de encabezado para números de pregunta
        n_cols = max(1, num_preguntas)
        n_filas_opciones = max(1, opciones_por_pregunta)
        encabezado_h = max(18, int(altura_tabla * 0.10))
        restante_h = altura_tabla - encabezado_h
        # altura de fila de opción compacta
        fila_opcion_h = max(15, int(restante_h / n_filas_opciones))
        # recalcular parte_inferior_tabla para ajustar encabezado + filas de opciones
        altura_tabla = encabezado_h + fila_opcion_h * n_filas_opciones
        parte_inferior_tabla = parte_superior_tabla + altura_tabla

        # Reservar una pequeña columna izquierda para etiquetas de opciones
        ancho_col_etiqueta = max(30, int(tabla_w * 0.08))
        area_q_w = tabla_w - ancho_col_etiqueta
        ancho_celda = area_q_w / n_cols

        # Dibujar tabla: primero dibujar fila de encabezado con números de pregunta. Dibujamos primero la columna de etiquetas.
        # Dibujar encabezado de columna de etiquetas (vacío)
        lbl_x1 = izquierda_tabla
        lbl_x2 = izquierda_tabla + ancho_col_etiqueta
        cv2.rectangle(img, (lbl_x1, parte_superior_tabla), (lbl_x2, parte_superior_tabla + encabezado_h), (0, 0, 0), 1)

        for col in range(n_cols):
            col_x1 = int(izquierda_tabla + ancho_col_etiqueta + col * ancho_celda)
            col_x2 = int(izquierda_tabla + ancho_col_etiqueta + (col + 1) * ancho_celda)
            # celda de encabezado
            encabezado_y1 = parte_superior_tabla
            encabezado_y2 = parte_superior_tabla + encabezado_h
            cv2.rectangle(img, (col_x1, encabezado_y1), (col_x2, encabezado_y2), (0, 0, 0), 1)
            num_pregunta = col + 1
            # centrar número de pregunta en celda de encabezado
            (qw, qh), _ = cv2.getTextSize(str(num_pregunta), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            qx = col_x1 + (col_x2 - col_x1 - qw) // 2
            qy = encabezado_y1 + (encabezado_h + qh) // 2
            cv2.putText(img, str(num_pregunta), (qx, qy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # dibujar filas de opciones
            for fila in range(n_filas_opciones):
                fila_y1 = encabezado_y2 + fila * fila_opcion_h
                fila_y2 = encabezado_y2 + (fila + 1) * fila_opcion_h
                cv2.rectangle(img, (col_x1, fila_y1), (col_x2, fila_y2), (0, 0, 0), 1)

                # Sin círculo: los estudiantes pueden marcar celdas de diferentes maneras; dejar celda vacía
                # Opcionalmente dibujar un cuadro guía interior muy ligero (deshabilitado por defecto)
                # cx = int((col_x1 + col_x2) / 2)
                # cy = int((fila_y1 + fila_y2) / 2)
                # cv2.rectangle(img, (cx-8, cy-8), (cx+8, cy+8), (0,0,0), 1)

        # Dibujar filas de columna de etiquetas y etiquetas
        for fila in range(n_filas_opciones):
            fila_y1 = parte_superior_tabla + encabezado_h + fila * fila_opcion_h
            fila_y2 = parte_superior_tabla + encabezado_h + (fila + 1) * fila_opcion_h
            cv2.rectangle(img, (lbl_x1, fila_y1), (lbl_x2, fila_y2), (0, 0, 0), 1)
            etiqueta = chr(ord('A') + fila) if fila < 26 else str(fila + 1)
            cy = int((fila_y1 + fila_y2) / 2)
            cv2.putText(img, etiqueta, (lbl_x1 + 8, cy + int(fila_opcion_h * 0.15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        return img
