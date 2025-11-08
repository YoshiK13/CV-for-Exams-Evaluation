"""Ejemplo: Flujo de trabajo completo en español

Este ejemplo demuestra:
1. Generar una plantilla de examen
2. Simular un examen rellenado (marcando respuestas)
3. Procesar el examen para detectar respuestas marcadas
4. Validar respuestas (detectando marcas inválidas/múltiples)

Ejecutar desde la raíz del repositorio:
    python3 examples/demo_flujo_completo_espanol.py
"""
import os
import sys
import cv2

# Asegurar que src sea importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from exam_evaluator import ReconocedorRespuestas, GeneradorPlantillas

DIR_SALIDA = os.path.dirname(__file__)


def main():
    reconocedor = ReconocedorRespuestas()
    generador = GeneradorPlantillas()
    
    print("=" * 60)
    print("PASO 1: Generar plantilla de examen")
    print("=" * 60)
    
    # Generar plantilla
    num_preguntas = 10
    opciones_por_pregunta = 4
    
    plantilla = generador.generar_plantilla_hoja_examen(
        titulo="Examen de Muestra",
        num_preguntas=num_preguntas,
        opciones_por_pregunta=opciones_por_pregunta,
        tamano_hoja=(800, 1000),
        margen=40,
        tamano_cuadrado_alineacion=40
    )
    
    ruta_plantilla = os.path.join(DIR_SALIDA, 'plantilla_espanol.png')
    cv2.imwrite(ruta_plantilla, plantilla)
    print(f"✓ Plantilla generada: {ruta_plantilla}")
    print(f"  Preguntas: {num_preguntas}, Opciones: {opciones_por_pregunta}")
    
    print("\n" + "=" * 60)
    print("PASO 2: Simular examen rellenado (marcando algunas respuestas)")
    print("=" * 60)
    
    # Simular un estudiante rellenando el examen
    # Marcar respuestas: Q1=A, Q2=C, Q3=B, Q4=D, Q5=A, Q6=B, Q7=C, Q8=A, Q9=D, Q10=B
    examen_rellenado = plantilla.copy()
    
    # Obtener coordenadas de celdas
    celdas = reconocedor.extraer_celdas_respuestas(
        examen_rellenado, num_preguntas, opciones_por_pregunta,
        tamano_plantilla=(800, 1000), margen=40, tamano_cuadrado_alineacion=40
    )
    
    # Simular marcado (rellenar algunas celdas)
    respuestas_marcadas = [0, 2, 1, 3, 0, 1, 2, 0, 3, 1]  # A, C, B, D, A, B, C, A, D, B
    
    for idx_p, idx_resp in enumerate(respuestas_marcadas):
        if idx_p < len(celdas) and idx_resp < len(celdas[idx_p]):
            x, y, w, h = celdas[idx_p][idx_resp]
            # Dibujar un círculo relleno para simular marca de estudiante
            centro_x = x + w // 2
            centro_y = y + h // 2
            radio = min(w, h) // 2 - 2
            cv2.circle(examen_rellenado, (centro_x, centro_y), radio, (0, 0, 0), -1)
    
    ruta_rellenado = os.path.join(DIR_SALIDA, 'examen_rellenado_espanol.png')
    cv2.imwrite(ruta_rellenado, examen_rellenado)
    print(f"✓ Examen rellenado creado: {ruta_rellenado}")
    print(f"  Respuestas marcadas: {['ABCD'[i] for i in respuestas_marcadas]}")
    
    print("\n" + "=" * 60)
    print("PASO 3: Procesar hoja de examen (detectar respuestas)")
    print("=" * 60)
    
    # Procesar el examen rellenado (con eliminación de sombras activada)
    resultado = reconocedor.procesar_hoja_examen(
        ruta_rellenado,
        num_preguntas=num_preguntas,
        opciones_por_pregunta=opciones_por_pregunta,
        tamano_plantilla=(800, 1000),
        margen=40,
        tamano_cuadrado_alineacion=40,
        umbral_marca=0.15,
        quitar_sombras=True  # ← Mejora la detección en imágenes con iluminación irregular
    )
    
    if resultado['exito']:
        print(f"✓ ¡Procesamiento exitoso!")
        print(f"\nRespuestas detectadas:")
        detectadas = resultado['respuestas']
        for i, respuesta in enumerate(detectadas):
            num_pregunta = i + 1
            if respuesta is not None:
                letra_respuesta = 'ABCD'[respuesta]
                letra_esperada = 'ABCD'[respuestas_marcadas[i]]
                coincide = "✓" if respuesta == respuestas_marcadas[i] else "✗"
                print(f"  P{num_pregunta}: {letra_respuesta} (esperada: {letra_esperada}) {coincide}")
            else:
                print(f"  P{num_pregunta}: INVÁLIDA (sin respuesta o múltiples respuestas marcadas)")
        
        # Guardar imagen sin sombras (si está disponible)
        if resultado['imagen_sin_sombras'] is not None:
            ruta_sin_sombras = os.path.join(DIR_SALIDA, 'examen_sin_sombras_espanol.png')
            cv2.imwrite(ruta_sin_sombras, resultado['imagen_sin_sombras'])
            print(f"\n✓ Imagen sin sombras guardada: {ruta_sin_sombras}")
        
        # Guardar imagen alineada
        ruta_alineada = os.path.join(DIR_SALIDA, 'examen_alineado_espanol.png')
        cv2.imwrite(ruta_alineada, resultado['imagen_alineada'])
        print(f"✓ Imagen alineada guardada: {ruta_alineada}")
        
        # También guardar versión binaria para inspección
        binaria = reconocedor.convertir_a_blanco_y_negro(resultado['imagen_alineada'])
        ruta_binaria = os.path.join(DIR_SALIDA, 'examen_binario_espanol.png')
        cv2.imwrite(ruta_binaria, binaria)
        print(f"✓ Imagen binaria guardada: {ruta_binaria}")
        
    else:
        print(f"✗ Procesamiento falló: {resultado['error']}")
    
    print("\n" + "=" * 60)
    print("FLUJO DE TRABAJO COMPLETO")
    print("=" * 60)


if __name__ == '__main__':
    main()
