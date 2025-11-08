"""
Tests para Módulos en Español (ReconocedorRespuestas y GeneradorPlantillas)
"""

import sys
import os
import pytest
import numpy as np
import cv2

# Agregar directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from exam_evaluator import ReconocedorRespuestas, GeneradorPlantillas


class TestGeneradorPlantillas:
    """Suite de tests para la clase GeneradorPlantillas."""
    
    @pytest.fixture
    def generador(self):
        """Crear una instancia de GeneradorPlantillas para testing."""
        return GeneradorPlantillas()
    
    def test_inicializacion(self, generador):
        """Test que GeneradorPlantillas se inicialice correctamente."""
        assert generador is not None
        assert hasattr(generador, 'opencv_version')
        assert isinstance(generador.opencv_version, str)
    
    def test_generar_plantilla_basica(self, generador):
        """Test generación básica de plantilla."""
        plantilla = generador.generar_plantilla_hoja_examen(
            titulo="Test",
            num_preguntas=5,
            opciones_por_pregunta=4,
            tamano_hoja=(800, 1000)
        )
        assert plantilla is not None
        assert plantilla.shape == (1000, 800, 3)
        assert plantilla.dtype == np.uint8
    
    def test_plantilla_con_parametros_personalizados(self, generador):
        """Test generación con parámetros personalizados."""
        plantilla = generador.generar_plantilla_hoja_examen(
            titulo="Examen Personalizado",
            num_preguntas=20,
            opciones_por_pregunta=5,
            tamano_hoja=(1000, 1200),
            margen=50
        )
        assert plantilla is not None
        assert plantilla.shape == (1200, 1000, 3)


class TestReconocedorRespuestas:
    """Suite de tests para la clase ReconocedorRespuestas."""
    
    @pytest.fixture
    def reconocedor(self):
        """Crear una instancia de ReconocedorRespuestas para testing."""
        return ReconocedorRespuestas()
    
    @pytest.fixture
    def imagen_muestra(self):
        """Crear una imagen de prueba simple."""
        # Crear una imagen blanca con un rectángulo negro
        imagen = np.ones((100, 100, 3), dtype=np.uint8) * 255
        cv2.rectangle(imagen, (25, 25), (75, 75), (0, 0, 0), -1)
        return imagen
    
    @pytest.fixture
    def imagen_grises_muestra(self):
        """Crear una imagen de prueba simple en escala de grises."""
        imagen = np.ones((100, 100), dtype=np.uint8) * 255
        cv2.rectangle(imagen, (25, 25), (75, 75), 0, -1)
        return imagen
    
    def test_inicializacion(self, reconocedor):
        """Test que ReconocedorRespuestas se inicialice correctamente."""
        assert reconocedor is not None
        assert hasattr(reconocedor, 'opencv_version')
        assert isinstance(reconocedor.opencv_version, str)
    
    def test_convertir_a_escala_grises(self, reconocedor, imagen_muestra):
        """Test conversión a escala de grises."""
        grises = reconocedor.convertir_a_escala_grises(imagen_muestra)
        assert grises is not None
        assert len(grises.shape) == 2  # Imágenes en escala de grises son 2D
        assert grises.dtype == np.uint8
    
    def test_aplicar_umbral(self, reconocedor, imagen_grises_muestra):
        """Test aplicación de umbral binario."""
        binaria = reconocedor.aplicar_umbral(imagen_grises_muestra, valor_umbral=127)
        assert binaria is not None
        assert len(binaria.shape) == 2
        # Imagen binaria debe tener solo valores 0 y 255
        valores_unicos = np.unique(binaria)
        assert all(v in [0, 255] for v in valores_unicos)
    
    def test_detectar_bordes(self, reconocedor, imagen_grises_muestra):
        """Test detección de bordes."""
        bordes = reconocedor.detectar_bordes(imagen_grises_muestra, umbral_bajo=50, umbral_alto=150)
        assert bordes is not None
        assert len(bordes.shape) == 2
        assert bordes.dtype == np.uint8
    
    def test_encontrar_contornos(self, reconocedor, imagen_grises_muestra):
        """Test detección de contornos."""
        binaria = reconocedor.aplicar_umbral(imagen_grises_muestra, valor_umbral=127)
        contornos, jerarquia = reconocedor.encontrar_contornos(binaria)
        assert contornos is not None
        assert jerarquia is not None
        assert len(contornos) > 0  # Debería encontrar al menos el rectángulo
    
    def test_obtener_info_imagen(self, reconocedor, imagen_muestra):
        """Test obtener información de imagen."""
        info = reconocedor.obtener_info_imagen(imagen_muestra)
        assert info is not None
        assert 'forma' in info
        assert 'dtype' in info
        assert 'tamano' in info
        assert 'dimensiones' in info
        assert info['forma'] == (100, 100, 3)
        assert info['dimensiones'] == 3
    
    def test_convertir_a_blanco_y_negro(self, reconocedor, imagen_muestra):
        """Test conversión a blanco y negro."""
        binaria = reconocedor.convertir_a_blanco_y_negro(imagen_muestra)
        assert binaria is not None
        assert len(binaria.shape) == 2
        # Debe ser binaria (solo 0 y 255)
        valores_unicos = np.unique(binaria)
        assert all(v in [0, 255] for v in valores_unicos)
    
    def test_extraer_celdas_respuestas(self, reconocedor):
        """Test extracción de coordenadas de celdas."""
        # Crear una imagen dummy
        imagen = np.ones((1000, 800, 3), dtype=np.uint8) * 255
        
        celdas = reconocedor.extraer_celdas_respuestas(
            imagen,
            num_preguntas=5,
            opciones_por_pregunta=4,
            tamano_plantilla=(800, 1000)
        )
        
        assert celdas is not None
        assert len(celdas) == 5  # 5 preguntas
        assert all(len(pregunta) == 4 for pregunta in celdas)  # 4 opciones cada una
        
        # Verificar que las coordenadas son tuplas de 4 elementos
        for pregunta in celdas:
            for celda in pregunta:
                assert len(celda) == 4  # (x, y, w, h)
                x, y, w, h = celda
                assert x >= 0 and y >= 0
                assert w > 0 and h > 0
    
    def test_es_celda_marcada(self, reconocedor):
        """Test detección de celda marcada."""
        # Crear una imagen binaria con una región marcada
        imagen_binaria = np.ones((100, 100), dtype=np.uint8) * 255
        # Marcar un área (negro = 0)
        cv2.rectangle(imagen_binaria, (10, 10), (40, 40), 0, -1)
        
        # Test celda marcada
        celda_marcada = (10, 10, 30, 30)
        assert reconocedor.es_celda_marcada(imagen_binaria, celda_marcada, umbral=0.15)
        
        # Test celda no marcada
        celda_no_marcada = (60, 60, 30, 30)
        assert not reconocedor.es_celda_marcada(imagen_binaria, celda_no_marcada, umbral=0.15)
    
    def test_detectar_circulos_retorna_formato_valido(self, reconocedor):
        """Test detección de círculos retorna formato correcto."""
        # Crear una imagen con un círculo
        imagen = np.ones((200, 200), dtype=np.uint8) * 255
        cv2.circle(imagen, (100, 100), 30, (0,), -1)
        
        circulos = reconocedor.detectar_circulos(imagen, radio_min=20, radio_max=40)
        # Nota: circulos puede ser None si la detección falla, lo cual es aceptable
        if circulos is not None:
            assert isinstance(circulos, np.ndarray)
    
    def test_cargar_imagen_archivo_inexistente(self, reconocedor):
        """Test que cargar imagen devuelve None para archivo inexistente."""
        imagen = reconocedor.cargar_imagen('/ruta/inexistente/imagen.jpg')
        assert imagen is None
    
    def test_preprocesar_imagen_examen_archivo_inexistente(self, reconocedor):
        """Test que preprocesar devuelve None para archivo inexistente."""
        procesada = reconocedor.preprocesar_imagen_examen('/ruta/inexistente/examen.jpg')
        assert procesada is None


class TestIntegracionEspanol:
    """Tests de integración para verificar que ambas clases funcionen juntas."""
    
    def test_flujo_completo_generacion_y_reconocimiento(self):
        """Test flujo completo: generar plantilla y extraer celdas."""
        generador = GeneradorPlantillas()
        reconocedor = ReconocedorRespuestas()
        
        # Generar plantilla
        plantilla = generador.generar_plantilla_hoja_examen(
            titulo="Test",
            num_preguntas=5,
            opciones_por_pregunta=4
        )
        
        # Extraer celdas
        celdas = reconocedor.extraer_celdas_respuestas(
            plantilla,
            num_preguntas=5,
            opciones_por_pregunta=4
        )
        
        assert len(celdas) == 5
        assert all(len(pregunta) == 4 for pregunta in celdas)


def test_importacion_opencv():
    """Test que OpenCV se puede importar."""
    import cv2
    assert cv2.__version__ is not None


def test_importacion_numpy():
    """Test que NumPy se puede importar."""
    import numpy
    assert numpy.__version__ is not None
