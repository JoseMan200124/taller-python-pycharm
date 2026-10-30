"""
LECCIÓN 06 — Nuestra primera ventana con tkinter 🪟
====================================================
⏱ 20 minutos

Objetivo: pasar de la consola negra a una ventana con botones.

tkinter viene incluido con Python (en Linux: sudo apt install python3-tk).

La idea clave: PROGRAMACIÓN POR EVENTOS
    En consola, el programa manda: pregunta, espera, sigue.
    En una ventana, el USUARIO manda: el programa se queda esperando
    (mainloop) y reacciona cuando ocurre un evento (un clic, una tecla).

        ┌──────────────── mainloop() ────────────────┐
        │   espera... ──► ¡clic en «Saludar»! ──►    │
        │                 llama a saludar()          │
        │   espera... ◄────────────────────────────  │
        └────────────────────────────────────────────┘

Widgets (piezas) que usaremos:
    tk.Tk()     → la ventana
    ttk.Label   → texto
    ttk.Entry   → caja para escribir
    ttk.Button  → botón
    .grid()     → acomodar en filas y columnas
"""

import tkinter as tk
from tkinter import ttk

# ─────────────────────────────────────────────────────────────────────────────
# 1. Crear la ventana
# ─────────────────────────────────────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Mi primera ventana")
ventana.geometry("420x260")          # ancho x alto en píxeles
ventana.configure(padx=20, pady=20)  # margen interno

# ─────────────────────────────────────────────────────────────────────────────
# 2. Variables «enlazadas»: StringVar
# ─────────────────────────────────────────────────────────────────────────────
# Una StringVar está conectada al widget: si escribes en la caja,
# la variable cambia sola, y si cambias la variable, cambia la caja.
nombre = tk.StringVar()
mensaje = tk.StringVar(value="Escribe tu nombre y pulsa el botón")
contador = tk.IntVar(value=0)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Funciones que responden a los eventos («callbacks»)
# ─────────────────────────────────────────────────────────────────────────────
def saludar():
    texto = nombre.get().strip()             # .get() lee la variable
    if not texto:
        mensaje.set("⚠ ¡No escribiste nada!")
        etiqueta_mensaje.configure(foreground="#C62828")   # rojo
        return
    contador.set(contador.get() + 1)
    mensaje.set(f"¡Hola, {texto}!  (saludo #{contador.get()})")
    etiqueta_mensaje.configure(foreground="#1E9E5A")       # verde


def limpiar():
    nombre.set("")
    mensaje.set("Escribe tu nombre y pulsa el botón")
    etiqueta_mensaje.configure(foreground="black")
    caja.focus_set()                         # poner el cursor en la caja


# ─────────────────────────────────────────────────────────────────────────────
# 4. Crear los widgets y acomodarlos con grid (como una hoja de Excel)
# ─────────────────────────────────────────────────────────────────────────────
#        columna 0          columna 1
# fila 0 [ Nombre:  ]       [ caja de texto      ]
# fila 1 [ Saludar  ]       [ Limpiar            ]
# fila 2 [ mensaje (ocupa 2 columnas)            ]
# fila 3 [ contador (ocupa 2 columnas)           ]

ttk.Label(ventana, text="Nombre:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")

caja = ttk.Entry(ventana, textvariable=nombre, font=("Arial", 12))
caja.grid(row=0, column=1, sticky="ew", pady=8)

# command=saludar  → ¡SIN paréntesis! Le pasamos la función, no la ejecutamos.
ttk.Button(ventana, text="Saludar", command=saludar).grid(row=1, column=0, sticky="ew", padx=(0, 6))
ttk.Button(ventana, text="Limpiar", command=limpiar).grid(row=1, column=1, sticky="ew")

etiqueta_mensaje = ttk.Label(ventana, textvariable=mensaje, font=("Arial", 12, "bold"))
etiqueta_mensaje.grid(row=2, column=0, columnspan=2, pady=20)

ttk.Label(ventana, text="Saludos dados:").grid(row=3, column=0, sticky="w")
ttk.Label(ventana, textvariable=contador, font=("Arial", 16, "bold")).grid(row=3, column=1, sticky="w")

ventana.columnconfigure(1, weight=1)   # la columna 1 se estira si agrandas la ventana

# Atajo de teclado: Enter también saluda. bind() conecta un evento con una función.
ventana.bind("<Return>", lambda evento: saludar())

caja.focus_set()

# ─────────────────────────────────────────────────────────────────────────────
# 5. ¡Arrancar! mainloop() se queda escuchando eventos hasta cerrar la ventana.
# ─────────────────────────────────────────────────────────────────────────────
ventana.mainloop()

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 RETO (5 min): agrega una caja «Edad» y que el saludo diga
#    «¡Hola, Ana! Tienes 21 años». Si la edad no es número, mensaje en rojo.
#    (Pista: try/except ValueError, igual que en la lección 02.)
# ─────────────────────────────────────────────────────────────────────────────
