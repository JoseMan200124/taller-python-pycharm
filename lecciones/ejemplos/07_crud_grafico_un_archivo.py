"""
Ejemplo corto de la lección 07 — CRUD gráfico: ventana + SQLite en un archivo.
En PyCharm se abre la ventana de verdad; en la página web se simulan los clics.
"""
import sqlite3
import tkinter as tk

conexion = sqlite3.connect(":memory:")   # en la lección: "leccion07.db"
conexion.execute("""CREATE TABLE estudiantes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    edad   INTEGER)""")

ventana = tk.Tk()
ventana.title("CRUD de estudiantes")
nombre = tk.StringVar()
edad = tk.StringVar()
mensaje = tk.StringVar(value="Llena los campos y pulsa Crear")


def cargar_tabla():                      # R — leer y mostrar
    tabla.delete(0, tk.END)
    for id_, nom, ed in conexion.execute("SELECT id, nombre, edad FROM estudiantes"):
        tabla.insert(tk.END, f"#{id_}  {nom}, {ed} años")


def crear():                             # C — validar y guardar
    texto = nombre.get().strip()
    if not texto or not edad.get().isdigit():
        mensaje.set("Revisa el nombre y la edad")
        return
    with conexion:
        conexion.execute("INSERT INTO estudiantes (nombre, edad) VALUES (?, ?)",
                         (texto, int(edad.get())))
    mensaje.set(f"{texto} guardado")
    nombre.set("")
    edad.set("")
    cargar_tabla()


tk.Label(ventana, text="Nombre").pack()
tk.Entry(ventana, textvariable=nombre).pack()
tk.Label(ventana, text="Edad").pack()
tk.Entry(ventana, textvariable=edad).pack()
tk.Button(ventana, text="Crear", command=crear).pack()
tk.Label(ventana, textvariable=mensaje).pack()
tabla = tk.Listbox(ventana)
tabla.pack()

ventana.mainloop()
