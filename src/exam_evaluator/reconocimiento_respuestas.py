"""
Modulo de Reconocimiento de Respuestas para Evaluacion de Examenes

Este modulo proporciona capacidades de reconocimiento de patrones usando OpenCV para analisis de 
imagenes de examenes.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional

# Clase para el reconocimiento de respuestas en examenes
class ReconocedorRespuestas:
    
    # Se inicializa el Reconocedor de respuestas, con open CV
    def __init__(self):
        self.opencv_version = cv2.__version__
    
    # Cargar una imagen desde la ruta especificada.
    # La imagen se carga como un array numpy (forma en la que trabaja open CV), o None si falla la carga
    def cargar_imagen(self, ruta_imagen: str) -> Optional[np.ndarray]:

        imagen = cv2.imread(ruta_imagen)

        if imagen is None:
            print(f"Error: No se pudo cargar la imagen desde {ruta_imagen}")
            return None
        
        return imagen
    
    # Funcion auxiliar para convertir a escala de grises
    def convertir_a_escala_grises(self, imagen: np.ndarray) -> np.ndarray:

        # Si la imagen ya esta en escala de grises (np 2d array) no se altera
        if len(imagen.shape) == 2:
            return imagen
        
        return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    def encontrar_cuadrados_alineacion(self, imagen: np.ndarray, area_min: int = 2000) -> List[Tuple[int, int]]:
        # Encontrar los cuadrados de alineacion en las esquinas de la hoja de examen.
        # Retorna una lista de tuplas (x, y) con las coordenadas centrales de los cuadrados encontrados.

        # Usar la conversion a escala de grises y umbralizacion para detectar contornos
        grises = self.convertir_a_escala_grises(imagen)
        _, umbral = cv2.threshold(grises, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Usar cierre morfologico para reducir pequeños agujeros/efectos de desenfoque
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        umbral = cv2.morphologyEx(umbral, cv2.MORPH_CLOSE, kernel)
        contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrar contornos para encontrar cuadrados de alineacion
        marcadores = []
        for cnt in contornos:
            area = cv2.contourArea(cnt)
            if area < max(800, area_min * 0.2):
                continue

            # rectangulo delimitador y relación de aspecto
            x, y, ancho, alto = cv2.boundingRect(cnt)

            if alto == 0:
                continue

            relacion_aspecto = float(ancho) / float(alto)

            # solidez: cuánto del cuadrado delimitador esta cubierto por el contorno
            area_rect = float(ancho * alto)
            solidez = area / area_rect if area_rect > 0 else 0

            # Aceptar contornos aproximadamente cuadrados y bastante sólidos
            if 0.5 <= relacion_aspecto <= 2.0 and solidez > 0.4 and area > area_min * 0.1:
                cx = x + ancho // 2
                cy = y + alto // 2
                marcadores.append((cx, cy))

        return marcadores

    # Retornar posiciones centrales de marcadores esperadas para un tamaño de plantilla dado.
    def _posiciones_marcadores_esperadas(self, tamano_plantilla: Tuple[int, int], margen: int, tamano_cuadrado_alineacion: int) -> np.ndarray:

        ancho, alto = tamano_plantilla
        cuadrado = float(tamano_cuadrado_alineacion)

        # Posiciones esperadas de los marcadores en las esquinas
        return np.array([
            [margen + cuadrado / 2.0, margen + cuadrado / 2.0],
            [ancho - margen - cuadrado / 2.0, margen + cuadrado / 2.0],
            [margen + cuadrado / 2.0, alto - margen - cuadrado / 2.0],
            [ancho - margen - cuadrado / 2.0, alto - margen - cuadrado / 2.0],
        ], dtype=np.float32)

    # Seleccionar el candidato más cercano a cada esquina esperada.
    def _seleccionar_marcadores_mas_cercanos(self, candidatos: List[Tuple[int, int]], esperados: np.ndarray) -> Optional[np.ndarray]:

        # Si hay menos de 4 candidatos, no se puede alinear
        if len(candidatos) < 4:
            return None
        
        # Convertir a lista de floats para mayor precision
        cand = [(float(x), float(y)) for x, y in candidatos]
        pts_origen = []

        # Para cada punto esperado, elegir el candidato restante mas cercano
        for ex in esperados:
            # Calcular distancias al cuadrado
            dists = [((cx - ex[0])**2 + (cy - ex[1])**2, i) for i, (cx, cy) in enumerate(cand)]

            # Si no hay distancias, no se puede alinear
            if not dists:
                return None

            # Ordenar distancias y seleccionar el mas cercano
            dists.sort()
            mejor_idx = dists[0][1]
            mejor = cand.pop(mejor_idx)
            pts_origen.append(mejor)

        # Convertir a array de floats, con los puntos de origen
        return np.array(pts_origen, dtype=np.float32)

    # Alinear una imagen de examen usando los marcadores encontrados.
    def alinear_imagen_examen(self, imagen: np.ndarray, tamano_plantilla: Tuple[int, int] = (800, 1000), margen: int = 40, tamano_cuadrado_alineacion: int = 40) -> Optional[np.ndarray]:

        # Encontrar los cuadrados de alineación en la imagen
        candidatos = self.encontrar_cuadrados_alineacion(imagen)
        if len(candidatos) < 4:
            return None


        altura_img, ancho_img = imagen.shape[:2]
        # posiciones esperadas en el sistema de coordenadas de la imagen escaneada
        esperados_img = self._posiciones_marcadores_esperadas((ancho_img, altura_img), margen, tamano_cuadrado_alineacion)
        origen = self._seleccionar_marcadores_mas_cercanos(candidatos, esperados_img)
        if origen is None:
            return None

        # posiciones de destino en el sistema de coordenadas de la plantilla
        destino = self._posiciones_marcadores_esperadas(tamano_plantilla, margen, tamano_cuadrado_alineacion)

        # Calcular la transformacion de perspectiva y aplicarla
        MATRIZ_TRANS = cv2.getPerspectiveTransform(origen, destino)
        ancho, alto = tamano_plantilla
        deformada = cv2.warpPerspective(imagen, MATRIZ_TRANS, (ancho, alto), flags=cv2.INTER_LINEAR)
        
        return deformada

    # Eliminar sombras de una imagen para mejorar la deteccion usando morfologia de OpenCV.
    def quitar_sombras(self, imagen: np.ndarray) -> np.ndarray:
        
        # Usar el metodo auxiliar para convertir a escala de grises
        grises = self.convertir_a_escala_grises(imagen)
        
        # Pipeline optimizado con OpenCV para eliminar sombras
        # Desenfoque + dilatacion morfologica + division normalizada
        desenfocada = cv2.GaussianBlur(grises, (5, 5), 0)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        fondo = cv2.morphologyEx(desenfocada, cv2.MORPH_DILATE, kernel, iterations=3)
        sin_sombras = cv2.divide(desenfocada, fondo, scale=255)
        
        # Se retorna equalizada la imagen
        return cv2.equalizeHist(sin_sombras)

    # Convertir a blanco y negro
    def convertir_a_blanco_y_negro(self, imagen: np.ndarray, usar_adaptativo: bool = False, quitar_sombras: bool = False) -> np.ndarray:
        
        # Conversion a grises
        grises = self.convertir_a_escala_grises(imagen)
        
        # Quitar sombras solo si se solicita directamente
        if quitar_sombras:
            grises = self.quitar_sombras(grises)
        
        # Pipeline de umbralizacion optimizado con OpenCV
        # Se utiliza un enfoque adaptativo (mejor para iluminacion variable) o simple (por defecto)
        if usar_adaptativo:
            # Blur + umbral adaptativo para iluminacion variable
            desenfocada = cv2.GaussianBlur(grises, (5, 5), 0)
            return cv2.adaptiveThreshold(
                desenfocada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        
        else:
            # Umbral simple (optimo para imágenes ya preprocesadas)
            _, binaria = cv2.threshold(grises, 200, 255, cv2.THRESH_BINARY)
            return binaria

    # Extraer las coordenadas de las celdas de respuesta de una hoja de examen alineada.
    def extraer_celdas_respuestas(
        self,
        imagen: np.ndarray,
        num_preguntas: int = 10,
        opciones_por_pregunta: int = 4,
        tamano_plantilla: Tuple[int, int] = (800, 1000),
        margen: int = 40,
        tamano_cuadrado_alineacion: int = 40,
    ) -> List[List[Tuple[int, int, int, int]]]:
        
        ancho, alto = tamano_plantilla
        cuadrado = tamano_cuadrado_alineacion
        
        # Calcular posicion de tabla (debe coincidir con la plantilla)
        # Calculos de titulo y cuadro de nombre
        escala_titulo = 1.2
        grosor_titulo = 2
        fuente_titulo = cv2.FONT_HERSHEY_SIMPLEX
        (ancho_titulo, alto_titulo), _ = cv2.getTextSize("Examen", fuente_titulo, escala_titulo, grosor_titulo)
        titulo_y = margen + alto_titulo

        parte_superior_cuadro = titulo_y + 15
        altura_cuadro = 50
        
        parte_superior_tabla = parte_superior_cuadro + altura_cuadro + 20
        
        izquierda_contenido = margen + cuadrado + 15
        derecha_contenido = ancho - margen - cuadrado - 15
        ancho_contenido = derecha_contenido - izquierda_contenido
        ancho_tabla = int(ancho_contenido * 0.95)
        izquierda_tabla = izquierda_contenido + (ancho_contenido - ancho_tabla) // 2
        
        altura_disponible = alto - parte_superior_tabla - margen - cuadrado - 20
        altura_tabla = int(altura_disponible * 0.85)
        
        n_cols = max(1, num_preguntas)
        n_filas_opciones = max(1, opciones_por_pregunta)
        altura_encabezado = max(18, int(altura_tabla * 0.10))
        altura_restante = altura_tabla - altura_encabezado
        altura_fila_opcion = max(15, int(altura_restante / n_filas_opciones))

        ancho_col_etiqueta = max(30, int(ancho_tabla * 0.08))
        area_q_w = ancho_tabla - ancho_col_etiqueta
        ancho_celda = area_q_w / n_cols
        
        # Extraer coordenadas de celda
        celdas = []
        for col in range(n_cols):
            celdas_pregunta = []
            col_x1 = int(izquierda_tabla + ancho_col_etiqueta + col * ancho_celda)
            col_x2 = int(izquierda_tabla + ancho_col_etiqueta + (col + 1) * ancho_celda)
            
            for fila in range(n_filas_opciones):
                fila_y1 = parte_superior_tabla + altura_encabezado + fila * altura_fila_opcion
                fila_y2 = parte_superior_tabla + altura_encabezado + (fila + 1) * altura_fila_opcion
                
                # Agregar pequeño relleno para evitar bordes
                relleno = 3
                x = col_x1 + relleno
                y = fila_y1 + relleno
                ancho = (col_x2 - col_x1) - 2 * relleno
                alto = (fila_y2 - fila_y1) - 2 * relleno
                
                celdas_pregunta.append((x, y, ancho, alto))
            
            celdas.append(celdas_pregunta)
        
        return celdas

    # Determinar si una celda esta marcada analizando la proporción de pixeles negros
    def es_celda_marcada(
        self,
        imagen_binaria: np.ndarray,
        coordenadas_celda: Tuple[int, int, int, int],
        umbral: float = 0.15
    ) -> bool:
        
        x, y, ancho, alto = coordenadas_celda
        
        # Asegurar que las coordenadas esten dentro de los limites de la imagen
        altura_img, ancho_img = imagen_binaria.shape[:2]
        x = max(0, min(x, ancho_img - 1))
        y = max(0, min(y, altura_img - 1))
        ancho = max(1, min(ancho, ancho_img - x))
        alto = max(1, min(alto, altura_img - y))

        # Extraer region de celda
        celda = imagen_binaria[y:y+alto, x:x+ancho]

        if celda.size == 0:
            return False
        
        # Contar pixeles negros (valor 0 en imagen binaria)
        pixeles_negros = np.sum(celda == 0)
        pixeles_totales = celda.size
        
        # Calcular proporcion
        proporcion_negra = pixeles_negros / pixeles_totales
        
        # Regresa True: si la casilla esta marcada
        # Regresa False: si no esta marcada
        return proporcion_negra >= umbral

    # Detectar y validar las respuestas marcadas
    def detectar_respuestas_marcadas(
        self,
        imagen: np.ndarray,
        num_preguntas: int = 10,
        opciones_por_pregunta: int = 4,
        tamano_plantilla: Tuple[int, int] = (800, 1000),
        margen: int = 40,
        tamano_cuadrado_alineacion: int = 40,
        umbral_marca: float = 0.15,
        preprocesar_sombras: bool = True
    ) -> List[Optional[int]]:
        
        # Preprocesar: Convertir a blanco y negro con eliminacion de sombras
        binaria = self.convertir_a_blanco_y_negro(imagen, quitar_sombras=preprocesar_sombras)
        
        # Extraer coordenadas de celdas
        celdas = self.extraer_celdas_respuestas(
            imagen, num_preguntas, opciones_por_pregunta,
            tamano_plantilla, margen, tamano_cuadrado_alineacion
        )
        
        # Detectar respuestas marcadas
        respuestas = []
        for idx_pregunta, celdas_pregunta in enumerate(celdas):
            opciones_marcadas = []
            
            for idx_opcion, coordenadas_celda in enumerate(celdas_pregunta):
                if self.es_celda_marcada(binaria, coordenadas_celda, umbral_marca):
                    opciones_marcadas.append(idx_opcion)
            
            # Validar: exactamente una respuesta debe estar marcada
            if len(opciones_marcadas) == 1:
                respuestas.append(opciones_marcadas[0])
            
            else:
                # Invalida: ya sea ninguna respuesta o multiples respuestas marcadas
                respuestas.append(None)
        
        # Regresa una lista de respuestas detectadas
        # de forma tal [Pregunta1, Pregunta2, ..., PreguntaN]
        # Y los valores de la forma 0: A, 1: B, 2: C, 3: D, None: invalida
        return respuestas

    # Pipeline completo para procesar una hoja de examen desde archivo de imagen.
    def procesar_hoja_examen(
        self,
        ruta_imagen: str,
        num_preguntas: int = 10,
        opciones_por_pregunta: int = 4,
        tamano_plantilla: Tuple[int, int] = (800, 1000),
        margen: int = 40,
        tamano_cuadrado_alineacion: int = 40,
        umbral_marca: float = 0.15,
        quitar_sombras: bool = True
    ) -> dict:
        
        # Cargar imagen
        imagen = self.cargar_imagen(ruta_imagen)
        if imagen is None:
            return {
                'exito': False,
                'error': f'Falló al cargar imagen: {ruta_imagen}',
                'respuestas': None,
                'imagen_alineada': None,
                'imagen_sin_sombras': None
            }
        
        # Quitar sombras si se solicita
        # Guardamos imagen sin sombras para depuracion, pero la alineacion
        # funciona mejor con la imagen original a color
        imagen_sin_sombras = None
        if quitar_sombras:
            imagen_sin_sombras = self.quitar_sombras(imagen)
        
        # Alinear imagen (usar original a color para mejor detección de marcadores)
        alineada = self.alinear_imagen_examen(
            imagen, tamano_plantilla, margen, tamano_cuadrado_alineacion
        )
        if alineada is None:
            return {
                'exito': False,
                'error': 'Falló al alinear imagen (no se pudieron encontrar 4 marcadores de alineación)',
                'respuestas': None,
                'imagen_alineada': None,
                'imagen_sin_sombras': imagen_sin_sombras
            }
        
        # Detectar respuestas con preprocesamiento de sombras integrado
        respuestas = self.detectar_respuestas_marcadas(
            alineada, num_preguntas, opciones_por_pregunta,
            tamano_plantilla, margen, tamano_cuadrado_alineacion, umbral_marca,
            preprocesar_sombras=quitar_sombras
        )
        
        # Regresar resultados como diccionario con toda la informacion
        return {
            'exito': True,
            'respuestas': respuestas,
            'error': None,
            'imagen_alineada': alineada,
            'imagen_sin_sombras': imagen_sin_sombras
        }
