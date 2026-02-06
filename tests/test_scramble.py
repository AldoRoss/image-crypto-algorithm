"""
Tests para el sistema de cifrado de imagenes por adveccion caotica.

Ejecutar con:
    pytest tests/test_scramble.py -v
"""

import numpy as np
import pytest

from crypto import scramble, descramble


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_image():
    """Imagen sintetica de 64x64 con patron de colores reconocible."""
    h, w = 64, 64
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :, 0] = np.tile(np.linspace(0, 255, w, dtype=np.uint8), (h, 1))
    img[:, :, 1] = np.tile(
        np.linspace(0, 255, h, dtype=np.uint8).reshape(-1, 1), (1, w)
    )
    img[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4, 2] = 200
    return img


@pytest.fixture
def default_key():
    """Llave con los parametros sugeridos en el README."""
    return {
        "A": 0.25,
        "epsilon": 0.25,
        "omega": 2.0 * np.pi,
        "dt": 0.1,
        "N": 20,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_reversibility(sample_image, default_key):
    """Verificar que descramble(scramble(img)) == img.

    Este es el requisito fundamental: el cifrado debe ser perfectamente
    reversible cuando se usa la misma llave.
    """
    encrypted = scramble(sample_image, default_key)
    recovered = descramble(encrypted, default_key)

    assert np.array_equal(sample_image, recovered), (
        "La imagen recuperada no es identica a la original."
    )


def test_determinism(sample_image, default_key):
    """Verificar que dos ejecuciones con la misma llave dan el mismo resultado.

    El cifrado es determinista: no depende de estado aleatorio.
    """
    encrypted_1 = scramble(sample_image, default_key)
    encrypted_2 = scramble(sample_image, default_key)

    assert np.array_equal(encrypted_1, encrypted_2), (
        "Dos ejecuciones con la misma llave produjeron resultados diferentes."
    )


def test_scramble_changes_image(sample_image, default_key):
    """Verificar que la imagen cifrada es diferente a la original.

    Si el scrambling no cambia nada, el cifrado no esta funcionando.
    """
    encrypted = scramble(sample_image, default_key)

    assert not np.array_equal(sample_image, encrypted), (
        "La imagen cifrada es identica a la original. El scrambling no funciona."
    )


def test_sensitivity(sample_image, default_key):
    """Verificar que una llave ligeramente diferente no recupera la imagen.

    Cambiar epsilon por 0.001 debe producir una imagen completamente
    diferente al intentar descifrar.
    """
    encrypted = scramble(sample_image, default_key)

    wrong_key = default_key.copy()
    wrong_key["epsilon"] += 0.001

    recovered_wrong = descramble(encrypted, wrong_key)

    assert not np.array_equal(sample_image, recovered_wrong), (
        "Una llave incorrecta recupero la imagen original. "
        "El cifrado no es sensible a los parametros."
    )


def test_grayscale_image(default_key):
    """Verificar que el cifrado funciona con imagenes en escala de grises."""
    gray_img = np.random.randint(0, 256, size=(32, 32), dtype=np.uint8)

    encrypted = scramble(gray_img, default_key)
    recovered = descramble(encrypted, default_key)

    assert np.array_equal(gray_img, recovered), (
        "Fallo la reversibilidad en una imagen en escala de grises."
    )


def test_output_shape_matches_input(sample_image, default_key):
    """Verificar que la imagen cifrada conserva la forma de la original."""
    encrypted = scramble(sample_image, default_key)

    assert encrypted.shape == sample_image.shape, (
        f"La forma cambio: {sample_image.shape} -> {encrypted.shape}"
    )
