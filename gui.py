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
import matplotlib.pyplot as plt

from crypto import scramble, descramble


# =========================================================================
# Paleta de colores y constantes de estilo
# =========================================================================

COLORS = {
    "bg_deep":       "#080c10",   # fondo principal (mas oscuro = mas contraste)
    "bg_panel":      "#0d1117",   # paneles
    "bg_card":       "#161b22",   # tarjetas internas
    "bg_input":      "#1c2128",   # entradas
    "border":        "#444c56",   # bordes visibles (mas claros)
    "border_strong": "#6e7681",   # bordes en hover / foco
    "border_focus":  "#4493f8",   # borde al enfocar
    "accent":        "#4493f8",   # azul brillante
    "accent_hover":  "#79c0ff",   # hover accent
    "accent2":       "#d2a8ff",   # violeta mas brillante
    "success":       "#56d364",   # verde mas brillante
    "warning":       "#e3b341",   # amarillo mas brillante
    "error":         "#ff7b72",   # rojo mas brillante
    "text_primary":  "#f0f6fc",   # blanco casi puro
    "text_secondary":"#c9d1d9",   # gris claro (buen contraste)
    "text_muted":    "#8b949e",   # gris medio
    "btn_primary":   "#238636",
    "btn_primary_b": "#3fb950",   # borde verde brillante
    "btn_primary_h": "#2ea043",
    "btn_save":      "#1158c7",
    "btn_save_b":    "#4493f8",   # borde azul brillante
    "btn_save_h":    "#1a68d1",
    "btn_open_b":    "#6e7681",   # borde boton neutro
}

FONT_FAMILY = "Segoe UI"

FONTS = {
    "title":    (FONT_FAMILY, 18, "bold"),
    "subtitle": (FONT_FAMILY, 11),
    "label":    (FONT_FAMILY, 11, "bold"),
    "body":     (FONT_FAMILY, 11),
    "small":    (FONT_FAMILY, 10),
    "mono":     ("Consolas", 11),
    "section":  (FONT_FAMILY, 9,  "bold"),
    "status":   (FONT_FAMILY, 11, "bold"),
    "badge":    (FONT_FAMILY, 9,  "bold"),
    "param_lbl":(FONT_FAMILY, 12, "bold"),
}

# Tema matplotlib para coincidir con la UI oscura
MPL_STYLE = {
    "figure.facecolor":  COLORS["bg_card"],
    "axes.facecolor":    COLORS["bg_panel"],
    "axes.edgecolor":    COLORS["border"],
    "axes.labelcolor":   COLORS["text_secondary"],
    "axes.titlecolor":   COLORS["text_primary"],
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.color":       COLORS["text_muted"],
    "ytick.color":       COLORS["text_muted"],
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "grid.color":        COLORS["border"],
    "grid.alpha":        0.4,
    "text.color":        COLORS["text_primary"],
}


# =========================================================================
# Configuracion global de ttk.Style
# =========================================================================

def apply_dark_theme(root: tk.Tk) -> None:
    """Aplica el tema oscuro personalizado a todos los widgets ttk."""
    root.configure(bg=COLORS["bg_deep"])
    style = ttk.Style(root)
    style.theme_use("clam")

    # Frame / LabelFrame
    style.configure("TFrame",
                     background=COLORS["bg_panel"])
    style.configure("Card.TFrame",
                     background=COLORS["bg_card"],
                     relief="flat")
    style.configure("Deep.TFrame",
                     background=COLORS["bg_deep"])
    style.configure("TLabelframe",
                     background=COLORS["bg_card"],
                     bordercolor=COLORS["border"],
                     relief="flat",
                     padding=2)
    style.configure("TLabelframe.Label",
                     background=COLORS["bg_card"],
                     foreground=COLORS["accent2"],
                     font=FONTS["section"])

    # Labels
    style.configure("TLabel",
                     background=COLORS["bg_panel"],
                     foreground=COLORS["text_primary"],
                     font=FONTS["body"])
    style.configure("Title.TLabel",
                     background=COLORS["bg_deep"],
                     foreground=COLORS["text_primary"],
                     font=FONTS["title"])
    style.configure("Subtitle.TLabel",
                     background=COLORS["bg_deep"],
                     foreground=COLORS["text_secondary"],
                     font=FONTS["subtitle"])
    style.configure("Muted.TLabel",
                     background=COLORS["bg_card"],
                     foreground=COLORS["text_secondary"],
                     font=FONTS["body"])
    style.configure("Path.TLabel",
                     background=COLORS["bg_card"],
                     foreground=COLORS["text_secondary"],
                     font=FONTS["mono"])
    style.configure("Status.TLabel",
                     background=COLORS["bg_panel"],
                     font=FONTS["status"])
    style.configure("ParamLabel.TLabel",
                     background=COLORS["bg_card"],
                     foreground=COLORS["accent2"],
                     font=FONTS["label"])

    # Entry
    style.configure("TEntry",
                     fieldbackground=COLORS["bg_input"],
                     foreground=COLORS["text_primary"],
                     insertcolor=COLORS["accent"],
                     bordercolor=COLORS["border"],
                     lightcolor=COLORS["bg_input"],
                     darkcolor=COLORS["bg_input"],
                     font=FONTS["mono"],
                     padding=(6, 4))
    style.map("TEntry",
              bordercolor=[("focus", COLORS["border_focus"]),
                           ("!focus", COLORS["border"])])

    # Notebook (pestanas)
    style.configure("TNotebook",
                     background=COLORS["bg_deep"],
                     bordercolor=COLORS["border"],
                     tabmargins=[2, 5, 0, 0])
    style.configure("TNotebook.Tab",
                     background=COLORS["bg_panel"],
                     foreground=COLORS["text_muted"],
                     font=FONTS["label"],
                     padding=[22, 10],
                     bordercolor=COLORS["border"])
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["bg_card"]),
                          ("active",   COLORS["bg_card"])],
              foreground=[("selected", COLORS["accent"]),
                          ("active",   COLORS["text_primary"])],
              expand=[("selected", [1, 1, 1, 0])])

    # Boton base (neutro/secundario) — borde visible
    style.configure("TButton",
                     background=COLORS["bg_card"],
                     foreground=COLORS["text_primary"],
                     bordercolor=COLORS["border"],
                     lightcolor=COLORS["border"],
                     darkcolor=COLORS["border"],
                     borderwidth=2,
                     font=FONTS["body"],
                     padding=(14, 7),
                     relief="solid")
    style.map("TButton",
              background=[("active",   COLORS["bg_input"]),
                          ("disabled", COLORS["bg_panel"])],
              foreground=[("disabled", COLORS["text_muted"])],
              bordercolor=[("active",   COLORS["border_strong"]),
                           ("disabled", COLORS["bg_panel"])])

    # Boton primario — borde verde brillante
    style.configure("Primary.TButton",
                     background=COLORS["btn_primary"],
                     foreground="#ffffff",
                     bordercolor=COLORS["btn_primary_b"],
                     lightcolor=COLORS["btn_primary_b"],
                     darkcolor=COLORS["btn_primary_b"],
                     borderwidth=2,
                     font=FONTS["label"],
                     padding=(20, 8),
                     relief="solid")
    style.map("Primary.TButton",
              background=[("active",   COLORS["btn_primary_h"]),
                          ("disabled", COLORS["bg_panel"])],
              foreground=[("disabled", COLORS["text_muted"])],
              bordercolor=[("active",   COLORS["accent2"]),
                           ("disabled", COLORS["bg_panel"])])

    # Boton guardar — borde azul brillante
    style.configure("Save.TButton",
                     background=COLORS["btn_save"],
                     foreground="#ffffff",
                     bordercolor=COLORS["btn_save_b"],
                     lightcolor=COLORS["btn_save_b"],
                     darkcolor=COLORS["btn_save_b"],
                     borderwidth=2,
                     font=FONTS["label"],
                     padding=(18, 8),
                     relief="solid")
    style.map("Save.TButton",
              background=[("active",   COLORS["btn_save_h"]),
                          ("disabled", COLORS["bg_panel"])],
              foreground=[("disabled", COLORS["text_muted"])],
              bordercolor=[("active",   COLORS["accent_hover"]),
                           ("disabled", COLORS["bg_panel"])])

    # Boton abrir archivo — borde gris visible
    style.configure("Open.TButton",
                     background=COLORS["bg_card"],
                     foreground=COLORS["text_primary"],
                     bordercolor=COLORS["btn_open_b"],
                     lightcolor=COLORS["btn_open_b"],
                     darkcolor=COLORS["btn_open_b"],
                     borderwidth=2,
                     font=FONTS["body"],
                     padding=(14, 7),
                     relief="solid")
    style.map("Open.TButton",
              background=[("active", COLORS["bg_input"])],
              bordercolor=[("active", COLORS["border_focus"])])

    # Separator
    style.configure("TSeparator",
                     background=COLORS["border"])

    # Scrollbar
    style.configure("TScrollbar",
                     background=COLORS["bg_panel"],
                     troughcolor=COLORS["bg_deep"],
                     bordercolor=COLORS["border"],
                     arrowcolor=COLORS["text_muted"])


# =========================================================================
# Widgets auxiliares
# =========================================================================

class Divider(tk.Frame):
    """Linea separadora horizontal con color del tema."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                         height=1,
                         bg=COLORS["border"],
                         **kwargs)


class SectionHeader(tk.Frame):
    """Encabezado de seccion con etiqueta y linea decorativa."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)
        tk.Label(self,
                 text=text.upper(),
                 bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"],
                 font=(FONT_FAMILY, 9, "bold")).pack(side="left", padx=(0, 10))
        Divider(self).pack(side="left", fill="x", expand=True)


class StatusIndicator(tk.Frame):
    """Pastilla de estado con punto de color + texto."""

    PRESETS = {
        "idle":       (COLORS["text_muted"],    COLORS["bg_panel"]),
        "loading":    (COLORS["warning"],        COLORS["bg_panel"]),
        "success":    (COLORS["success"],        COLORS["bg_panel"]),
        "error":      (COLORS["error"],          COLORS["bg_panel"]),
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_panel"], **kwargs)
        self._dot = tk.Label(self, text="●", bg=COLORS["bg_panel"],
                             font=(FONT_FAMILY, 13))
        self._dot.pack(side="left", padx=(0, 6))
        self._text = tk.Label(self, text="", bg=COLORS["bg_panel"],
                              font=FONTS["status"])
        self._text.pack(side="left")

    def set(self, state: str, message: str) -> None:
        color, _ = self.PRESETS.get(state, self.PRESETS["idle"])
        self._dot.config(fg=color)
        self._text.config(text=message, fg=color)


# =========================================================================
# Funciones auxiliares
# =========================================================================

def create_parameter_fields(parent) -> dict:
    """Crea los campos de parametros de la llave con estilo oscuro."""

    outer = tk.Frame(parent, bg=COLORS["bg_card"],
                     highlightbackground=COLORS["border"],
                     highlightthickness=1)
    outer.pack(fill="x", padx=12, pady=(0, 8))

    SectionHeader(outer, "Parametros de la llave").pack(
        fill="x", padx=12, pady=(10, 6))

    row_frame = tk.Frame(outer, bg=COLORS["bg_card"])
    row_frame.pack(fill="x", padx=12, pady=(0, 12))

    defaults = {
        "A":       ("A",       "0.25"),
        "epsilon": ("ε",       "0.25"),
        "omega":   ("ω",       "6.283185307179586"),
        "dt":      ("dt",      "0.1"),
        "N":       ("N",       "20"),
    }

    fields = {}
    for i, (key, (symbol, default)) in enumerate(defaults.items()):
        cell = tk.Frame(row_frame, bg=COLORS["bg_card"])
        cell.pack(side="left", expand=True, fill="x", padx=5)

        tk.Label(cell, text=symbol,
                 bg=COLORS["bg_card"],
                 fg=COLORS["accent2"],
                 font=FONTS["param_lbl"]).pack(anchor="w", pady=(0, 3))

        var = tk.StringVar(value=default)
        entry = tk.Entry(cell,
                         textvariable=var,
                         width=14,
                         bg=COLORS["bg_input"],
                         fg=COLORS["text_primary"],
                         insertbackground=COLORS["accent"],
                         relief="flat",
                         highlightbackground=COLORS["border"],
                         highlightthickness=2,
                         font=FONTS["mono"])
        entry.pack(fill="x", ipady=4)

        # Efecto focus
        entry.bind("<FocusIn>",  lambda e, w=entry: w.config(
            highlightbackground=COLORS["border_focus"]))
        entry.bind("<FocusOut>", lambda e, w=entry: w.config(
            highlightbackground=COLORS["border"]))

        fields[key] = var

    return fields


def get_key_from_fields(fields: dict) -> dict:
    """Lee los campos y retorna el diccionario de llave."""
    return {
        "A":       float(fields["A"].get()),
        "epsilon": float(fields["epsilon"].get()),
        "omega":   float(fields["omega"].get()),
        "dt":      float(fields["dt"].get()),
        "N":       int(fields["N"].get()),
    }


def draw_comparison(figure, canvas, img_input, img_output,
                    title_in, title_out) -> None:
    """Dibuja la comparacion 2x2 de imagenes e histogramas con tema oscuro."""
    for key, val in MPL_STYLE.items():
        plt.rcParams[key] = val

    figure.clear()
    figure.patch.set_facecolor(COLORS["bg_card"])

    axes = [figure.add_subplot(2, 2, i) for i in range(1, 5)]

    # --- Imagenes ---
    axes[0].imshow(img_input)
    axes[0].set_title(title_in, color=COLORS["text_primary"],
                      fontsize=11, pad=8)
    axes[0].axis("off")

    axes[1].imshow(img_output)
    axes[1].set_title(title_out, color=COLORS["text_primary"],
                      fontsize=11, pad=8)
    axes[1].axis("off")

    HIST_COLORS = ["#f87171", "#4ade80", "#60a5fa"]

    # --- Histogramas ---
    for ax_idx, img in [(2, img_input), (3, img_output)]:
        ax = axes[ax_idx]
        ax.set_facecolor(COLORS["bg_panel"])
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS["border"])
        ax.grid(True, color=COLORS["border"], alpha=0.3, linewidth=0.5)

        if img.ndim == 3:
            for ch, color in enumerate(HIST_COLORS):
                ax.hist(img[:, :, ch].ravel(),
                        bins=256, range=(0, 256),
                        color=color, alpha=0.6, linewidth=0)
        else:
            ax.hist(img.ravel(), bins=256, range=(0, 256),
                    color=COLORS["text_secondary"], alpha=0.7, linewidth=0)

        label = "Histograma — " + (title_in if ax_idx == 2 else title_out)
        ax.set_title(label, color=COLORS["text_secondary"],
                     fontsize=10, pad=6)
        ax.set_xlabel("Intensidad", fontsize=9,
                      color=COLORS["text_muted"])
        ax.set_ylabel("Frecuencia",  fontsize=9,
                      color=COLORS["text_muted"])
        ax.tick_params(colors=COLORS["text_muted"], labelsize=8.5)

    figure.tight_layout(pad=1.5)
    canvas.draw()


# =========================================================================
# Pestana base reutilizable
# =========================================================================

class CryptoTab(ttk.Frame):
    """Pestana con estructura comun para cifrar y descifrar."""

    def __init__(self, parent, action_label: str, action_fn):
        super().__init__(parent, style="Card.TFrame", padding=0)
        self.action_fn   = action_fn
        self.input_image  = None
        self.output_image = None

        self._build_file_selector()
        self._build_params()
        self._build_action_bar(action_label)
        self._build_canvas()

    # ------------------------------------------------------------------
    # Construccion de secciones
    # ------------------------------------------------------------------

    def _build_file_selector(self) -> None:
        outer = tk.Frame(self, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1)
        outer.pack(fill="x", padx=12, pady=(12, 4))

        SectionHeader(outer, "Imagen de entrada").pack(
            fill="x", padx=12, pady=(10, 6))

        row = tk.Frame(outer, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=12, pady=(0, 12))

        self.btn_open = ttk.Button(row,
                                   text="  Abrir archivo...",
                                   style="Open.TButton",
                                   command=self.open_image)
        self.btn_open.pack(side="left")

        self.lbl_path = tk.Label(row,
                                 text="Ninguna imagen seleccionada",
                                 bg=COLORS["bg_card"],
                                 fg=COLORS["text_muted"],
                                 font=FONTS["body"])
        self.lbl_path.pack(side="left", padx=14)

    def _build_params(self) -> None:
        self.fields = create_parameter_fields(self)

    def _build_action_bar(self, action_label: str) -> None:
        bar = tk.Frame(self, bg=COLORS["bg_panel"])
        bar.pack(fill="x", padx=12, pady=(0, 8))

        self.btn_action = ttk.Button(bar,
                                     text=f"  {action_label}  ",
                                     style="Primary.TButton",
                                     command=self.run_action)
        self.btn_action.pack(side="left", padx=(0, 6))

        self.btn_save = ttk.Button(bar,
                                   text="  Guardar resultado  ",
                                   style="Save.TButton",
                                   command=self.save_image,
                                   state="disabled")
        self.btn_save.pack(side="left")

        self.status = StatusIndicator(bar)
        self.status.pack(side="left", padx=20)

    def _build_canvas(self) -> None:
        canvas_outer = tk.Frame(self,
                                bg=COLORS["bg_card"],
                                highlightbackground=COLORS["border"],
                                highlightthickness=1)
        canvas_outer.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        SectionHeader(canvas_outer, "Visualizacion").pack(
            fill="x", padx=12, pady=(10, 6))

        self.figure = Figure(figsize=(10, 5.5), dpi=100,
                             facecolor=COLORS["bg_card"])
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_outer)
        widget = self.canvas.get_tk_widget()
        widget.configure(bg=COLORS["bg_card"],
                         highlightthickness=0)
        widget.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        # Placeholder inicial
        ax = self.figure.add_subplot(1, 1, 1)
        ax.set_facecolor(COLORS["bg_panel"])
        ax.text(0.5, 0.5,
                "Selecciona una imagen para comenzar",
                ha="center", va="center",
                color=COLORS["text_muted"],
                fontsize=13,
                transform=ax.transAxes)
        ax.axis("off")
        for spine in ax.spines.values():
            spine.set_visible(False)
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def open_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imagenes", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if not path:
            return

        self.input_image  = np.array(Image.open(path).convert("RGB"))
        self.output_image = None
        self.btn_save.config(state="disabled")
        self.status.set("idle", "")

        # Mostrar imagen de entrada con tema oscuro
        for key, val in MPL_STYLE.items():
            plt.rcParams[key] = val
        self.figure.clear()
        self.figure.patch.set_facecolor(COLORS["bg_card"])
        ax = self.figure.add_subplot(1, 1, 1)
        ax.imshow(self.input_image)
        ax.set_title("Imagen cargada", color=COLORS["text_primary"],
                     fontsize=10, pad=8)
        ax.axis("off")
        self.figure.tight_layout(pad=1.5)
        self.canvas.draw()

        display_path = path if len(path) < 65 else "..." + path[-62:]
        self.lbl_path.config(text=display_path,
                             fg=COLORS["text_secondary"])

    def run_action(self) -> None:
        if self.input_image is None:
            messagebox.showwarning("Sin imagen",
                                   "Primero selecciona una imagen.")
            return
        try:
            key = get_key_from_fields(self.fields)
        except ValueError:
            messagebox.showerror("Parametros invalidos",
                                 "Todos los parametros deben ser valores numericos.")
            return

        self.status.set("loading", "Procesando...")
        self.update_idletasks()

        self.output_image = self.action_fn(self.input_image, key)

        if self.action_fn is scramble:
            title_in, title_out = "Original", "Cifrada"
        else:
            title_in, title_out = "Cifrada", "Recuperada"

        draw_comparison(self.figure, self.canvas,
                        self.input_image, self.output_image,
                        title_in, title_out)

        self.btn_save.config(state="normal")
        self.status.set("success", "Completado")

    def save_image(self) -> None:
        if self.output_image is None:
            return
        path = filedialog.asksaveasfilename(
            title="Guardar imagen resultado",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
        )
        if not path:
            return
        Image.fromarray(self.output_image).save(path)
        self.status.set("success", f"Guardado en {path}")


# =========================================================================
# Header superior de la aplicacion
# =========================================================================

class AppHeader(tk.Frame):
    """Barra de encabezado con titulo, subtitulo y separador."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_deep"], **kwargs)

        inner = tk.Frame(self, bg=COLORS["bg_deep"])
        inner.pack(fill="x", padx=24, pady=(18, 16))

        # Bloque de titulo
        title_block = tk.Frame(inner, bg=COLORS["bg_deep"])
        title_block.pack(side="left")

        # Pastilla de version / badge
        badge = tk.Frame(title_block, bg=COLORS["accent"],
                         padx=8, pady=3)
        badge.pack(side="left", anchor="n", padx=(0, 12), pady=(6, 0))
        tk.Label(badge, text="v1.0",
                 bg=COLORS["accent"], fg="#fff",
                 font=FONTS["badge"]).pack()

        text_block = tk.Frame(title_block, bg=COLORS["bg_deep"])
        text_block.pack(side="left")

        tk.Label(text_block,
                 text="Cifrado de Imagenes",
                 bg=COLORS["bg_deep"],
                 fg=COLORS["text_primary"],
                 font=FONTS["title"]).pack(anchor="w")

        tk.Label(text_block,
                 text="Adveccion caotica — Double Gyre Flow",
                 bg=COLORS["bg_deep"],
                 fg=COLORS["text_secondary"],
                 font=FONTS["subtitle"]).pack(anchor="w")

        Divider(self).pack(fill="x")


# =========================================================================
# Ventana principal
# =========================================================================

class CryptoApp(tk.Tk):
    """Ventana principal de la aplicacion de cifrado de imagenes."""

    def __init__(self):
        super().__init__()
        self.title("Cifrado de Imagenes — Double Gyre Chaotic Advection")
        self.geometry("1150x820")
        self.minsize(900, 660)
        self.configure(bg=COLORS["bg_deep"])

        apply_dark_theme(self)

        # Header
        AppHeader(self).pack(fill="x")

        # Notebook con pestanas
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=0, pady=0)

        tab_scramble   = CryptoTab(notebook, "Cifrar",    scramble)
        tab_descramble = CryptoTab(notebook, "Descifrar", descramble)

        notebook.add(tab_scramble,   text="    Cifrar    ")
        notebook.add(tab_descramble, text="    Descifrar    ")

        # Barra de estado inferior
        status_bar = tk.Frame(self, bg=COLORS["bg_panel"],
                              highlightbackground=COLORS["border"],
                              highlightthickness=1)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar,
                 text="Double Gyre Chaotic Advection  •  Algoritmo de cifrado por flujo caotico",
                 bg=COLORS["bg_panel"],
                 fg=COLORS["text_muted"],
                 font=FONTS["small"],
                 padx=16, pady=7).pack(side="left")


# =========================================================================
# Punto de entrada
# =========================================================================

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()
