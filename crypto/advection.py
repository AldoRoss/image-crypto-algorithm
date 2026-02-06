"""
Adveccion de particulas mediante integracion Euler explicito.

Este modulo se encarga de:
1. Mapear pixeles de la imagen al dominio continuo del Double Gyre.
2. Mover las particulas paso a paso usando el campo de velocidad.
3. Aplicar condiciones de frontera para mantenerlas en el dominio.
"""

import numpy as np

from .double_gyre import velocity_field


def map_pixels_to_domain(height: int, width: int) -> tuple[np.ndarray, np.ndarray]:
    """Convierte coordenadas de pixeles (i, j) al dominio continuo [0, 2] x [0, 1].

    Cada pixel se coloca en el centro de su celda correspondiente dentro
    del dominio del Double Gyre.

    Parametros:
        height: Numero de filas de la imagen.
        width: Numero de columnas de la imagen.

    Retorna:
        (x, y): Arrays 1D de longitud height*width con las posiciones
                en el dominio continuo. x va de 0 a 2, y va de 0 a 1.
    """
    # Crear grilla uniforme centrada en cada celda
    cols = np.linspace(0, 2, width, endpoint=False) + (1.0 / width)
    rows = np.linspace(0, 1, height, endpoint=False) + (0.5 / height)

    # Expandir a grilla 2D y aplanar
    grid_x, grid_y = np.meshgrid(cols, rows)
    return grid_x.ravel(), grid_y.ravel()


def apply_boundary_conditions(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mantiene las particulas dentro del dominio [0, 2] x [0, 1].

    Usa condiciones reflectivas: cuando una particula cruza un borde,
    rebota de vuelta al dominio. Esto preserva la estructura de la
    permutacion y evita perder particulas.

    Parametros:
        x: Coordenadas x de las particulas.
        y: Coordenadas y de las particulas.

    Retorna:
        (x, y): Coordenadas corregidas dentro del dominio.
    """
    # Reflexion en x: dominio [0, 2]
    # Plegar al periodo [0, 4], luego reflejar la mitad superior
    x = np.mod(x, 4.0)
    x = np.where(x > 2.0, 4.0 - x, x)

    # Reflexion en y: dominio [0, 1]
    # Plegar al periodo [0, 2], luego reflejar la mitad superior
    y = np.mod(y, 2.0)
    y = np.where(y > 1.0, 2.0 - y, y)

    return x, y


def advect_particles(
    x: np.ndarray,
    y: np.ndarray,
    key: dict,
) -> tuple[np.ndarray, np.ndarray]:
    """Mueve particulas por N pasos usando integracion Euler explicito.

    En cada paso temporal:
        x_{k+1} = x_k + dt * u(x_k, y_k, t_k)
        y_{k+1} = y_k + dt * v(x_k, y_k, t_k)

    donde t_k = k * dt.

    Parametros:
        x: Posiciones iniciales x de las particulas (array 1D).
        y: Posiciones iniciales y de las particulas (array 1D).
        key: Diccionario con los parametros del flujo:
             - A: Intensidad del flujo.
             - epsilon: Amplitud de la oscilacion temporal.
             - omega: Frecuencia de la oscilacion temporal.
             - dt: Paso de integracion.
             - N: Numero de pasos de adveccion.

    Retorna:
        (x_final, y_final): Posiciones finales de las particulas.
    """
    A = key["A"]
    epsilon = key["epsilon"]
    omega = key["omega"]
    dt = key["dt"]
    N = key["N"]

    x = x.copy()
    y = y.copy()

    for k in range(N):
        t = k * dt

        u, v = velocity_field(x, y, t, A, epsilon, omega)

        x = x + dt * u
        y = y + dt * v

        x, y = apply_boundary_conditions(x, y)

    return x, y
