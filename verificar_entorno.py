"""
verificar_entorno.py — ¿Mi computadora está lista para el taller? ✅
===================================================================

▶ Ejecuta este archivo ANTES del taller (clic derecho → Run).
  Revisa Python, SQLite y tkinter, y abre una ventanita de prueba.

  Si todo sale en verde, ¡estás listo! Si algo sale en rojo, lee la
  sugerencia que aparece al lado o revisa docs/INSTALACION.md.
"""

import platform
import sys

VERDE, ROJO, NORMAL = "\033[92m", "\033[91m", "\033[0m"
todo_bien = True


def revisar(nombre: str, ok: bool, detalle: str, sugerencia: str = "") -> None:
    global todo_bien
    marca = f"{VERDE}✔{NORMAL}" if ok else f"{ROJO}✘{NORMAL}"
    print(f"  {marca} {nombre:<12} {detalle}")
    if not ok:
        todo_bien = False
        print(f"      → {sugerencia}")


print("\n  Verificando tu entorno para el taller...\n")

# 1. Versión de Python (necesitamos 3.10 o más nueva)
version = sys.version_info
revisar("Python", version >= (3, 10),
        f"{version.major}.{version.minor}.{version.micro} ({platform.system()})",
        "Instala Python 3.12 desde https://www.python.org/downloads/")

# 2. SQLite
try:
    import sqlite3
    revisar("SQLite", True, f"versión {sqlite3.sqlite_version}")
except ImportError:
    revisar("SQLite", False, "no encontrado", "Reinstala Python desde python.org")

# 3. tkinter
try:
    import tkinter as tk
    revisar("tkinter", True, f"Tk {tk.TkVersion}")
except ImportError:
    tk = None
    revisar("tkinter", False, "no encontrado",
            "Linux: sudo apt install python3-tk · Windows/macOS: reinstala desde python.org")

print()
if not todo_bien:
    print(f"  {ROJO}Hay algo pendiente. Corrígelo y vuelve a ejecutar este archivo.{NORMAL}\n")
    sys.exit(1)

print(f"  {VERDE}¡Todo listo! Se abrirá una ventanita de prueba...{NORMAL}\n")

# 4. Ventana de prueba: si la ves, tkinter funciona de verdad.
ventana = tk.Tk()
ventana.title("¡Listo para el taller!")
ventana.geometry("380x170")
ventana.configure(background="#1F3A68")
tk.Label(ventana, text="✔  Tu computadora está lista", font=("Arial", 15, "bold"),
         foreground="#FFD43B", background="#1F3A68").pack(pady=(34, 8))
tk.Label(ventana, text="Python + SQLite + tkinter funcionando", font=("Arial", 11),
         foreground="white", background="#1F3A68").pack()
tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=16)
ventana.mainloop()
