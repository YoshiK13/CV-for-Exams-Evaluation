"""
Módulo de Reconocimiento de Respuestas para Evaluación de Exámenes

Este módulo proporciona capacidades de reconocimiento de patrones usando OpenCV para análisis de 
imágenes de exámenes.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional


class ReconocedorRespuestas:
    """
    Una clase para realizar reconocimiento de respuestas en imágenes de exámenes usando OpenCV.
    
    Esta clase proporciona métodos para detectar patrones, formas y características
    en imágenes de exámenes para evaluación automatizada.
    """
    
    def __init__(self):
        """Inicializar el ReconocedorRespuestas."""
        self.opencv_version = cv2.__version__
    
    def cargar_imagen(self, ruta_imagen: str) -> Optional[np.ndarray]:
        """
        Cargar una imagen desde la ruta especificada.
        
        Args:
            ruta_imagen: Ruta al archivo de imagen
            
        Returns:
            La imagen cargada como un array numpy, o None si falla la carga
        """
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            print(f"Error: No se pudo cargar la imagen desde {ruta_imagen}")
            return None
        return imagen
    
    def convertir_a_escala_grises(self, imagen: np.ndarray) -> np.ndarray:
        """
        Convertir una imagen a color a escala de grises.
        
        Args:
            imagen: Imagen de entrada (formato BGR)
            
        Returns:
            Imagen en escala de grises
        """
        return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    
    def aplicar_umbral(self, imagen: np.ndarray, valor_umbral: int = 127) -> np.ndarray:
        """
        Aplicar umbral binario a una imagen.
        
        Args:
            imagen: Imagen de entrada en escala de grises
            valor_umbral: Valor de umbral (0-255)
            
        Returns:
            Imagen binaria umbralizada
        """
        _, imagen_binaria = cv2.threshold(imagen, valor_umbral, 255, cv2.THRESH_BINARY)
        return imagen_binaria
    
    def detectar_bordes(self, imagen: np.ndarray, umbral_bajo: int = 50, 
                        umbral_alto: int = 150) -> np.ndarray:
        """
        Detectar bordes en una imagen usando detección de bordes Canny.
        
        Args:
            imagen: Imagen de entrada en escala de grises
            umbral_bajo: Umbral inferior para detección de bordes
            umbral_alto: Umbral superior para detección de bordes
            
        Returns:
            Imagen con bordes detectados
        """
        bordes = cv2.Canny(imagen, umbral_bajo, umbral_alto)
        return bordes
    
    def encontrar_contornos(self, imagen_binaria: np.ndarray) -> Tuple:
        """
        Encontrar contornos en una imagen binaria.
        
        Args:
            imagen_binaria: Imagen de entrada binaria
            
        Returns:
            Tupla de (contornos, jerarquía)
        """
        contornos, jerarquia = cv2.findContours(
            imagen_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contornos, jerarquia
    
    def detectar_circulos(self, imagen: np.ndarray, radio_min: int = 10, 
                          radio_max: int = 100) -> Optional[np.ndarray]:
        """
        Detectar círculos en una imagen usando Transformada de Hough para Círculos.
        
        Args:
            imagen: Imagen de entrada en escala de grises
            radio_min: Radio mínimo del círculo
            radio_max: Radio máximo del círculo
            
        Returns:
            Array de círculos detectados (x, y, radio) o None
        """
        circulos = cv2.HoughCircles(
            imagen,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=radio_min,
            maxRadius=radio_max
        )
        return circulos
    
    def coincidencia_plantilla(self, imagen: np.ndarray, plantilla: np.ndarray, 
                               umbral: float = 0.8) -> List[Tuple[int, int]]:
        """
        Realizar coincidencia de plantilla para encontrar patrones en una imagen.
        
        Args:
            imagen: Imagen de entrada
            plantilla: Imagen de plantilla a buscar
            umbral: Umbral de coincidencia (0-1)
            
        Returns:
            Lista de coordenadas (x, y) donde se encontró la plantilla
        """
        resultado = cv2.matchTemplate(imagen, plantilla, cv2.TM_CCOEFF_NORMED)
        ubicaciones = np.where(resultado >= umbral)
        coincidencias = list(zip(*ubicaciones[::-1]))
        return coincidencias
    
    def obtener_info_imagen(self, imagen: np.ndarray) -> dict:
        """
        Obtener información sobre una imagen.
        
        Args:
            imagen: Imagen de entrada
            
        Returns:
            Diccionario conteniendo información de la imagen
        """
        return {
            'forma': imagen.shape,
            'dtype': str(imagen.dtype),
            'tamano': imagen.size,
            'dimensiones': len(imagen.shape)
        }
    
    def preprocesar_imagen_examen(self, ruta_imagen: str) -> Optional[np.ndarray]:
        """
        Preprocesar una imagen de examen para reconocimiento de patrones.
        
        Este método aplica un pipeline de preprocesamiento estándar:
        - Cargar imagen
        - Convertir a escala de grises
        - Aplicar desenfoque Gaussiano para reducción de ruido
        - Aplicar umbral adaptativo
        
        Args:
            ruta_imagen: Ruta a la imagen del examen
            
        Returns:
            Imagen binaria preprocesada o None si el procesamiento falla
        """
        # Cargar imagen
        imagen = self.cargar_imagen(ruta_imagen)
        if imagen is None:
            return None
        
        # Convertir a escala de grises
        grises = self.convertir_a_escala_grises(imagen)
        
        # Aplicar desenfoque Gaussiano para reducir ruido
        desenfocada = cv2.GaussianBlur(grises, (5, 5), 0)
        
        # Aplicar umbral adaptativo
        procesada = cv2.adaptiveThreshold(
            desenfocada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return procesada

    # ------------------------------------------------------------------
    # Utilidades de alineación de hojas de examen
    # ------------------------------------------------------------------
    def encontrar_cuadrados_alineacion(self, imagen: np.ndarray, area_min: int = 2000) -> List[Tuple[int, int]]:
        """
        Detectar marcadores de alineación cuadrados rellenos en una imagen.

        Args:
            imagen: Imagen de entrada (BGR o escala de grises)
            area_min: Área mínima del contorno a considerar como cuadrado de alineación

        Returns:
            Lista de centros (x, y) para marcadores cuadrados detectados. Retorna una
            lista vacía si no se encuentra ninguno.
        """
        grises = imagen if len(imagen.shape) == 2 else cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        _, umbral = cv2.threshold(grises, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        # Usar cierre morfológico para reducir pequeños agujeros/efectos de desenfoque
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        umbral = cv2.morphologyEx(umbral, cv2.MORPH_CLOSE, kernel)
        contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        marcadores = []
        for cnt in contornos:
            area = cv2.contourArea(cnt)
            if area < max(800, area_min * 0.2):
                continue

            # rectángulo delimitador y relación de aspecto
            x, y, w, h = cv2.boundingRect(cnt)
            if h == 0:
                continue
            ra = float(w) / float(h)

            # solidez: cuánto del cuadro delimitador está cubierto por el contorno
            area_rect = float(w * h)
            solidez = area / area_rect if area_rect > 0 else 0

            # Aceptar contornos aproximadamente cuadrados y bastante sólidos
            if 0.5 <= ra <= 2.0 and solidez > 0.4 and area > area_min * 0.1:
                cx = x + w // 2
                cy = y + h // 2
                marcadores.append((cx, cy))

        return marcadores

    def _posiciones_marcadores_esperadas(self, tamano_plantilla: Tuple[int, int], margen: int, tamano_cuadrado_alineacion: int) -> np.ndarray:
        """Retornar posiciones centrales de marcadores esperadas para un tamaño de plantilla dado.

        Orden: superior-izquierda, superior-derecha, inferior-izquierda, inferior-derecha.
        """
        w, h = tamano_plantilla
        sq = float(tamano_cuadrado_alineacion)
        return np.array([
            [margen + sq / 2.0, margen + sq / 2.0],
            [w - margen - sq / 2.0, margen + sq / 2.0],
            [margen + sq / 2.0, h - margen - sq / 2.0],
            [w - margen - sq / 2.0, h - margen - sq / 2.0],
        ], dtype=np.float32)

    def _seleccionar_marcadores_mas_cercanos(self, candidatos: List[Tuple[int, int]], esperados: np.ndarray) -> Optional[np.ndarray]:
        """Seleccionar el candidato más cercano a cada esquina esperada.

        Retorna un array de forma (4,2) con coordenadas float32 o None si no hay suficientes candidatos.
        """
        if len(candidatos) < 4:
            return None
        cand = [(float(x), float(y)) for x, y in candidatos]
        pts_origen = []
        # Para cada punto esperado, elegir el candidato restante más cercano
        for ex in esperados:
            dists = [((cx - ex[0])**2 + (cy - ex[1])**2, i) for i, (cx, cy) in enumerate(cand)]
            if not dists:
                return None
            dists.sort()
            mejor_idx = dists[0][1]
            mejor = cand.pop(mejor_idx)
            pts_origen.append(mejor)
        return np.array(pts_origen, dtype=np.float32)

    def alinear_imagen_examen(self, imagen: np.ndarray, tamano_plantilla: Tuple[int, int] = (800, 1000), margen: int = 40, tamano_cuadrado_alineacion: int = 40) -> Optional[np.ndarray]:
        """
        Intentar desinclinear/redimensionar una imagen de examen escaneada usando los cuatro
        cuadrados de alineación de las esquinas. Si se encuentran cuatro marcadores, se calcula
        una transformación de perspectiva para mapear los marcadores escaneados a las esquinas
        ideales de la plantilla.

        Args:
            imagen: Imagen BGR de entrada de un examen escaneado
            tamano_plantilla: (ancho, alto) de salida deseado en píxeles
            margen: Margen usado cuando se generó la plantilla
            tamano_cuadrado_alineacion: Tamaño de los cuadrados de alineación usados en la plantilla

        Returns:
            Imagen deformada alineada al sistema de coordenadas de la plantilla, o None si
            la alineación falló (ej., se detectaron menos de 4 marcadores)
        """
        candidatos = self.encontrar_cuadrados_alineacion(imagen)
        if len(candidatos) < 4:
            return None

        h_img, w_img = imagen.shape[:2]
        # posiciones esperadas en el sistema de coordenadas de la imagen escaneada
        esperados_img = self._posiciones_marcadores_esperadas((w_img, h_img), margen, tamano_cuadrado_alineacion)
        origen = self._seleccionar_marcadores_mas_cercanos(candidatos, esperados_img)
        if origen is None:
            return None

        # posiciones de destino en el sistema de coordenadas de la plantilla
        destino = self._posiciones_marcadores_esperadas(tamano_plantilla, margen, tamano_cuadrado_alineacion)

        M = cv2.getPerspectiveTransform(origen, destino)
        w, h = tamano_plantilla
        deformada = cv2.warpPerspective(imagen, M, (w, h), flags=cv2.INTER_LINEAR)
        return deformada

    def quitar_sombras(self, imagen: np.ndarray) -> np.ndarray:
        """
        Eliminar sombras de una imagen para mejorar la detección.
        
        Este método utiliza operaciones morfológicas para eliminar iluminación desigual
        y sombras que pueden afectar la detección de marcas.
        
        Args:
            imagen: Imagen de entrada (BGR o escala de grises)
            
        Returns:
            Imagen con sombras eliminadas (escala de grises)
        """
        # Convertir a escala de grises si es necesario
        if len(imagen.shape) == 3:
            grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        else:
            grises = imagen.copy()
        
        # Aplicar desenfoque para reducir ruido
        desenfocada = cv2.GaussianBlur(grises, (5, 5), 0)
        
        # Usar operación morfológica de dilatación para obtener el fondo
        # Esto crea una estimación de la iluminación de fondo
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        fondo = cv2.morphologyEx(desenfocada, cv2.MORPH_DILATE, kernel, iterations=3)
        
        # Restar el fondo de la imagen original para eliminar sombras
        # Usamos cv2.divide para normalización
        sin_sombras = cv2.divide(desenfocada, fondo, scale=255)
        
        # Aplicar ecualización de histograma para mejorar contraste
        sin_sombras = cv2.equalizeHist(sin_sombras)
        
        return sin_sombras

    def convertir_a_blanco_y_negro(self, imagen: np.ndarray, usar_adaptativo: bool = False, quitar_sombras: bool = True) -> np.ndarray:
        """
        Convertir una imagen a puro blanco y negro (binario).
        
        Args:
            imagen: Imagen de entrada (BGR o escala de grises)
            usar_adaptativo: Si es True, usar umbralización adaptativa; de lo contrario usar umbral simple
            quitar_sombras: Si es True, eliminar sombras antes de la conversión (recomendado)
            
        Returns:
            Imagen binaria (blanco y negro) donde negro=0, blanco=255
        """
        # Convertir a escala de grises si es necesario
        if len(imagen.shape) == 3:
            grises = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        else:
            grises = imagen.copy()
        
        # Quitar sombras si se solicita (mejora detección con iluminación desigual)
        if quitar_sombras:
            grises = self.quitar_sombras(grises)
        
        if usar_adaptativo:
            # Aplicar desenfoque Gaussiano para reducir ruido
            desenfocada = cv2.GaussianBlur(grises, (5, 5), 0)
            # El umbral adaptativo funciona mejor con iluminación variable
            binaria = cv2.adaptiveThreshold(
                desenfocada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        else:
            # Umbral simple - cualquier cosa por debajo de 200 se considera negro
            # Esto funciona bien para imágenes escaneadas/generadas limpias
            _, binaria = cv2.threshold(grises, 200, 255, cv2.THRESH_BINARY)
        
        return binaria

    def extraer_celdas_respuestas(
        self,
        imagen: np.ndarray,
        num_preguntas: int = 10,
        opciones_por_pregunta: int = 4,
        tamano_plantilla: Tuple[int, int] = (800, 1000),
        margen: int = 40,
        tamano_cuadrado_alineacion: int = 40,
    ) -> List[List[Tuple[int, int, int, int]]]:
        """
        Extraer las coordenadas de las celdas de respuesta de una hoja de examen alineada.
        
        Retorna una lista donde cada elemento representa una pregunta, y contiene
        una lista de tuplas (x, y, w, h) para cada celda de opción.
        
        Args:
            imagen: Imagen de hoja de examen alineada
            num_preguntas: Número de preguntas en el examen
            opciones_por_pregunta: Número de opciones por pregunta
            tamano_plantilla: Tamaño de plantilla (ancho, alto)
            margen: Margen de plantilla
            tamano_cuadrado_alineacion: Tamaño de cuadrados de alineación
            
        Returns:
            Lista de listas conteniendo coordenadas de celda (x, y, ancho, alto)
        """
        ancho, alto = tamano_plantilla
        sq = tamano_cuadrado_alineacion
        
        # Calcular posición de tabla (debe coincidir con la generación de plantilla)
        # Cálculos de título y cuadro de nombre
        escala_titulo = 1.2
        grosor_titulo = 2
        fuente_titulo = cv2.FONT_HERSHEY_SIMPLEX
        (t_w, t_h), _ = cv2.getTextSize("Examen", fuente_titulo, escala_titulo, grosor_titulo)
        titulo_y = margen + t_h
        
        parte_superior_cuadro = titulo_y + 15
        altura_cuadro = 50
        
        parte_superior_tabla = parte_superior_cuadro + altura_cuadro + 20
        
        izquierda_contenido = margen + sq + 15
        derecha_contenido = ancho - margen - sq - 15
        contenido_w = derecha_contenido - izquierda_contenido
        tabla_w = int(contenido_w * 0.95)
        izquierda_tabla = izquierda_contenido + (contenido_w - tabla_w) // 2
        
        altura_disponible = alto - parte_superior_tabla - margen - sq - 20
        altura_tabla = int(altura_disponible * 0.85)
        
        n_cols = max(1, num_preguntas)
        n_filas_opciones = max(1, opciones_por_pregunta)
        encabezado_h = max(18, int(altura_tabla * 0.10))
        restante_h = altura_tabla - encabezado_h
        fila_opcion_h = max(15, int(restante_h / n_filas_opciones))
        
        ancho_col_etiqueta = max(30, int(tabla_w * 0.08))
        area_q_w = tabla_w - ancho_col_etiqueta
        ancho_celda = area_q_w / n_cols
        
        # Extraer coordenadas de celda
        celdas = []
        for col in range(n_cols):
            celdas_pregunta = []
            col_x1 = int(izquierda_tabla + ancho_col_etiqueta + col * ancho_celda)
            col_x2 = int(izquierda_tabla + ancho_col_etiqueta + (col + 1) * ancho_celda)
            
            for fila in range(n_filas_opciones):
                fila_y1 = parte_superior_tabla + encabezado_h + fila * fila_opcion_h
                fila_y2 = parte_superior_tabla + encabezado_h + (fila + 1) * fila_opcion_h
                
                # Agregar pequeño relleno para evitar bordes
                relleno = 3
                x = col_x1 + relleno
                y = fila_y1 + relleno
                w = (col_x2 - col_x1) - 2 * relleno
                h = (fila_y2 - fila_y1) - 2 * relleno
                
                celdas_pregunta.append((x, y, w, h))
            
            celdas.append(celdas_pregunta)
        
        return celdas

    def es_celda_marcada(
        self,
        imagen_binaria: np.ndarray,
        coordenadas_celda: Tuple[int, int, int, int],
        umbral: float = 0.15
    ) -> bool:
        """
        Determinar si una celda está marcada analizando la proporción de píxeles negros.
        
        Args:
            imagen_binaria: Imagen binaria (blanco y negro)
            coordenadas_celda: Tupla de (x, y, ancho, alto) para la celda
            umbral: Proporción mínima de píxeles negros para considerar la celda como marcada (0-1)
            
        Returns:
            True si la celda está marcada, False en caso contrario
        """
        x, y, w, h = coordenadas_celda
        
        # Asegurar que las coordenadas estén dentro de los límites de la imagen
        img_h, img_w = imagen_binaria.shape[:2]
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))
        
        # Extraer región de celda
        celda = imagen_binaria[y:y+h, x:x+w]
        
        if celda.size == 0:
            return False
        
        # Contar píxeles negros (valor 0 en imagen binaria)
        pixeles_negros = np.sum(celda == 0)
        pixeles_totales = celda.size
        
        # Calcular proporción
        proporcion_negra = pixeles_negros / pixeles_totales
        
        return proporcion_negra >= umbral

    def detectar_respuestas_marcadas(
        self,
        imagen: np.ndarray,
        num_preguntas: int = 10,
        opciones_por_pregunta: int = 4,
        tamano_plantilla: Tuple[int, int] = (800, 1000),
        margen: int = 40,
        tamano_cuadrado_alineacion: int = 40,
        umbral_marca: float = 0.15
    ) -> List[Optional[int]]:
        """
        Detectar respuestas marcadas de una imagen de hoja de examen.
        
        Este método realiza el pipeline completo:
        1. Convierte la imagen a blanco y negro
        2. Extrae coordenadas de celdas de respuesta
        3. Detecta qué celdas están marcadas
        4. Valida que solo una respuesta por pregunta esté marcada
        
        Args:
            imagen: Imagen de hoja de examen de entrada (debe estar alineada)
            num_preguntas: Número de preguntas
            opciones_por_pregunta: Número de opciones por pregunta
            tamano_plantilla: Tamaño de plantilla
            margen: Margen de plantilla
            tamano_cuadrado_alineacion: Tamaño de cuadrado de alineación
            umbral_marca: Umbral para detectar celdas marcadas
            
        Returns:
            Lista de respuestas detectadas (indexadas en 0), None para preguntas inválidas/sin marcar
            Ejemplo: [0, 2, 1, None, 3, ...] significa Q1=A, Q2=C, Q3=B, Q4=inválida, Q5=D
        """
        # Convertir a blanco y negro
        binaria = self.convertir_a_blanco_y_negro(imagen)
        
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
                # Inválida: ya sea ninguna respuesta o múltiples respuestas marcadas
                respuestas.append(None)
        
        return respuestas

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
        """
        Pipeline completo para procesar una hoja de examen desde archivo de imagen.
        
        Este es el método principal que combina todos los pasos:
        1. Cargar imagen
        2. Quitar sombras (opcional, mejora detección)
        3. Alinear imagen usando marcadores de esquina
        4. Convertir a blanco y negro
        5. Detectar respuestas marcadas
        
        Args:
            ruta_imagen: Ruta al archivo de imagen de la hoja de examen
            num_preguntas: Número de preguntas
            opciones_por_pregunta: Número de opciones por pregunta
            tamano_plantilla: Tamaño de plantilla
            margen: Margen de plantilla
            tamano_cuadrado_alineacion: Tamaño de cuadrado de alineación
            umbral_marca: Umbral para detectar celdas marcadas
            quitar_sombras: Si es True, elimina sombras antes de procesar (recomendado)
            
        Returns:
            Diccionario conteniendo:
                - 'exito': bool indicando si el procesamiento fue exitoso
                - 'respuestas': Lista de respuestas detectadas (si es exitoso)
                - 'error': Mensaje de error (si falló)
                - 'imagen_alineada': Imagen alineada (si es exitoso)
                - 'imagen_sin_sombras': Imagen con sombras eliminadas (si quitar_sombras=True)
        """
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
        
        # Quitar sombras si se solicita (mejora la detección de marcadores y marcas)
        imagen_procesada = imagen
        imagen_sin_sombras = None
        if quitar_sombras:
            # Convertir a escala de grises y quitar sombras
            grises_sin_sombras = self.quitar_sombras(imagen)
            # Convertir de vuelta a BGR para alineación
            imagen_sin_sombras = cv2.cvtColor(grises_sin_sombras, cv2.COLOR_GRAY2BGR)
            imagen_procesada = imagen_sin_sombras
        
        # Alinear imagen
        alineada = self.alinear_imagen_examen(
            imagen_procesada, tamano_plantilla, margen, tamano_cuadrado_alineacion
        )
        if alineada is None:
            return {
                'exito': False,
                'error': 'Falló al alinear imagen (no se pudieron encontrar 4 marcadores de alineación)',
                'respuestas': None,
                'imagen_alineada': None,
                'imagen_sin_sombras': imagen_sin_sombras
            }
        
        # Detectar respuestas (la conversión a blanco y negro se hace dentro)
        respuestas = self.detectar_respuestas_marcadas(
            alineada, num_preguntas, opciones_por_pregunta,
            tamano_plantilla, margen, tamano_cuadrado_alineacion, umbral_marca
        )
        
        return {
            'exito': True,
            'respuestas': respuestas,
            'error': None,
            'imagen_alineada': alineada,
            'imagen_sin_sombras': imagen_sin_sombras
        }
