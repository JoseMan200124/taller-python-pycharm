"""
Ejemplo corto de la lección 06 — primera ventana con tkinter.
En PyCharm se abre la ventana de verdad. En la página web se simula lo que
hace el usuario (escribir y hacer clic) para ver qué código se ejecuta.
"""
import tkinter as tk

ventana = tk.Tk()
ventana.title("Mi primera ventana")

# Variables «enlazadas»: cambian solas cuando el usuario escribe
nombre = tk.StringVar()
mensaje = tk.StringVar(value="Escribe tu nombre")
contador = tk.IntVar(value=0)


def saludar():                       # se ejecuta con cada clic en «Saludar»
    texto = nombre.get().strip()
    if not texto:
        mensaje.set("¡No escribiste nada!")
        return
    contador.set(contador.get() + 1)
    mensaje.set(f"¡Hola, {texto}! (saludo #{contador.get()})")


tk.Label(ventana, text="Nombre:").pack()
tk.Entry(ventana, textvariable=nombre).pack()
tk.Button(ventana, text="Saludar", command=saludar).pack()   # sin paréntesis
tk.Label(ventana, textvariable=mensaje).pack()

ventana.mainloop()   # espera eventos: cada clic llama a saludar()
