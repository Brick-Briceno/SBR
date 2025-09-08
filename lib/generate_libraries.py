import os
import re

notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def renombrar_archivos():
    # Ruta a la carpeta actual
    ruta_actual = os.path.dirname(__file__)

    # Lista todas las carpetas en la carpeta actual
    carpetas = [nombre for nombre in os.listdir(ruta_actual) if os.path.isdir(os.path.join(ruta_actual, nombre))]

    for carpeta in carpetas:
        i = 0
        for octava in range(0, 9):
            for nota in notas:
                # Busca archivos que coincidan con el patrón
                for archivo in os.listdir(os.path.join(ruta_actual, carpeta)):
                    if re.search(f'{nota}{octava}', archivo, re.IGNORECASE):
                        # Renombra el archivo
                        os.rename(os.path.join(ruta_actual, carpeta, archivo), os.path.join(ruta_actual, carpeta, f'{i:02}.wav'))
                        i += 1
                        break

renombrar_archivos()
