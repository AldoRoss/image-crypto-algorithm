"""
Campo de velocidad del flujo Double Gyre.

El Double Gyre es un flujo 2D clasico en dinamica de fluidos que presenta
mezcla caotica Lagrangiana. Vive en el dominio [0, 2] x [0, 1].

Ecuaciones:
    u(x, y, t) = -pi * A * sin(pi * f(x,t)) * cos(pi * y)
    v(x, y, t) =  pi * A * cos(pi * f(x,t)) * sin(pi * y) * (df/dx)

donde:
    f(x, t)  = a(t) * x^2 + b(t) * x
    a(t)     = epsilon * sin(omega * t)
    b(t)     = 1 - 2 * epsilon * sin(omega * t)
    df/dx    = 2 * a(t) * x + b(t)
"""

import numpy as np


def _a(t: float, epsilon: float, omega: float) -> float:
    """Coeficiente cuadratico de la oscilacion temporal.

    Controla la amplitud de la deformacion del giro.
    """
    return epsilon * np.sin(omega * t)


def _b(t: float, epsilon: float, omega: float) -> float:
    """Coeficiente lineal de la oscilacion temporal.

    Complementa a _a(t) para mantener la estructura del flujo.
    """
    return 1.0 - 2.0 * epsilon * np.sin(omega * t)


def _f(x: np.ndarray, t: float, epsilon: float, omega: float) -> np.ndarray:
    """Funcion de deformacion espacial dependiente del tiempo.

    Define como se distorsiona el eje x del flujo en cada instante.
    """
    a = _a(t, epsilon, omega)
    b = _b(t, epsilon, omega)
    return a * x**2 + b * x


def _dfdx(x: np.ndarray, t: float, epsilon: float, omega: float) -> np.ndarray:
    """Derivada parcial de f respecto a x.

    Necesaria para calcular la componente vertical del campo de velocidad.
    """
    a = _a(t, epsilon, omega)
    b = _b(t, epsilon, omega)
    return 2.0 * a * x + b


def velocity_field(
    x: np.ndarray,
    y: np.ndarray,
    t: float,
    A: float,
    epsilon: float,
    omega: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Calcula las componentes (u, v) del campo de velocidad Double Gyre.

    Parametros:
        x: Coordenadas x de las particulas (array 1D).
        y: Coordenadas y de las particulas (array 1D).
        t: Tiempo actual.
        A: Intensidad del flujo.
        epsilon: Amplitud de la oscilacion temporal.
        omega: Frecuencia de la oscilacion temporal.

    Retorna:
        (u, v): Tupla con las componentes horizontal y vertical
                de la velocidad en cada punto.
    """
    f = _f(x, t, epsilon, omega)
    dfdx = _dfdx(x, t, epsilon, omega)

    u = -np.pi * A * np.sin(np.pi * f) * np.cos(np.pi * y)
    v = np.pi * A * np.cos(np.pi * f) * np.sin(np.pi * y) * dfdx

    return u, v
