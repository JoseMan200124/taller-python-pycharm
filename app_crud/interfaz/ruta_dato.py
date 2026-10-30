"""
ruta_dato.py — El viaje del dato, dibujado y animado.
======================================================

Cinco estaciones, una por cada capa del programa:

    (Ventana) ──► (Validar) ──► (Repositorio) ──► (SQL) ──► (taller.db)

En cada operación, un punto de color recorre la ruta:
    • verde/naranja/rojo/azul según la letra del CRUD,
    • si la validación falla, el punto se detiene en «Validar» con una ✕,
    • si SQLite rechaza el dato (ej. correo repetido), se detiene en «SQL».

Leer y eliminar no pasan por «Validar» (no hay datos escritos que revisar),
por eso esa estación se ve apagada en esos casos.
"""

import tkinter as tk
from tkinter import ttk

from configuracion import COLORES
from interfaz.animaciones import animar
from interfaz.estilos import FUENTES

# (nombre de la estación, archivo de Python responsable)
ESTACIONES = [
    ("Ventana", "formulario.py"),
    ("Validar", "validaciones.py"),
    ("Repositorio", "repositorio.py"),
    ("SQL", "base_datos.py"),
    ("taller.db", "SQLite"),
]
RADIO = 13


class RutaDelDato(ttk.Frame):
    def __init__(self, padre: tk.Misc):
        super().__init__(padre, style="Tarjeta.TFrame", padding=(18, 8, 18, 4))
        ttk.Label(self, text="Ruta del dato", style="Seccion.TLabel").pack(side="left", anchor="n", padx=(0, 12))

        self.lienzo = tk.Canvas(self, height=74, background=COLORES["tarjeta"], highlightthickness=0)
        self.lienzo.pack(side="left", fill="x", expand=True)

        # Estado del dibujo (lo cambia recorrer() y lo lee _dibujar()).
        self._color = COLORES["leer"]
        self._avance = -1.0        # posición del punto: 0 = Ventana ... 4 = taller.db
        self._hasta = len(ESTACIONES) - 1
        self._fallo = False
        self._saltar: set[int] = set()

        self.lienzo.bind("<Configure>", lambda _e: self._dibujar())

    # -----------------------------------------------------------------------
    def recorrer(self, color: str, hasta: int | None = None, fallo: bool = False,
                 saltar: set[int] | None = None) -> None:
        """Anima el punto desde «Ventana» hasta la estación `hasta`."""
        self._color = color
        self._hasta = len(ESTACIONES) - 1 if hasta is None else hasta
        self._fallo = fallo
        self._saltar = saltar or set()

        def avanzar(t: float) -> None:
            self._avance = t * self._hasta
            self._dibujar()

        animar(self.lienzo, 220 * max(1, self._hasta), avanzar)

    # -----------------------------------------------------------------------
    def _x(self, indice: float) -> float:
        """Posición horizontal de una estación (reparte el ancho en partes iguales)."""
        ancho = self.lienzo.winfo_width()
        margen = 46
        return margen + (ancho - 2 * margen) * indice / (len(ESTACIONES) - 1)

    def _dibujar(self) -> None:
        c = self.lienzo
        c.delete("all")
        y = 18

        # 1) Riel gris de fondo y tramo ya recorrido en color.
        c.create_line(self._x(0), y, self._x(len(ESTACIONES) - 1), y, fill=COLORES["borde"], width=4)
        if self._avance > 0:
            c.create_line(self._x(0), y, self._x(self._avance), y, fill=self._color, width=4)

        # 2) Las estaciones.
        for i, (nombre, archivo) in enumerate(ESTACIONES):
            x = self._x(i)
            alcanzada = i <= self._avance + 0.001
            if i in self._saltar:
                relleno, borde, texto = COLORES["tarjeta"], COLORES["borde"], COLORES["borde"]
            elif alcanzada:
                relleno, borde, texto = self._color, self._color, COLORES["texto"]
            else:
                relleno, borde, texto = COLORES["tarjeta"], COLORES["borde"], COLORES["texto_suave"]

            c.create_oval(x - RADIO, y - RADIO, x + RADIO, y + RADIO, fill=relleno, outline=borde, width=2)
            c.create_text(x, y + RADIO + 11, text=nombre, fill=texto, font=FUENTES["pequena"])
            if self._x(1) - self._x(0) > 125:   # el nombre del archivo solo si hay espacio
                c.create_text(x, y + RADIO + 26, text=archivo, fill=COLORES["texto_suave"],
                              font=(FUENTES["codigo"][0], 8))

        # 3) Si falló, una ✕ blanca en la estación donde se detuvo.
        if self._fallo and self._avance >= self._hasta - 0.001:
            x = self._x(self._hasta)
            d = RADIO / 2.2
            c.create_line(x - d, y - d, x + d, y + d, fill="white", width=3)
            c.create_line(x - d, y + d, x + d, y - d, fill="white", width=3)
        # 4) El «paquete» viajero.
        elif 0 <= self._avance < self._hasta:
            x = self._x(self._avance)
            c.create_oval(x - 6, y - 6, x + 6, y + 6, fill="white", outline=self._color, width=3)
