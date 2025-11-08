"""
Módulo Evaluador de Exámenes
Funcionalidad central para evaluación automatizada de exámenes usando OpenCV.
"""

# Importar clase original en inglés (para compatibilidad hacia atrás)
from .pattern_recognition import PatternRecognizer

# Importar nuevas clases en español
from .reconocimiento_respuestas import ReconocedorRespuestas
from .generador_plantillas import GeneradorPlantillas

__all__ = [
    'PatternRecognizer',  # Mantener compatibilidad
    'ReconocedorRespuestas',  # Nueva clase en español
    'GeneradorPlantillas',  # Nueva clase en español
]
