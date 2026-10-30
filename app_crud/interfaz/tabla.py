"""
tabla.py — Donde se VEN los datos (la «R» de Read).
====================================================

ttk.Treeview sirve para árboles y tablas. Aquí lo usamos como tabla:
    • columns=...      → nombres internos de las columnas.
    • heading(...)     → el título visible de cada columna.
    • insert("", "end", iid=..., values=...) → agrega una fila.
    • <<TreeviewSelect>> → evento que ocurre al hacer clic en una fila.

Arriba hay un buscador: cada letra que escribes dispara un SELECT ... LIKE.
"""

import tkinter as tk
from tkinter import ttk

from configuracion import COLORES
from interfaz.animaciones import destellar_fila
from interfaz.estilos import FUENTES

# (clave, título, ancho en píxeles, alineación)
COLUMNAS = [
    ("id", "#", 50, "center"),
    ("nombre", "Nombre", 160, "w"),
    ("correo", "Correo", 220, "w"),
    ("telefono", "Teléfono", 90, "center"),
    ("edad", "Edad", 62, "center"),
    ("carrera", "Carrera", 180, "w"),
]


class TablaEstudiantes(ttk.Frame):
    def __init__(self, padre: tk.Misc, al_seleccionar, al_buscar):
        super().__init__(padre, style="Tarjeta.TFrame", padding=14)
        self._al_seleccionar = al_seleccionar

        # --- Barra superior: título + buscador ---------------------------------
        barra = ttk.Frame(self, style="Tarjeta.TFrame")
        barra.pack(fill="x", pady=(0, 10))
        ttk.Label(barra, text="Estudiantes registrados", style="Seccion.TLabel").pack(side="left")

        self.busqueda = tk.StringVar()
        caja = ttk.Entry(barra, textvariable=self.busqueda, width=28, font=FUENTES["normal"])
        caja.pack(side="right")
        ttk.Label(barra, text="⌕ Buscar:", style="Suave.TLabel").pack(side="right", padx=(0, 6))
        # Cada vez que cambia el texto → buscar.
        self.busqueda.trace_add("write", lambda *_: al_buscar(self.busqueda.get().strip()))

        # --- La tabla ----------------------------------------------------------
        marco = ttk.Frame(self, style="Tarjeta.TFrame")
        marco.pack(fill="both", expand=True)

        self.arbol = ttk.Treeview(marco, columns=[c[0] for c in COLUMNAS],
                                  show="headings", selectmode="browse")
        for clave, titulo, ancho, alineacion in COLUMNAS:
            self.arbol.heading(clave, text=titulo)
            self.arbol.column(clave, width=ancho, anchor=alineacion, minwidth=40)

        # Filas «cebra» (una sí, una no) para leer mejor.
        self.arbol.tag_configure("par", background="#F6F8FC")

        desplazador = ttk.Scrollbar(marco, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=desplazador.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        desplazador.pack(side="right", fill="y")

        self.arbol.bind("<<TreeviewSelect>>", self._cuando_seleccionan)

        # Mensaje para cuando la búsqueda no encuentra nada.
        self.vacio = tk.Label(self.arbol, text="No hay estudiantes que coincidan.",
                              font=FUENTES["normal"], foreground=COLORES["texto_suave"],
                              background="white")

    # -----------------------------------------------------------------------
    def mostrar(self, estudiantes: list) -> None:
        """Borra la tabla y la vuelve a llenar con la lista recibida."""
        self.arbol.delete(*self.arbol.get_children())
        for posicion, estudiante in enumerate(estudiantes):
            etiquetas = ("par",) if posicion % 2 else ()
            self.arbol.insert("", "end", iid=str(estudiante.id),
                              values=estudiante.como_tupla_tabla(), tags=etiquetas)

        if estudiantes:
            self.vacio.place_forget()
        else:
            self.vacio.place(relx=0.5, rely=0.5, anchor="center")

    def destellar(self, id_estudiante: int, color: str) -> None:
        """Resalta una fila (la recién creada o editada) y la hace visible."""
        iid = str(id_estudiante)
        if self.arbol.exists(iid):
            self.arbol.see(iid)
            destellar_fila(self.arbol, iid, color)

    def quitar_seleccion(self) -> None:
        self.arbol.selection_remove(*self.arbol.selection())

    def _cuando_seleccionan(self, _evento) -> None:
        seleccion = self.arbol.selection()
        if seleccion:
            self._al_seleccionar(int(seleccion[0]))
