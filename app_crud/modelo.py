"""
modelo.py — ¿Qué ES un estudiante para nuestro programa?
=========================================================

Una `dataclass` es una clase que solo guarda datos.
Python escribe por nosotros el constructor (__init__) y la forma
de imprimirla (__repr__). Menos código, menos errores.

    Fila de la tabla (SQLite)          Objeto de Python
    ┌────┬────────┬───────────┐        Estudiante(
    │ id │ nombre │ correo ...│  ───►     id=1, nombre="Ana", ...
    └────┴────────┴───────────┘        )
"""

from dataclasses import dataclass
import sqlite3


@dataclass
class Estudiante:
    nombre: str
    correo: str
    telefono: str
    edad: int
    carrera: str
    # Estos dos los pone SQLite, por eso empiezan vacíos (None).
    id: int | None = None
    creado_en: str | None = None

    @classmethod
    def desde_fila(cls, fila: sqlite3.Row) -> "Estudiante":
        """Convierte una fila de SQLite en un objeto Estudiante."""
        return cls(
            id=fila["id"],
            nombre=fila["nombre"],
            correo=fila["correo"],
            telefono=fila["telefono"] or "",
            edad=fila["edad"],
            carrera=fila["carrera"],
            creado_en=fila["creado_en"],
        )

    def como_tupla_tabla(self) -> tuple:
        """Valores en el orden en que se muestran en la tabla de la ventana."""
        return (self.id, self.nombre, self.correo, self.telefono, self.edad, self.carrera)
