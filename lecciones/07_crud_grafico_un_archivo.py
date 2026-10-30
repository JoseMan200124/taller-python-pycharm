"""
LECCIÓN 07 — CRUD con ventana + SQLite, ¡todo en UN archivo! 🖥️💾
==================================================================
⏱ 35 minutos

Objetivo: juntar la ventana (lección 06) con el CRUD en SQLite (lección 05).
Es el corazón del taller: ~150 líneas que hacen un sistema completo.

Mapa de la ventana:
    ┌───────────────────────────────────────────────────────────┐
    │ Nombre [__________]  Correo [__________]  Edad [___]      │  ← formulario
    │ [Crear] [Actualizar] [Eliminar] [Limpiar]                 │  ← botones
    │ ┌────┬──────────────┬────────────────────┬──────┐         │
    │ │ ID │ Nombre       │ Correo             │ Edad │         │  ← tabla (Treeview)
    │ ├────┼──────────────┼────────────────────┼──────┤         │
    │ │ 1  │ Ana Pérez    │ ana@correo.com     │ 21   │ ◄── clic: carga en el formulario
    │ └────┴──────────────┴────────────────────┴──────┘         │
    └───────────────────────────────────────────────────────────┘

El ciclo de cada botón:
    clic → leer campos → validar → SQL → commit → recargar tabla

👉 Cuando esto funcione, abre la carpeta  app_crud/ : es ESTE MISMO
   programa, pero ordenado en varios archivos, con animaciones y
   una consola que muestra el SQL en vivo.
"""

import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

RUTA_BD = Path(__file__).parent / "leccion07.db"

# ═════════════════════════════════════════════════════════════════════════════
# 1. BASE DE DATOS
# ═════════════════════════════════════════════════════════════════════════════
conexion = sqlite3.connect(RUTA_BD)
conexion.execute("""
    CREATE TABLE IF NOT EXISTS estudiantes (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        edad   INTEGER
    )
""")

# ═════════════════════════════════════════════════════════════════════════════
# 2. VENTANA Y VARIABLES
# ═════════════════════════════════════════════════════════════════════════════
ventana = tk.Tk()
ventana.title("CRUD de Estudiantes — Lección 07")
ventana.geometry("760x480")
ventana.configure(padx=16, pady=16)

var_nombre = tk.StringVar()
var_correo = tk.StringVar()
var_edad = tk.StringVar()
id_seleccionado = None   # None = estamos creando; un número = estamos editando


# ═════════════════════════════════════════════════════════════════════════════
# 3. FUNCIONES DE APOYO
# ═════════════════════════════════════════════════════════════════════════════
def leer_formulario():
    """Devuelve (nombre, correo, edad) validados, o None si algo está mal."""
    nombre = var_nombre.get().strip()
    correo = var_correo.get().strip().lower()
    try:
        edad = int(var_edad.get())
    except ValueError:
        messagebox.showwarning("Dato inválido", "La edad debe ser un número.")
        return None
    if not nombre or "@" not in correo:
        messagebox.showwarning("Dato inválido", "Escribe un nombre y un correo válido.")
        return None
    return nombre, correo, edad


def cargar_tabla():
    """R — Borra la tabla de la ventana y la vuelve a llenar desde SQLite."""
    tabla.delete(*tabla.get_children())          # * «desempaca» la lista de filas
    for fila in conexion.execute("SELECT id, nombre, correo, edad FROM estudiantes ORDER BY id"):
        tabla.insert("", "end", values=fila)
    etiqueta_total.configure(text=f"Total: {len(tabla.get_children())} estudiantes")


def limpiar():
    global id_seleccionado
    id_seleccionado = None
    for variable in (var_nombre, var_correo, var_edad):
        variable.set("")
    tabla.selection_remove(*tabla.selection())
    boton_crear.state(["!disabled"])             # habilitar Crear
    boton_actualizar.state(["disabled"])         # deshabilitar Actualizar
    boton_eliminar.state(["disabled"])
    caja_nombre.focus_set()


# ═════════════════════════════════════════════════════════════════════════════
# 4. LAS CUATRO OPERACIONES DEL CRUD
# ═════════════════════════════════════════════════════════════════════════════
def crear():                                                        # C
    datos = leer_formulario()
    if datos is None:
        return
    try:
        with conexion:
            conexion.execute("INSERT INTO estudiantes (nombre, correo, edad) VALUES (?, ?, ?)", datos)
    except sqlite3.IntegrityError:
        messagebox.showerror("Correo repetido", "Ya existe un estudiante con ese correo.")
        return
    cargar_tabla()
    limpiar()


def seleccionar(_evento):                                           # R (uno)
    """Al hacer clic en una fila, sus datos pasan al formulario."""
    global id_seleccionado
    seleccion = tabla.selection()
    if not seleccion:
        return
    id_, nombre, correo, edad = tabla.item(seleccion[0], "values")
    id_seleccionado = int(id_)
    var_nombre.set(nombre)
    var_correo.set(correo)
    var_edad.set(edad)
    boton_crear.state(["disabled"])
    boton_actualizar.state(["!disabled"])
    boton_eliminar.state(["!disabled"])


def actualizar():                                                   # U
    datos = leer_formulario()
    if datos is None or id_seleccionado is None:
        return
    try:
        with conexion:
            conexion.execute("UPDATE estudiantes SET nombre = ?, correo = ?, edad = ? WHERE id = ?",
                             (*datos, id_seleccionado))
    except sqlite3.IntegrityError:
        messagebox.showerror("Correo repetido", "Otro estudiante ya usa ese correo.")
        return
    cargar_tabla()
    limpiar()


def eliminar():                                                     # D
    if id_seleccionado is None:
        return
    if messagebox.askyesno("Confirmar", f"¿Eliminar al estudiante #{id_seleccionado}?"):
        with conexion:
            conexion.execute("DELETE FROM estudiantes WHERE id = ?", (id_seleccionado,))
        cargar_tabla()
        limpiar()


# ═════════════════════════════════════════════════════════════════════════════
# 5. CONSTRUIR LA INTERFAZ
# ═════════════════════════════════════════════════════════════════════════════
# --- Formulario (fila de campos) ---------------------------------------------
formulario = ttk.Frame(ventana)
formulario.pack(fill="x")

ttk.Label(formulario, text="Nombre").grid(row=0, column=0, sticky="w")
caja_nombre = ttk.Entry(formulario, textvariable=var_nombre, width=26)
caja_nombre.grid(row=1, column=0, padx=(0, 10))

ttk.Label(formulario, text="Correo").grid(row=0, column=1, sticky="w")
ttk.Entry(formulario, textvariable=var_correo, width=30).grid(row=1, column=1, padx=(0, 10))

ttk.Label(formulario, text="Edad").grid(row=0, column=2, sticky="w")
ttk.Entry(formulario, textvariable=var_edad, width=8).grid(row=1, column=2)

# --- Botones ------------------------------------------------------------------
botones = ttk.Frame(ventana)
botones.pack(fill="x", pady=12)
boton_crear = ttk.Button(botones, text="Crear", command=crear)
boton_actualizar = ttk.Button(botones, text="Actualizar", command=actualizar)
boton_eliminar = ttk.Button(botones, text="Eliminar", command=eliminar)
for boton in (boton_crear, boton_actualizar, boton_eliminar):
    boton.pack(side="left", padx=(0, 6))
ttk.Button(botones, text="Limpiar", command=limpiar).pack(side="left")

# --- Tabla --------------------------------------------------------------------
columnas = ("id", "nombre", "correo", "edad")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings", selectmode="browse")
for columna, titulo, ancho in zip(columnas, ("ID", "Nombre", "Correo", "Edad"), (50, 220, 280, 70)):
    tabla.heading(columna, text=titulo)
    tabla.column(columna, width=ancho)
tabla.pack(fill="both", expand=True)
tabla.bind("<<TreeviewSelect>>", seleccionar)   # evento: cambió la fila seleccionada

etiqueta_total = ttk.Label(ventana, text="")
etiqueta_total.pack(anchor="w", pady=(8, 0))

# ═════════════════════════════════════════════════════════════════════════════
# 6. ARRANCAR
# ═════════════════════════════════════════════════════════════════════════════
cargar_tabla()
limpiar()


def al_cerrar():
    conexion.close()
    ventana.destroy()


ventana.protocol("WM_DELETE_WINDOW", al_cerrar)
ventana.mainloop()

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 RETOS
#   1. (fácil)   Agrega el campo «Carrera» con un ttk.Combobox.
#   2. (medio)   Agrega una caja «Buscar» que filtre con SELECT ... LIKE ?
#   3. (difícil) Ordena la tabla al hacer clic en el título de una columna.
#               Pista: tabla.heading(col, command=lambda: ...)
# ─────────────────────────────────────────────────────────────────────────────
