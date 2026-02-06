"""
Demo: Cifrado de imagenes por adveccion caotica (Double Gyre).

Muestra el proceso completo:
1. Cargar o generar una imagen.
2. Cifrarla con una llave (scramble).
3. Recuperarla con la misma llave (descramble).
4. Intentar recuperar con una llave incorrecta.
5. Comparar histogramas antes y despues del cifrado.

Uso:
    python demo/demo.py       # Usa todas las imagenes de la carpeta images/
"""

import os
import sys

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Agregar el directorio raiz del proyecto al path para importar crypto
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)

from crypto import scramble, descramble

IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================================
# 1. Buscar imagenes en la carpeta images/
# =====================================================================

EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
image_paths = sorted(
    os.path.join(IMAGES_DIR, f)
    for f in os.listdir(IMAGES_DIR)
    if f.lower().endswith(EXTENSIONS)
)

if not image_paths:
    print("No se encontraron imagenes en images/. Abortando.")
    sys.exit(1)

print(f"Se encontraron {len(image_paths)} imagen(es) en images/\n")


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

print(f"Llave: {key}\n")


# =====================================================================
# 3. Procesar cada imagen
# =====================================================================

for path in image_paths:
    filename = os.path.basename(path)
    name, _ = os.path.splitext(filename)

    print("=" * 65)
    print(f"Imagen: {filename}")
    print("=" * 65)

    # Cargar imagen y redimensionar para que la demo sea rapida
    img = np.array(Image.open(path).convert("RGB"))
    # Redimensionar a maximo 256px en su lado mayor para velocidad
    max_side = max(img.shape[:2])
    if max_side > 256:
        scale = 256 / max_side
        new_h = int(img.shape[0] * scale)
        new_w = int(img.shape[1] * scale)
        img = np.array(Image.fromarray(img).resize((new_w, new_h)))
    print(f"  Shape: {img.shape}")

    # --- Scramble ---
    print("  Cifrando...")
    encrypted = scramble(img, key)

    # --- Descramble con llave correcta ---
    print("  Descifrando con llave correcta...")
    recovered = descramble(encrypted, key)

    assert np.array_equal(img, recovered), f"  ERROR: reversibilidad fallo en {filename}"
    print("  Reversibilidad verificada.")

    # --- Descramble con llave incorrecta ---
    wrong_key = key.copy()
    wrong_key["epsilon"] += 0.001
    recovered_wrong = descramble(encrypted, wrong_key)

    if not np.array_equal(img, recovered_wrong):
        print("  Sensibilidad verificada: llave incorrecta NO recupera la imagen.")
    else:
        print("  ADVERTENCIA: la llave incorrecta recupero la imagen.")

    # -----------------------------------------------------------------
    # Visualizacion 1: proceso de cifrado (original vs scrambled)
    # -----------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].imshow(img)
    axes[0].set_title("Original")
    axes[0].axis("off")

    axes[1].imshow(encrypted)
    axes[1].set_title("Scrambled")
    axes[1].axis("off")

    plt.suptitle(f"Cifrado Caotico - {filename}", fontsize=14)
    plt.tight_layout()

    out_scramble = os.path.join(OUTPUT_DIR, f"{name}_scramble.png")
    plt.savefig(out_scramble, dpi=150, bbox_inches="tight")
    print(f"  Guardado: {out_scramble}")
    plt.close()

    # -----------------------------------------------------------------
    # Visualizacion 2: comparacion de recuperacion
    #   Original vs Llave correcta vs Llave incorrecta
    #   + diferencia pixel a pixel para evidenciar el resultado
    # -----------------------------------------------------------------
    diff_correct = np.abs(img.astype(np.int16) - recovered.astype(np.int16)).astype(np.uint8)
    diff_wrong = np.abs(img.astype(np.int16) - recovered_wrong.astype(np.int16)).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Fila superior: imagenes
    axes[0, 0].imshow(img)
    axes[0, 0].set_title("Original")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(recovered)
    axes[0, 1].set_title("Llave correcta")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(recovered_wrong)
    axes[0, 2].set_title("Llave incorrecta\n(epsilon + 0.001)")
    axes[0, 2].axis("off")

    # Fila inferior: diferencias pixel a pixel
    axes[1, 0].text(
        0.5, 0.5, "Diferencia\npixel a pixel\n(amplificada x10)",
        ha="center", va="center", fontsize=12, transform=axes[1, 0].transAxes,
    )
    axes[1, 0].axis("off")

    # Diferencia con llave correcta (deberia ser toda negra = 0)
    axes[1, 1].imshow(np.clip(diff_correct * 10, 0, 255))
    match_pct = 100.0 * np.mean(diff_correct == 0)
    axes[1, 1].set_title(f"Diferencia: {match_pct:.1f}% identico")
    axes[1, 1].axis("off")

    # Diferencia con llave incorrecta (deberia verse llena de ruido)
    axes[1, 2].imshow(np.clip(diff_wrong * 10, 0, 255))
    match_pct_wrong = 100.0 * np.mean(diff_wrong == 0)
    axes[1, 2].set_title(f"Diferencia: {match_pct_wrong:.1f}% identico")
    axes[1, 2].axis("off")

    plt.suptitle(f"Comparacion de Recuperacion - {filename}", fontsize=14)
    plt.tight_layout()

    out_comparison = os.path.join(OUTPUT_DIR, f"{name}_comparison.png")
    plt.savefig(out_comparison, dpi=150, bbox_inches="tight")
    print(f"  Guardado: {out_comparison}")
    plt.close()

    # -----------------------------------------------------------------
    # Visualizacion: histogramas
    # -----------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for i, color in enumerate(["red", "green", "blue"]):
        axes[0].hist(img[:, :, i].ravel(), bins=256, range=(0, 256),
                     color=color, alpha=0.5, label=color)
    axes[0].set_title("Histograma - Original")
    axes[0].set_xlabel("Intensidad")
    axes[0].set_ylabel("Frecuencia")
    axes[0].legend()

    for i, color in enumerate(["red", "green", "blue"]):
        axes[1].hist(encrypted[:, :, i].ravel(), bins=256, range=(0, 256),
                     color=color, alpha=0.5, label=color)
    axes[1].set_title("Histograma - Scrambled")
    axes[1].set_xlabel("Intensidad")
    axes[1].set_ylabel("Frecuencia")
    axes[1].legend()

    plt.suptitle(f"Histogramas - {filename}", fontsize=14)
    plt.tight_layout()

    out_histograms = os.path.join(OUTPUT_DIR, f"{name}_histograms.png")
    plt.savefig(out_histograms, dpi=150, bbox_inches="tight")
    print(f"  Guardado: {out_histograms}")
    plt.close()

    print()

print("Demo completada. Resultados en demo/output/")
