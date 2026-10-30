"""
grafico.py — Un gráfico de barras hecho a mano con Canvas.
===========================================================

No usamos librerías externas (como matplotlib) a propósito: así se ve
que un gráfico es solo geometría.

    Para cada carrera:
        ancho_barra = (total / total_maximo) * ancho_disponible

El Canvas es un lienzo: create_rectangle, create_text, create_line...
Las barras CRECEN animadas cada vez que cambian los datos.
"""

import tkinter as tk
from tkinter import ttk

from configuracion import COLORES
from interfaz.animaciones import animar
from interfaz.estilos import FUENTES

# Un color por barra (se repiten si hay más carreras que colores).
COLORES_BARRAS = ["#2F6FDE", "#1E9E5A", "#E08A00", "#8E5BD9", "#D64545", "#0F9BA8", "#7A8599"]


class GraficoCarreras(ttk.Frame):
    def __init__(self, padre: tk.Misc):
        super().__init__(padre, style="Tarjeta.TFrame")
        self.lienzo = tk.Canvas(self, background=COLORES["tarjeta"], highlightthickness=0, height=200)
        self.lienzo.pack(fill="both", expand=True)
        self._datos: list[tuple[str, int]] = []
        # Si cambian el tamaño de la ventana, redibujamos sin animación.
        self.lienzo.bind("<Configure>", lambda _e: self._dibujar(1.0))

    def actualizar(self, datos: list[tuple[str, int]]) -> None:
        """datos = [('Agronomía', 4), ('Medicina', 2), ...]"""
        self._datos = datos
        animar(self.lienzo, 700, self._dibujar)

    def _dibujar(self, progreso: float) -> None:
        lienzo = self.lienzo
        lienzo.delete("all")  # borrón y cuenta nueva en cada cuadro
        ancho, alto = lienzo.winfo_width(), lienzo.winfo_height()

        if not self._datos:
            lienzo.create_text(ancho / 2, alto / 2, text="Aún no hay datos para graficar.",
                               fill=COLORES["texto_suave"], font=FUENTES["normal"])
            return

        margen_izq, margen_der, arriba = 200, 50, 16
        disponible = max(10, ancho - margen_izq - margen_der)
        alto_fila = min(30, (alto - arriba * 2) / len(self._datos))
        maximo = max(total for _, total in self._datos)

        for i, (carrera, total) in enumerate(self._datos):
            y = arriba + i * alto_fila
            color = COLORES_BARRAS[i % len(COLORES_BARRAS)]
            largo = disponible * (total / maximo) * progreso

            lienzo.create_text(margen_izq - 10, y + alto_fila / 2, text=carrera, anchor="e",
                               fill=COLORES["texto"], font=FUENTES["normal"])
            # Pista gris (el 100 %) y barra de color encima.
            lienzo.create_rectangle(margen_izq, y + 5, margen_izq + disponible, y + alto_fila - 5,
                                    fill="#EEF2F8", outline="")
            lienzo.create_rectangle(margen_izq, y + 5, margen_izq + largo, y + alto_fila - 5,
                                    fill=color, outline="")
            lienzo.create_text(margen_izq + largo + 8, y + alto_fila / 2,
                               text=str(round(total * progreso)), anchor="w",
                               fill=COLORES["texto"], font=FUENTES["seccion"])
