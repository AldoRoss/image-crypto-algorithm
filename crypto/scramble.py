"""
API publica para cifrado y descifrado de imagenes por adveccion caotica.

Este modulo orquesta los tres pasos del proceso:
1. Mapear pixeles al dominio continuo del Double Gyre.
2. Advectar las particulas para generar una permutacion caotica.
3. Aplicar (o invertir) la permutacion sobre los pixeles de la imagen.
"""

import numpy as np

from .advection import advect_particles, map_pixels_to_domain
from .permutation import build_permutation, invert_permutation


def _generate_permutation(height: int, width: int, key: dict) -> np.ndarray:
    """Genera la permutacion caotica para una imagen de tamanio dado.

    Proceso interno:
        1. Coloca cada pixel como particula en el dominio [0,2] x [0,1].
        2. Mueve todas las particulas con el campo de velocidad Double Gyre.
        3. Convierte las posiciones finales en una permutacion biyectiva.

    Parametros:
        height: Alto de la imagen en pixeles.
        width: Ancho de la imagen en pixeles.
        key: Diccionario con los parametros de la llave.

    Retorna:
        perm: Permutacion directa (array 1D de enteros).
    """
    x, y = map_pixels_to_domain(height, width)
    x_final, y_final = advect_particles(x, y, key)
    perm = build_permutation(x_final, y_final)
    return perm


def scramble(image: np.ndarray, key: dict) -> np.ndarray:
    """Cifra una imagen reordenando sus pixeles con adveccion caotica.

    Cada pixel de la imagen se trata como una particula en el flujo
    Double Gyre. Despues de N pasos de adveccion, las posiciones
    finales definen una permutacion que reordena los pixeles,
    produciendo una imagen visualmente irreconocible.

    Parametros:
        image: Imagen original como np.ndarray.
               Acepta forma (H, W, C) para color o (H, W) para escala de grises.
        key: Diccionario con los parametros de la llave:
             - A (float): Intensidad del flujo.
             - epsilon (float): Amplitud de la oscilacion temporal.
             - omega (float): Frecuencia de la oscilacion temporal.
             - dt (float): Paso de integracion.
             - N (int): Numero de pasos de adveccion.

    Retorna:
        Imagen cifrada con la misma forma y tipo que la original.
    """
    height, width = image.shape[:2]
    perm = _generate_permutation(height, width, key)

    # Aplanar pixeles, aplicar permutacion, reconstruir forma original
    flat = image.reshape(-1, *image.shape[2:]) if image.ndim > 2 else image.ravel()
    scrambled_flat = flat[perm]

    return scrambled_flat.reshape(image.shape)


def descramble(image: np.ndarray, key: dict) -> np.ndarray:
    """Descifra una imagen aplicando la permutacion inversa.

    Reconstruye la misma permutacion caotica a partir de la llave,
    calcula su inversa, y reordena los pixeles de vuelta a su
    posicion original.

    Parametros:
        image: Imagen cifrada como np.ndarray.
        key: Diccionario con los mismos parametros usados para cifrar.

    Retorna:
        Imagen recuperada con la misma forma y tipo que la entrada.
        Si la llave es correcta, sera identica a la imagen original.
    """
    height, width = image.shape[:2]
    perm = _generate_permutation(height, width, key)
    inv_perm = invert_permutation(perm)

    flat = image.reshape(-1, *image.shape[2:]) if image.ndim > 2 else image.ravel()
    recovered_flat = flat[inv_perm]

    return recovered_flat.reshape(image.shape)
