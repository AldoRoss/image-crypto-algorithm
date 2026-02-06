"""
Paquete de cifrado de imagenes por adveccion caotica (Double Gyre).

Uso basico:
    from crypto import scramble, descramble

    key = {"A": 0.25, "epsilon": 0.25, "omega": 6.283, "dt": 0.1, "N": 20}
    encrypted = scramble(image, key)
    recovered = descramble(encrypted, key)
"""

from .scramble import descramble, scramble

__all__ = ["scramble", "descramble"]
