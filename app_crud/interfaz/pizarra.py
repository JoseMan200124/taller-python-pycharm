"""
pizarra.py — «¿Qué acaba de pasar?» explicado en español sencillo.
===================================================================

Después de cada operación, la pizarra cuenta el viaje del dato:

    Ventana  →  función de Python  →  SQL  →  SQLite  →  resultado

Y lo escribe letra por letra (efecto máquina de escribir) para que el
grupo lo lea mientras el instructor lo explica en voz alta.
"""

import tkinter as tk
from tkinter import ttk

from configuracion import COLORES, OPERACIONES, VELOCIDAD_ESCRITURA
from interfaz.animaciones import MaquinaDeEscribir
from interfaz.estilos import FUENTES


class Pizarra(ttk.Frame):
    def __init__(self, padre: tk.Misc):
        super().__init__(padre, style="Tarjeta.TFrame", padding=18)

        ttk.Label(self, text="¿Qué acaba de pasar?", style="Seccion.TLabel").pack(anchor="w")

        # Franja de color que cambia según la operación.
        self.franja = tk.Frame(self, height=4, background=COLORES["borde"])
        self.franja.pack(fill="x", pady=(6, 10))

        self.caja = tk.Text(self, width=30, height=7, wrap="word", font=FUENTES["pizarra"],
                            background=COLORES["tarjeta"], foreground=COLORES["texto"],
                            relief="flat", borderwidth=0, highlightthickness=0, cursor="arrow")
        self.caja.pack(fill="both", expand=True)

        self.caja.tag_configure("normal")
        self.caja.tag_configure("codigo", font=FUENTES["codigo_negrita"], foreground=COLORES["encabezado"],
                                background="#EDF2FB")
        self.caja.tag_configure("suave", foreground=COLORES["texto_suave"])
        self.caja.tag_configure("error", foreground=COLORES["error"], font=FUENTES["seccion"])
        for operacion, info in OPERACIONES.items():
            self.caja.tag_configure(operacion, foreground=info["color"], font=FUENTES["seccion"])

        self.maquina = MaquinaDeEscribir(self.caja, VELOCIDAD_ESCRITURA)

    # -----------------------------------------------------------------------
    def explicar(self, operacion: str, partes: list[tuple[str, str]]) -> None:
        """
        operacion: 'INSERT', 'SELECT', 'UPDATE', 'DELETE' o 'ERROR'.
        partes:    [(texto, estilo), ...]  estilos: normal, codigo, suave, error.
        """
        color = OPERACIONES[operacion]["color"] if operacion in OPERACIONES else COLORES["error"]
        self.franja.configure(background=color)
        self.maquina.escribir(partes)

    # -----------------------------------------------------------------------
    # 📚 Guiones: una explicación preparada para cada operación
    # -----------------------------------------------------------------------
    def explicar_crear(self, estudiante, nuevo_id: int) -> None:
        self.explicar("INSERT", [
            ("C · CREATE\n", "INSERT"),
            ("1. Pulsaste «Crear». La ventana leyó los campos y llamó a ", "normal"),
            ("validar_estudiante()", "codigo"), (".\n", "normal"),
            ("2. Todo estaba bien, así que se llamó a ", "normal"),
            ("repo.crear(estudiante)", "codigo"), (".\n", "normal"),
            ("3. Python envió un ", "normal"), ("INSERT", "codigo"), (" a SQLite.\n", "normal"),
            (f"4. SQLite guardó a «{estudiante.nombre}» y le asignó el id ", "normal"),
            (f"#{nuevo_id}", "codigo"), (" por su cuenta (AUTOINCREMENT).", "normal"),
        ])

    def explicar_leer(self, estudiante) -> None:
        self.explicar("SELECT", [
            ("R · READ\n", "SELECT"),
            ("Hiciste clic en una fila. Se llamó a ", "normal"),
            (f"repo.obtener({estudiante.id})", "codigo"), (", que ejecutó:\n", "normal"),
            (f"SELECT * FROM estudiantes WHERE id = {estudiante.id}", "codigo"), ("\n", "normal"),
            ("Los datos viajaron de vuelta al formulario. Leer ", "normal"),
            ("no cambia nada", "SELECT"), (" en la base de datos.", "normal"),
        ])

    def explicar_busqueda(self, texto: str, encontrados: int) -> None:
        self.explicar("SELECT", [
            ("R · READ (búsqueda)\n", "SELECT"),
            ("Cada letra que escribes ejecuta un SELECT con ", "normal"), ("LIKE", "codigo"), (":\n", "normal"),
            (f"... WHERE nombre LIKE '%{texto}%'", "codigo"), ("\n", "normal"),
            (f"El % significa «lo que sea». Coincidencias: {encontrados}.", "normal"),
        ])

    def explicar_actualizar(self, estudiante, cambios: list[str]) -> None:
        detalle = ", ".join(cambios) if cambios else "ningún campo (los datos ya eran iguales)"
        self.explicar("UPDATE", [
            ("U · UPDATE\n", "UPDATE"),
            ("Se llamó a ", "normal"), ("repo.actualizar(estudiante)", "codigo"), (".\n", "normal"),
            (f"Cambiaste: {detalle}.\n", "normal"),
            ("La clave es el ", "normal"), (f"WHERE id = {estudiante.id}", "codigo"),
            (": sin él, SQLite cambiaría a TODOS los estudiantes.", "normal"),
        ])

    def explicar_eliminar(self, nombre: str, id_estudiante: int) -> None:
        self.explicar("DELETE", [
            ("D · DELETE\n", "DELETE"),
            ("Confirmaste y se llamó a ", "normal"), (f"repo.eliminar({id_estudiante})", "codigo"), (".\n", "normal"),
            (f"«{nombre}» ya no existe en el archivo taller.db. ", "normal"),
            ("No hay papelera: DELETE es definitivo.\n", "normal"),
            ("Observa que el id ", "suave"), (f"#{id_estudiante}", "codigo"),
            (" no se vuelve a usar.", "suave"),
        ])

    def explicar_error(self, titulo: str, mensaje: str) -> None:
        self.explicar("ERROR", [(f"{titulo}\n", "error"), (mensaje, "normal")])

    def bienvenida(self, total: int) -> None:
        self.explicar("SELECT", [
            ("¡Bienvenido!\n", "SELECT"),
            ("Al abrir, la app ejecutó ", "normal"), ("repo.listar()", "codigo"),
            (f" y encontró {total} estudiantes en taller.db.\n", "normal"),
            ("Prueba los botones y mira abajo la ", "normal"), ("Consola SQL", "codigo"),
            (": verás el SQL exacto de cada acción. En el ", "normal"), ("Visor de código", "codigo"),
            (" (F2) brilla cada línea de Python que se ejecuta.", "normal"),
        ])
