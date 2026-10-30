"""
validaciones.py — «Nunca confíes en lo que escribe el usuario».
================================================================

Antes de guardar, revisamos cada campo. Si algo está mal devolvemos
un diccionario  {campo: "mensaje de error"}  para pintar en rojo
exactamente el campo que falló.

    formulario ──► validar_estudiante() ──► ¿errores?
                                              ├─ sí → se muestran en rojo
                                              └─ no → se arma el Estudiante
"""

import re

from configuracion import CARRERAS
from modelo import Estudiante

# Expresión regular sencilla para un correo:  algo@algo.algo
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def validar_estudiante(datos: dict) -> tuple[Estudiante | None, dict]:
    """
    Recibe los textos del formulario y devuelve (estudiante, errores).

    - Si no hay errores → (Estudiante(...), {})
    - Si hay errores    → (None, {"correo": "Correo no válido", ...})
    """
    errores = {}

    # .strip() quita espacios al inicio y al final: "  Ana  " → "Ana"
    nombre = datos.get("nombre", "").strip()
    correo = datos.get("correo", "").strip().lower()
    telefono = datos.get("telefono", "").strip().replace("-", "").replace(" ", "")
    edad_texto = datos.get("edad", "").strip()
    carrera = datos.get("carrera", "").strip()

    # --- Nombre --------------------------------------------------------------
    if len(nombre) < 3:
        errores["nombre"] = "Escribe al menos 3 letras."

    # --- Correo --------------------------------------------------------------
    if not PATRON_CORREO.match(correo):
        errores["correo"] = "Ejemplo válido: ana@correo.com"

    # --- Teléfono (opcional, 8 dígitos como en Guatemala) --------------------
    if telefono and not (telefono.isdigit() and len(telefono) == 8):
        errores["telefono"] = "Deben ser 8 dígitos, ej. 5555 1234."

    # --- Edad: texto → número entero -----------------------------------------
    # int("abc") lanza ValueError; lo atrapamos con try/except.
    edad = 0
    try:
        edad = int(edad_texto)
        if not 10 <= edad <= 120:
            errores["edad"] = "La edad debe estar entre 10 y 120."
    except ValueError:
        errores["edad"] = "Escribe la edad con números."

    # --- Carrera -------------------------------------------------------------
    if carrera not in CARRERAS:
        errores["carrera"] = "Elige una carrera de la lista."

    if errores:
        return None, errores

    if telefono:  # lo guardamos con formato bonito: 5555-1234
        telefono = f"{telefono[:4]}-{telefono[4:]}"

    return Estudiante(nombre=nombre, correo=correo, telefono=telefono,
                      edad=edad, carrera=carrera), {}
