"""
consola_sql.py — Rayos X: el SQL que hay detrás de cada botón.
===============================================================

Cada vez que BaseDatos ejecuta algo, esta consola lo muestra así:

    10:42:07  C · INSERT   ✓ 1 fila · 0.31 ms
    INSERT INTO estudiantes (nombre, correo, ...) VALUES (?, ?, ...)
      valores → ('Ana', 'ana@correo.com', ...)

Así el alumno ve que:
    1. cada botón produce UNA sentencia SQL,
    2. los ? se llenan con valores aparte (consultas parametrizadas),
    3. la base de datos responde con filas afectadas o un error.

Técnica de tkinter: tk.Text con «tags» (etiquetas de estilo) para colorear
partes del texto, igual que el resaltado de sintaxis de PyCharm.
"""

import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from configuracion import COLORES, OPERACIONES
from interfaz.estilos import FUENTES

PALABRAS_CLAVE = re.compile(
    r"\b(SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|ORDER BY|GROUP BY|"
    r"LIKE|OR|AND|COUNT|AS|DESC|ASC)\b"
)
MAXIMO_LINEAS = 400  # para que la consola no crezca sin fin


class ConsolaSQL(ttk.Frame):
    def __init__(self, padre: tk.Misc):
        super().__init__(padre, style="Tarjeta.TFrame")

        self.texto = tk.Text(self, width=40, height=7, wrap="word", font=FUENTES["codigo"],
                             background=COLORES["consola_fondo"], foreground=COLORES["consola_texto"],
                             insertbackground="white", relief="flat", padx=14, pady=10,
                             borderwidth=0, highlightthickness=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.texto.yview)
        self.texto.configure(yscrollcommand=barra.set)
        self.texto.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # --- Estilos («tags») del texto -----------------------------------------
        self.texto.tag_configure("hora", foreground=COLORES["consola_suave"])
        self.texto.tag_configure("palabra", foreground=COLORES["consola_palabra"],
                                 font=FUENTES["codigo_negrita"])
        self.texto.tag_configure("valor", foreground=COLORES["consola_valor"])
        self.texto.tag_configure("suave", foreground=COLORES["consola_suave"])
        self.texto.tag_configure("error", foreground="#FF7B7B", font=FUENTES["codigo_negrita"])
        for operacion, info in OPERACIONES.items():
            self.texto.tag_configure(operacion, foreground=info["color"], font=FUENTES["codigo_negrita"])

        self._escribir([("-- Consola SQL en vivo: cada clic en la ventana aparece aquí.\n", "suave"),
                        ("-- Los ? son huecos que SQLite llena con los «valores» de forma segura.\n\n",
                         "suave")])

    # -----------------------------------------------------------------------
    def registrar(self, detalle: dict) -> None:
        """Lo llama BaseDatos (es un «oyente») después de cada sentencia."""
        sql = " ".join(detalle["sql"].split())  # quitamos saltos de línea y espacios dobles
        operacion = sql.split()[0].upper()
        info = OPERACIONES.get(operacion, {"letra": "·"})

        hora = datetime.now().strftime("%H:%M:%S")

        # Consultas que la app hace sola para repintar → una línea discreta.
        if detalle.get("motivo") == "refresco" and not detalle["error"]:
            resumen = sql if len(sql) <= 60 else sql[:57] + "..."
            self._escribir([(f"{hora}  ↻ refresco  {resumen}  ({detalle['filas']} filas)\n\n", "suave")])
            return

        partes = [(f"{hora}  ", "hora"), (f"{info['letra']} · {operacion:<7}", operacion)]

        if detalle["error"]:
            partes.append((f"  ✗ {detalle['error']}\n", "error"))
        else:
            filas = detalle["filas"]
            palabra = "fila" if filas == 1 else "filas"
            partes.append((f"  ✓ {filas} {palabra} · {detalle['ms']:.2f} ms\n", "suave"))

        partes.extend(self._resaltar(sql))
        if detalle["parametros"]:
            partes.append(("\n  valores → ", "suave"))
            partes.append((repr(tuple(detalle["parametros"])), "valor"))
        partes.append(("\n\n", None))

        self._escribir(partes)

    # -----------------------------------------------------------------------
    @staticmethod
    def _resaltar(sql: str) -> list[tuple[str, str | None]]:
        """Parte el SQL en trozos: palabras clave en morado, el resto normal."""
        partes, ultimo = [], 0
        for coincidencia in PALABRAS_CLAVE.finditer(sql):
            partes.append((sql[ultimo:coincidencia.start()], None))
            partes.append((coincidencia.group(), "palabra"))
            ultimo = coincidencia.end()
        partes.append((sql[ultimo:], None))
        return partes

    def _escribir(self, partes: list) -> None:
        self.texto.configure(state="normal")
        for texto, estilo in partes:
            self.texto.insert("end", texto, estilo or ())
        # Si hay demasiadas líneas, borramos las más viejas.
        lineas = int(self.texto.index("end-1c").split(".")[0])
        if lineas > MAXIMO_LINEAS:
            self.texto.delete("1.0", f"{lineas - MAXIMO_LINEAS}.0")
        self.texto.see("end")              # bajar hasta lo más nuevo
        self.texto.configure(state="disabled")  # solo lectura
