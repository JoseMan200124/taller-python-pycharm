"""
base_datos.py — La única puerta de entrada a SQLite.
=====================================================

¿Qué es SQLite?
    Una base de datos completa que vive en UN SOLO ARCHIVO (taller.db).
    No hay que instalar un servidor: Python ya trae el módulo `sqlite3`.

¿Por qué una clase aparte?
    Porque así ningún otro archivo «habla» directo con SQLite.
    Si mañana cambiamos a MySQL o PostgreSQL, solo se toca este archivo.

    Ventana  ──►  Repositorio  ──►  BaseDatos  ──►  taller.db
    (botones)     (CRUD)            (SQL)           (archivo)

Truco didáctico — los «oyentes»:
    Cada vez que se ejecuta una sentencia SQL, la clase avisa a quien
    esté escuchando (por ejemplo, la Consola SQL de la ventana).
    Así los alumnos VEN en vivo el SQL que provoca cada botón.
"""

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from configuracion import RUTA_BD

# ---------------------------------------------------------------------------
# 🧱 Estructura de la tabla
# ---------------------------------------------------------------------------
# CREATE TABLE IF NOT EXISTS → solo la crea la primera vez.
#   PRIMARY KEY AUTOINCREMENT → SQLite pone el id solito (1, 2, 3...).
#   NOT NULL                  → el campo es obligatorio.
#   UNIQUE                    → no puede haber dos correos iguales.
#   CHECK                     → regla que la BD vigila por su cuenta.
#   DEFAULT                   → valor automático si no mandamos nada.
SQL_CREAR_TABLA = """
CREATE TABLE IF NOT EXISTS estudiantes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT    NOT NULL,
    correo    TEXT    NOT NULL UNIQUE,
    telefono  TEXT,
    edad      INTEGER CHECK (edad BETWEEN 10 AND 120),
    carrera   TEXT    NOT NULL,
    creado_en TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
)
"""


class BaseDatos:
    """Envuelve la conexión a SQLite y registra cada sentencia ejecutada."""

    def __init__(self, ruta: Path | str = RUTA_BD):
        # ":memory:" crea una BD temporal en RAM (la usan las pruebas).
        self.ruta = str(ruta)

        # 1) Abrir (o crear) el archivo de la base de datos.
        self.conexion = sqlite3.connect(self.ruta)

        # 2) row_factory = sqlite3.Row → cada fila se puede leer por nombre:
        #    fila["nombre"] en lugar de fila[1]. ¡Mucho más legible!
        self.conexion.row_factory = sqlite3.Row

        # 3) Lista de funciones que quieren enterarse de cada SQL.
        self._oyentes = []
        self._motivo = None   # etiqueta opcional, ej. "refresco" (ver más abajo)

        # 4) Asegurar que la tabla exista.
        self.conexion.execute(SQL_CREAR_TABLA)
        self.conexion.commit()

    # -----------------------------------------------------------------------
    # 👂 Oyentes (patrón «observador»)
    # -----------------------------------------------------------------------
    def agregar_oyente(self, funcion) -> None:
        """Registra una función que recibirá un dict con los detalles de cada SQL."""
        self._oyentes.append(funcion)

    def _avisar(self, **detalle) -> None:
        detalle["motivo"] = self._motivo
        for funcion in self._oyentes:
            funcion(detalle)

    @contextmanager
    def motivo(self, nombre: str):
        """
        Marca las sentencias de un bloque con un «motivo». Ejemplo:

            with bd.motivo("refresco"):
                repo.listar()      # la consola lo mostrará en una sola línea tenue

        Así la consola distingue el SQL que pidió el usuario del SQL que la
        app ejecuta por su cuenta para volver a pintar la tabla.
        """
        anterior, self._motivo = self._motivo, nombre
        try:
            yield
        finally:
            self._motivo = anterior

    # -----------------------------------------------------------------------
    # ✍️ Sentencias que MODIFICAN datos: INSERT, UPDATE, DELETE
    # -----------------------------------------------------------------------
    def ejecutar(self, sql: str, parametros: tuple = ()) -> sqlite3.Cursor:
        """
        Ejecuta una sentencia que cambia datos y la confirma (commit).

        `with self.conexion:` es una «transacción»:
            ✔ si todo sale bien → COMMIT  (se guarda en el archivo)
            ✘ si algo falla     → ROLLBACK (se deshace, la BD queda intacta)
        """
        inicio = time.perf_counter()
        try:
            with self.conexion:
                cursor = self.conexion.execute(sql, parametros)
        except sqlite3.Error as error:
            self._avisar(sql=sql, parametros=parametros, filas=0,
                         ms=self._ms_desde(inicio), error=str(error))
            raise  # se vuelve a lanzar para que la ventana muestre el mensaje

        self._avisar(sql=sql, parametros=parametros, filas=cursor.rowcount,
                     ms=self._ms_desde(inicio), error=None)
        return cursor

    # -----------------------------------------------------------------------
    # 🔎 Sentencias que solo LEEN datos: SELECT
    # -----------------------------------------------------------------------
    def consultar(self, sql: str, parametros: tuple = ()) -> list[sqlite3.Row]:
        """Ejecuta un SELECT y devuelve todas las filas encontradas."""
        inicio = time.perf_counter()
        filas = self.conexion.execute(sql, parametros).fetchall()
        self._avisar(sql=sql, parametros=parametros, filas=len(filas),
                     ms=self._ms_desde(inicio), error=None)
        return filas

    # -----------------------------------------------------------------------
    def cerrar(self) -> None:
        """Cierra la conexión. Se llama al cerrar la ventana."""
        self.conexion.close()

    @staticmethod
    def _ms_desde(inicio: float) -> float:
        return (time.perf_counter() - inicio) * 1000
