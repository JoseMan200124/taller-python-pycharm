"""
estilos.py — El «CSS» de tkinter.
==================================

tkinter tiene dos familias de widgets:
    tk.Label, tk.Button...   → clásicos, se pintan uno por uno.
    ttk.Label, ttk.Button... → «temáticos», se pintan con ESTILOS compartidos.

Con ttk.Style definimos una vez cómo se ve, por ejemplo, un botón verde
(«Crear.TButton») y luego cualquier botón puede usarlo.
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from configuracion import COLORES

# Se llena en configurar_estilos(). Los demás módulos leen de aquí.
FUENTES: dict[str, tuple] = {}


def _primera_fuente_disponible(*candidatas: str) -> str:
    """Windows, macOS y Linux traen fuentes distintas: usamos la primera que exista."""
    instaladas = set(tkfont.families())
    for nombre in candidatas:
        if nombre in instaladas:
            return nombre
    return "TkDefaultFont"


def configurar_estilos(raiz: tk.Tk) -> None:
    """Prepara fuentes y estilos. Se llama UNA vez, al crear la ventana."""
    texto = _primera_fuente_disponible("Segoe UI", "Helvetica Neue", "Ubuntu", "DejaVu Sans", "Arial")
    codigo = _primera_fuente_disponible("Cascadia Code", "Consolas", "JetBrains Mono",
                                        "Menlo", "DejaVu Sans Mono", "Courier New")
    FUENTES.update({
        "titulo": (texto, 17, "bold"),
        "subtitulo": (texto, 10),
        "seccion": (texto, 11, "bold"),
        "normal": (texto, 10),
        "pequena": (texto, 9),
        "insignia": (texto, 15, "bold"),
        "pizarra": (texto, 10),
        "codigo": (codigo, 10),
        "codigo_negrita": (codigo, 10, "bold"),
        # Visor de código: un poco más grande para que se lea en el proyector.
        "editor": (codigo, 12),
        "editor_negrita": (codigo, 12, "bold"),
        "editor_cursiva": (codigo, 12, "italic"),
    })

    estilo = ttk.Style(raiz)
    # «clam» es el tema que mejor respeta los colores en Windows, macOS y Linux.
    estilo.theme_use("clam")

    raiz.configure(background=COLORES["fondo"])

    # --- Contenedores --------------------------------------------------------
    estilo.configure("TFrame", background=COLORES["fondo"])
    estilo.configure("Tarjeta.TFrame", background=COLORES["tarjeta"])
    estilo.configure("TLabel", background=COLORES["tarjeta"], foreground=COLORES["texto"],
                     font=FUENTES["normal"])
    estilo.configure("Seccion.TLabel", font=FUENTES["seccion"])
    estilo.configure("Suave.TLabel", foreground=COLORES["texto_suave"], font=FUENTES["pequena"])
    estilo.configure("Error.TLabel", foreground=COLORES["error"], font=FUENTES["pequena"])
    estilo.configure("Barra.TLabel", background=COLORES["fondo"],
                     foreground=COLORES["texto_suave"], font=FUENTES["pequena"])

    # --- Campos de texto -----------------------------------------------------
    for nombre in ("TEntry", "TCombobox"):
        estilo.configure(nombre, padding=6, fieldbackground="white",
                         bordercolor=COLORES["borde"], lightcolor=COLORES["borde"])
    # Variante roja para campos con error.
    estilo.configure("Error.TEntry", fieldbackground=COLORES["campo_error"],
                     bordercolor=COLORES["error"], lightcolor=COLORES["error"])
    # Un Combobox «readonly» se ve gris por defecto: lo forzamos a blanco.
    estilo.map("TCombobox", fieldbackground=[("readonly", "white")])
    estilo.map("Error.TCombobox", fieldbackground=[("readonly", COLORES["campo_error"])])
    estilo.configure("Error.TCombobox", fieldbackground=COLORES["campo_error"],
                     bordercolor=COLORES["error"], lightcolor=COLORES["error"])

    # --- Botones: uno por cada operación del CRUD ---------------------------
    for nombre, color in (("Crear", COLORES["crear"]), ("Actualizar", COLORES["actualizar"]),
                          ("Eliminar", COLORES["eliminar"]), ("Leer", COLORES["leer"])):
        estilo.configure(f"{nombre}.TButton", background=color, foreground="white",
                         font=FUENTES["seccion"], padding=(14, 8), borderwidth=0)
        # map() cambia el aspecto según el estado: encima, presionado, desactivado.
        estilo.map(f"{nombre}.TButton",
                   background=[("disabled", "#C9CFDA"), ("pressed", color), ("active", _aclarar(color, 0.15))],
                   foreground=[("disabled", "#F4F6FA")])
    estilo.configure("Limpiar.TButton", background=COLORES["tarjeta"], foreground=COLORES["texto"],
                     font=FUENTES["normal"], padding=(12, 8), bordercolor=COLORES["borde"])
    estilo.map("Limpiar.TButton", background=[("active", COLORES["fondo"])])

    # --- Tabla (Treeview) ----------------------------------------------------
    estilo.configure("Treeview", rowheight=30, font=FUENTES["normal"],
                     background="white", fieldbackground="white", borderwidth=0)
    estilo.configure("Treeview.Heading", font=FUENTES["seccion"],
                     background=COLORES["encabezado"], foreground="white", padding=6, relief="flat")
    estilo.map("Treeview.Heading", background=[("active", _aclarar(COLORES["encabezado"], 0.15))])
    estilo.map("Treeview", background=[("selected", COLORES["leer"])],
               foreground=[("selected", "white")])

    # --- Pestañas ------------------------------------------------------------
    estilo.configure("TNotebook", background=COLORES["fondo"], borderwidth=0)
    estilo.configure("TNotebook.Tab", font=FUENTES["normal"], padding=(14, 6))
    estilo.map("TNotebook.Tab", background=[("selected", COLORES["tarjeta"])])


# ---------------------------------------------------------------------------
# 🎨 Utilidades de color (las usan también las animaciones)
# ---------------------------------------------------------------------------
def hex_a_rgb(color: str) -> tuple[int, int, int]:
    """'#1E9E5A' → (30, 158, 90)"""
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_a_hex(r: float, g: float, b: float) -> str:
    """(30, 158, 90) → '#1e9e5a'"""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def mezclar(color_a: str, color_b: str, t: float) -> str:
    """
    Mezcla dos colores. t=0 → color_a, t=1 → color_b, t=0.5 → mitad y mitad.
    Es la base de todas las animaciones de «desvanecer».
    """
    a, b = hex_a_rgb(color_a), hex_a_rgb(color_b)
    return rgb_a_hex(*(a[i] + (b[i] - a[i]) * t for i in range(3)))


def _aclarar(color: str, cantidad: float) -> str:
    return mezclar(color, "#FFFFFF", cantidad)
