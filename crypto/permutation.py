"""
Generacion de permutaciones biyectivas a partir de posiciones de particulas.

Despues de la adveccion, cada particula tiene una posicion final (x_f, y_f).
Este modulo convierte esas posiciones en una permutacion discreta:
una funcion que asigna a cada pixel un nuevo indice, sin repeticiones.

Estrategia:
    Se usa el ranking de las posiciones finales (ordenadas lexicograficamente
    por y, luego por x) como la permutacion. Como cada particula tiene una
    posicion unica en punto flotante, el ranking es naturalmente biyectivo.
"""

import numpy as np


def build_permutation(
    x_final: np.ndarray,
    y_final: np.ndarray,
) -> np.ndarray:
    """Convierte posiciones finales de particulas en una permutacion biyectiva.

    Ordena las particulas lexicograficamente por (y_final, x_final) y
    asigna a cada particula el rango que le corresponde en ese orden.
    El resultado es un array donde perm[i] indica a que posicion se
    mueve el pixel i.

    Parametros:
        x_final: Coordenadas x finales de las particulas (array 1D).
        y_final: Coordenadas y finales de las particulas (array 1D).

    Retorna:
        perm: Array 1D de enteros. perm[i] = j significa que el pixel
              en la posicion i se mueve a la posicion j.
    """
    n = len(x_final)

    # lexsort ordena primero por x_final (secundario), luego por y_final (primario)
    # El resultado son los indices que ordenarian las particulas
    sorted_indices = np.lexsort((x_final, y_final))

    # Crear la permutacion: el pixel en sorted_indices[k] va a la posicion k
    perm = np.empty(n, dtype=np.int64)
    perm[sorted_indices] = np.arange(n)

    return perm


def invert_permutation(perm: np.ndarray) -> np.ndarray:
    """Calcula la permutacion inversa.

    Si perm[i] = j, entonces inv_perm[j] = i.
    Se usa para revertir el scrambling y recuperar la imagen original.

    Parametros:
        perm: Array 1D con la permutacion directa.

    Retorna:
        inv_perm: Array 1D con la permutacion inversa.
    """
    inv_perm = np.empty_like(perm)
    inv_perm[perm] = np.arange(len(perm))
    return inv_perm
