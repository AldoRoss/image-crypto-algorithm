"""
Demo de referencia: Cifrado de imagenes por adveccion caotica.

Este archivo muestra la ESTRUCTURA ESPERADA de la demo final.
Adapten los imports y llamadas a su propia implementacion.

Uso esperado:
    python demo/demo.py [ruta_imagen]
"""

import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt


# =====================================================================
# 1. Cargar imagen
# =====================================================================

if len(sys.argv) > 1:
    img = np.array(Image.open(sys.argv[1]))
    print(f"Imagen cargada: {sys.argv[1]} | Shape: {img.shape}")
else:
    # Generar imagen de prueba si no se proporciona una
    h, w = 256, 256
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :, 0] = np.tile(np.linspace(0, 255, w, dtype=np.uint8), (h, 1))
    img[:, :, 1] = np.tile(np.linspace(0, 255, h, dtype=np.uint8).reshape(-1, 1), (1, w))
    img[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4, 2] = 200
    print(f"Imagen de prueba generada | Shape: {img.shape}")


# =====================================================================
# 2. Definir llave
# =====================================================================

key = {
    "A": 0.25,
    "epsilon": 0.25,
    "omega": 2.0 * np.pi,
    "dt": 0.1,
    "N": 20,
}


# =====================================================================
# 3. Scramble + Descramble
#
#    Aqui van a llamar a sus propias funciones.
#    Ejemplo de lo que esperamos ver:
#
#    encrypted = scramble(img, key)
#    recovered = descramble(encrypted, key)
#    assert np.array_equal(img, recovered), "Fallo la reversibilidad"
#
# =====================================================================


# =====================================================================
# 4. Sensibilidad a la llave
#
#    wrong_key = key.copy()
#    wrong_key["epsilon"] += 0.001
#    recovered_wrong = descramble(encrypted, wrong_key)
#
# =====================================================================


# =====================================================================
# 5. Visualizacion
#
#    Esperamos ver al menos:
#    - Imagen original
#    - Imagen scrambled
#    - Imagen recuperada
#    - Imagen recuperada con llave incorrecta
#    - Histogramas (original vs scrambled)
#
#    Ejemplo con matplotlib:
#
#    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
#    axes[0].imshow(img)
#    axes[0].set_title("Original")
#    axes[1].imshow(encrypted)
#    axes[1].set_title("Scrambled")
#    axes[2].imshow(recovered)
#    axes[2].set_title("Recovered")
#    plt.tight_layout()
#    plt.show()
#
# =====================================================================
