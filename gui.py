"""
Interfaz grafica para cifrado y descifrado de imagenes por adveccion caotica.

Dos pestanas:
  - Cifrar (Scramble): seleccionar imagen, ajustar parametros, cifrar y guardar.
  - Descifrar (Descramble): seleccionar imagen cifrada, ajustar parametros, descifrar y guardar.

Cada pestana muestra la comparacion entrada vs salida con sus histogramas.

Uso:
    python gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from PIL import Image
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from crypto import scramble, descramble


# =========================================================================
# Funciones auxiliares
# =========================================================================


def create_parameter_fields(parent):
    """Crea los campos de entrada para los 5 parametros de la llave.

    Retorna un diccionario {nombre: tk.StringVar} con los valores por defecto.
    """
    frame = ttk.LabelFrame(parent, text="Parametros de la llave", padding=10)
    frame.pack(fill="x", padx=10, pady=5)

    defaults = {
        "A": "0.25",
        "epsilon": "0.25",
        "omega": "6.283185307179586",
        "dt": "0.1",
        "N": "20",
    }

    fields = {}
    row = ttk.Frame(frame)
    row.pack(fill="x")

    for i, (name, default) in enumerate(defaults.items()):
        lbl = ttk.Label(row, text=f"{name}:")
        lbl.grid(row=0, column=i * 2, padx=(10, 2), pady=5, sticky="e")

        var = tk.StringVar(value=default)
        entry = ttk.Entry(row, textvariable=var, width=12)
        entry.grid(row=0, column=i * 2 + 1, padx=(0, 10), pady=5, sticky="w")

        fields[name] = var

    return fields


def get_key_from_fields(fields):
    """Lee los valores de los campos y retorna el diccionario de llave.

    Lanza ValueError si algun campo tiene un valor no numerico.
    """
    return {
        "A": float(fields["A"].get()),
        "epsilon": float(fields["epsilon"].get()),
        "omega": float(fields["omega"].get()),
        "dt": float(fields["dt"].get()),
        "N": int(fields["N"].get()),
    }


def draw_comparison(figure, canvas, img_input, img_output, title_in, title_out):
    """Dibuja la comparacion de dos imagenes con sus histogramas en el canvas.

    Layout 2x2:
      [imagen entrada]  [imagen salida]
      [histograma ent]  [histograma sal]
    """
    figure.clear()

    # --- Fila superior: imagenes ---
    ax1 = figure.add_subplot(2, 2, 1)
    ax1.imshow(img_input)
    ax1.set_title(title_in, fontsize=10)
    ax1.axis("off")

    ax2 = figure.add_subplot(2, 2, 2)
    ax2.imshow(img_output)
    ax2.set_title(title_out, fontsize=10)
    ax2.axis("off")

    # --- Fila inferior: histogramas ---
    ax3 = figure.add_subplot(2, 2, 3)
    if img_input.ndim == 3:
        for i, color in enumerate(["red", "green", "blue"]):
            ax3.hist(img_input[:, :, i].ravel(), bins=256, range=(0, 256),
                     color=color, alpha=0.5)
    else:
        ax3.hist(img_input.ravel(), bins=256, range=(0, 256), color="gray")
    ax3.set_title("Histograma entrada", fontsize=9)
    ax3.set_xlabel("Intensidad", fontsize=8)
    ax3.set_ylabel("Frecuencia", fontsize=8)
    ax3.tick_params(labelsize=7)

    ax4 = figure.add_subplot(2, 2, 4)
    if img_output.ndim == 3:
        for i, color in enumerate(["red", "green", "blue"]):
            ax4.hist(img_output[:, :, i].ravel(), bins=256, range=(0, 256),
                     color=color, alpha=0.5)
    else:
        ax4.hist(img_output.ravel(), bins=256, range=(0, 256), color="gray")
    ax4.set_title("Histograma salida", fontsize=9)
    ax4.set_xlabel("Intensidad", fontsize=8)
    ax4.set_ylabel("Frecuencia", fontsize=8)
    ax4.tick_params(labelsize=7)

    figure.tight_layout()
    canvas.draw()


# =========================================================================
# Pestana base reutilizable
# =========================================================================


class CryptoTab(ttk.Frame):
    """Pestana base con la estructura comun para cifrar y descifrar.

    Contiene: selector de imagen, campos de parametros, botones de accion,
    y un canvas de matplotlib para la comparacion visual.
    """

    def __init__(self, parent, action_label, action_fn):
        """Inicializa la pestana.

        Parametros:
            parent: Widget padre (Notebook).
            action_label: Texto del boton principal ("Cifrar" o "Descifrar").
            action_fn: Funcion a ejecutar (scramble o descramble).
        """
        super().__init__(parent, padding=5)
        self.action_fn = action_fn
        self.input_image = None
        self.output_image = None

        # --- Selector de imagen ---
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", padx=10, pady=5)

        self.btn_open = ttk.Button(file_frame, text="Seleccionar imagen...",
                                   command=self.open_image)
        self.btn_open.pack(side="left")

        self.lbl_path = ttk.Label(file_frame, text="Ninguna imagen seleccionada",
                                  foreground="gray")
        self.lbl_path.pack(side="left", padx=10)

        # --- Campos de parametros ---
        self.fields = create_parameter_fields(self)

        # --- Botones de accion ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_action = ttk.Button(btn_frame, text=action_label,
                                     command=self.run_action)
        self.btn_action.pack(side="left", padx=5)

        self.btn_save = ttk.Button(btn_frame, text="Guardar resultado...",
                                   command=self.save_image, state="disabled")
        self.btn_save.pack(side="left", padx=5)

        self.lbl_status = ttk.Label(btn_frame, text="", foreground="green")
        self.lbl_status.pack(side="left", padx=15)

        # --- Canvas de matplotlib ---
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

    def open_image(self):
        """Abre un dialogo para seleccionar una imagen y la muestra."""
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imagenes", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not path:
            return

        self.input_image = np.array(Image.open(path).convert("RGB"))
        self.output_image = None
        self.btn_save.config(state="disabled")
        self.lbl_status.config(text="")

        # Mostrar solo la imagen de entrada
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.imshow(self.input_image)
        ax.set_title("Imagen cargada")
        ax.axis("off")
        self.figure.tight_layout()
        self.canvas.draw()

        # Mostrar ruta recortada
        display_path = path if len(path) < 60 else "..." + path[-57:]
        self.lbl_path.config(text=display_path, foreground="black")

    def run_action(self):
        """Ejecuta la operacion (scramble o descramble) y muestra la comparacion."""
        if self.input_image is None:
            messagebox.showwarning("Sin imagen", "Primero selecciona una imagen.")
            return

        try:
            key = get_key_from_fields(self.fields)
        except ValueError:
            messagebox.showerror("Error", "Los parametros deben ser valores numericos.")
            return

        self.lbl_status.config(text="Procesando...", foreground="orange")
        self.update_idletasks()

        self.output_image = self.action_fn(self.input_image, key)

        # Determinar titulos segun la operacion
        if self.action_fn is scramble:
            title_in, title_out = "Original", "Cifrada"
        else:
            title_in, title_out = "Cifrada", "Recuperada"

        draw_comparison(self.figure, self.canvas,
                        self.input_image, self.output_image,
                        title_in, title_out)

        self.btn_save.config(state="normal")
        self.lbl_status.config(text="Listo", foreground="green")

    def save_image(self):
        """Guarda la imagen resultado en el formato elegido por el usuario."""
        if self.output_image is None:
            return

        path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
            ],
        )
        if not path:
            return

        Image.fromarray(self.output_image).save(path)
        self.lbl_status.config(text=f"Guardada: {path}", foreground="green")


# =========================================================================
# Ventana principal
# =========================================================================


class CryptoApp(tk.Tk):
    """Ventana principal de la aplicacion de cifrado de imagenes."""

    def __init__(self):
        super().__init__()
        self.title("Cifrado de Imagenes - Adveccion Caotica (Double Gyre)")
        self.geometry("1100x750")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        tab_scramble = CryptoTab(notebook, "Cifrar", scramble)
        tab_descramble = CryptoTab(notebook, "Descifrar", descramble)

        notebook.add(tab_scramble, text="  Cifrar (Scramble)  ")
        notebook.add(tab_descramble, text="  Descifrar (Descramble)  ")


# =========================================================================
# Punto de entrada
# =========================================================================

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
