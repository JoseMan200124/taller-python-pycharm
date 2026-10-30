"""
formulario.py — Donde el usuario ESCRIBE los datos.
====================================================

Conceptos de tkinter que aparecen aquí:
    • StringVar  → una «cajita» que guarda el texto de un campo.
                   Si cambia la variable, cambia el campo (y al revés).
    • grid()     → acomoda los widgets en filas y columnas, como Excel.
    • command=   → qué función se llama al hacer clic en un botón.

El formulario NO sabe nada de SQL. Solo junta los textos y avisa
a la ventana principal: «quieren crear», «quieren actualizar»...
(eso se llama «separación de responsabilidades»).
"""

import tkinter as tk
from tkinter import ttk

from configuracion import CARRERAS, COLORES
from interfaz.estilos import FUENTES

# (clave interna, etiqueta visible, pista de ejemplo, fila, columna, columnas que ocupa)
# Teléfono y Edad comparten fila para que el formulario quepa en pantallas bajas.
CAMPOS = [
    ("nombre", "Nombre completo", "Ej. Ana Lucía Pérez", 0, 0, 2),
    ("correo", "Correo electrónico", "Ej. ana@correo.com", 1, 0, 2),
    ("telefono", "Teléfono (opcional)", "8 dígitos", 2, 0, 1),
    ("edad", "Edad", "Solo números", 2, 1, 1),
    ("carrera", "Carrera", "Elige de la lista", 3, 0, 2),
]


class Formulario(ttk.Frame):
    def __init__(self, padre: tk.Misc, al_crear, al_actualizar, al_eliminar, al_limpiar):
        super().__init__(padre, style="Tarjeta.TFrame", padding=18)

        # Guardamos las funciones que nos pasó la ventana principal («callbacks»).
        self._al_limpiar = al_limpiar

        self.variables: dict[str, tk.StringVar] = {}
        self.entradas: dict[str, ttk.Widget] = {}
        self.mensajes_error: dict[str, ttk.Label] = {}

        # --- Título dinámico: «Nuevo estudiante» / «Editando #3» ----------------
        self.titulo = ttk.Label(self, text="Nuevo estudiante", style="Seccion.TLabel")
        self.titulo.grid(row=0, column=0, columnspan=2, sticky="w")
        self.pista = ttk.Label(self, text="Llena los campos y pulsa «Crear».", style="Suave.TLabel")
        self.pista.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # --- Un bloque (etiqueta + campo + error) por cada campo ----------------
        # Cada «fila lógica» de CAMPOS usa 3 filas reales de la rejilla:
        #   etiqueta / campo / mensaje.  Por eso: fila_real = 2 + fila * 3
        for clave, etiqueta, ejemplo, fila_logica, columna, ocupa in CAMPOS:
            fila = 2 + fila_logica * 3
            separacion = (0, 0) if ocupa == 2 else ((0, 6) if columna == 0 else (6, 0))
            ubicacion = dict(column=columna, columnspan=ocupa, padx=separacion)

            ttk.Label(self, text=etiqueta).grid(row=fila, sticky="w", **ubicacion)
            variable = tk.StringVar()

            if clave == "carrera":
                # Combobox = lista desplegable. state="readonly" → no se puede escribir.
                entrada = ttk.Combobox(self, textvariable=variable, values=CARRERAS,
                                       state="readonly", font=FUENTES["normal"])
            else:
                entrada = ttk.Entry(self, textvariable=variable, font=FUENTES["normal"])

            entrada.grid(row=fila + 1, sticky="ew", pady=(2, 0), **ubicacion)
            error = ttk.Label(self, text=ejemplo, style="Suave.TLabel")
            error.grid(row=fila + 2, sticky="w", pady=(0, 6), **ubicacion)

            # Al escribir en un campo con error, el rojo desaparece.
            variable.trace_add("write", lambda *_, c=clave: self._quitar_error(c))

            self.variables[clave] = variable
            self.entradas[clave] = entrada
            self.mensajes_error[clave] = error

        self._ejemplos = {clave: ejemplo for clave, _, ejemplo, *_ in CAMPOS}
        # Las dos columnas se estiran por igual a lo ancho.
        self.columnconfigure(0, weight=1, uniform="campos")
        self.columnconfigure(1, weight=1, uniform="campos")

        # --- Botones ------------------------------------------------------------
        botones = ttk.Frame(self, style="Tarjeta.TFrame")
        botones.grid(row=99, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        for columna in range(2):
            botones.columnconfigure(columna, weight=1)

        self.boton_crear = ttk.Button(botones, text="+  Crear", style="Crear.TButton", command=al_crear)
        self.boton_actualizar = ttk.Button(botones, text="✎  Actualizar", style="Actualizar.TButton",
                                           command=al_actualizar)
        self.boton_eliminar = ttk.Button(botones, text="✕  Eliminar", style="Eliminar.TButton",
                                         command=al_eliminar)
        self.boton_limpiar = ttk.Button(botones, text="Limpiar", style="Limpiar.TButton",
                                        command=al_limpiar)

        self.boton_crear.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))
        self.boton_actualizar.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=(0, 6))
        self.boton_eliminar.grid(row=1, column=0, sticky="ew", padx=(0, 4))
        self.boton_limpiar.grid(row=1, column=1, sticky="ew", padx=(4, 0))

        self.modo_nuevo()

    # -----------------------------------------------------------------------
    # 📤 Leer y escribir los campos
    # -----------------------------------------------------------------------
    def leer(self) -> dict:
        """Devuelve {'nombre': '...', 'correo': '...', ...} con lo escrito."""
        return {clave: variable.get() for clave, variable in self.variables.items()}

    def cargar(self, estudiante) -> None:
        """Llena el formulario con un estudiante elegido en la tabla."""
        self.variables["nombre"].set(estudiante.nombre)
        self.variables["correo"].set(estudiante.correo)
        self.variables["telefono"].set(estudiante.telefono)
        self.variables["edad"].set(str(estudiante.edad))
        self.variables["carrera"].set(estudiante.carrera)
        self.modo_edicion(estudiante.id)

    def vaciar(self) -> None:
        for variable in self.variables.values():
            variable.set("")
        self.modo_nuevo()
        self.entradas["nombre"].focus_set()

    # -----------------------------------------------------------------------
    # 🔀 Modos: ¿estamos creando o editando?
    # -----------------------------------------------------------------------
    def modo_nuevo(self) -> None:
        self.titulo.configure(text="Nuevo estudiante", foreground=COLORES["texto"])
        self.pista.configure(text="Llena los campos y pulsa «Crear».")
        self.boton_crear.state(["!disabled"])
        self.boton_actualizar.state(["disabled"])
        self.boton_eliminar.state(["disabled"])

    def modo_edicion(self, id_estudiante: int) -> None:
        self.titulo.configure(text=f"Editando al estudiante #{id_estudiante}",
                              foreground=COLORES["actualizar"])
        self.pista.configure(text="Cambia lo que quieras y pulsa «Actualizar».")
        self.boton_crear.state(["disabled"])
        self.boton_actualizar.state(["!disabled"])
        self.boton_eliminar.state(["!disabled"])

    # -----------------------------------------------------------------------
    # 🟥 Errores de validación
    # -----------------------------------------------------------------------
    def mostrar_errores(self, errores: dict) -> None:
        for clave, mensaje in errores.items():
            estilo = "Error.TCombobox" if clave == "carrera" else "Error.TEntry"
            self.entradas[clave].configure(style=estilo)
            self.mensajes_error[clave].configure(text="⚠ " + mensaje, style="Error.TLabel")
        # Llevamos el cursor al primer campo con error.
        primera = next(campo[0] for campo in CAMPOS if campo[0] in errores)
        self.entradas[primera].focus_set()

    def _quitar_error(self, clave: str) -> None:
        estilo = "TCombobox" if clave == "carrera" else "TEntry"
        self.entradas[clave].configure(style=estilo)
        self.mensajes_error[clave].configure(text=self._ejemplos[clave], style="Suave.TLabel")
