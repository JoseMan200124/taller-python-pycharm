"""
encabezado.py — Título de la app + «semáforo» C R U D.
=======================================================

Las cuatro insignias se encienden cuando ocurre su operación:
pulsas «Crear» → se ilumina la C en verde durante un instante.
Es la forma más rápida de que el alumno conecte  botón ↔ letra ↔ SQL.
"""

import tkinter as tk

from configuracion import COLORES, OPERACIONES, SUBTITULO_APP, TITULO_APP
from interfaz.animaciones import pulsar
from interfaz.estilos import FUENTES, mezclar


class Encabezado(tk.Frame):
    def __init__(self, padre: tk.Misc, al_ver_codigo):
        super().__init__(padre, background=COLORES["encabezado"], padx=22, pady=14)

        # --- Izquierda: logo dibujado + títulos --------------------------------
        logo = tk.Canvas(self, width=44, height=44, background=COLORES["encabezado"],
                         highlightthickness=0)
        self._dibujar_logo(logo)
        logo.pack(side="left", padx=(0, 14))

        textos = tk.Frame(self, background=COLORES["encabezado"])
        textos.pack(side="left")
        tk.Label(textos, text=TITULO_APP, font=FUENTES["titulo"],
                 foreground="white", background=COLORES["encabezado"]).pack(anchor="w")
        tk.Label(textos, text=SUBTITULO_APP, font=FUENTES["subtitulo"],
                 foreground=COLORES["amarillo"], background=COLORES["encabezado"]).pack(anchor="w")

        # --- Derecha: las 4 insignias del CRUD ---------------------------------
        self.insignias: dict[str, tk.Label] = {}
        self._reposo = mezclar(COLORES["encabezado"], "#FFFFFF", 0.12)
        contenedor = tk.Frame(self, background=COLORES["encabezado"])
        contenedor.pack(side="right")

        # Botón para abrir/cerrar el Visor de código (lo mismo que la tecla F2).
        tk.Button(self, text="</>  Ver código  (F2)", command=al_ver_codigo, font=FUENTES["seccion"],
                  foreground=COLORES["encabezado"], background=COLORES["amarillo"],
                  activebackground=mezclar(COLORES["amarillo"], "#FFFFFF", 0.3),
                  activeforeground=COLORES["encabezado"], relief="flat", borderwidth=0,
                  padx=14, pady=6, cursor="hand2").pack(side="right", padx=(0, 24))

        for operacion, info in OPERACIONES.items():
            columna = tk.Frame(contenedor, background=COLORES["encabezado"])
            columna.pack(side="left", padx=5)
            insignia = tk.Label(columna, text=info["letra"], width=3, height=1,
                                font=FUENTES["insignia"], foreground="white",
                                background=self._reposo)
            insignia.pack()
            tk.Label(columna, text=info["nombre"].split(" · ")[1], font=FUENTES["pequena"],
                     foreground="#AFC2E6", background=COLORES["encabezado"]).pack()
            self.insignias[operacion] = insignia

    def encender(self, operacion: str) -> None:
        """Ilumina la insignia de la operación ('INSERT', 'SELECT', ...)."""
        if operacion in self.insignias:
            pulsar(self.insignias[operacion], OPERACIONES[operacion]["color"], self._reposo)

    @staticmethod
    def _dibujar_logo(lienzo: tk.Canvas) -> None:
        """Dos «serpientes» geométricas, un guiño al logo de Python, con Canvas."""
        lienzo.create_rectangle(4, 4, 26, 26, fill="#4B8BBE", outline="")
        lienzo.create_rectangle(18, 18, 40, 40, fill=COLORES["amarillo"], outline="")
        lienzo.create_oval(9, 8, 14, 13, fill="white", outline="")
        lienzo.create_oval(30, 31, 35, 36, fill="white", outline="")
