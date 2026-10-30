"""
repositorio.py — Aquí vive el CRUD.
====================================

    C  →  crear()        →  INSERT
    R  →  listar()       →  SELECT
          obtener()      →  SELECT ... WHERE id = ?
    U  →  actualizar()   →  UPDATE
    D  →  eliminar()     →  DELETE

⚠️ Regla de oro: NUNCA armar el SQL pegando texto del usuario.

    ❌ MAL:  f"SELECT * FROM estudiantes WHERE nombre = '{nombre}'"
            Si alguien escribe   ' OR '1'='1   ¡ve todos los datos!
            (eso se llama «inyección SQL»).

    ✅ BIEN: "SELECT * FROM estudiantes WHERE nombre = ?"  + (nombre,)
            El signo ? es un «hueco» que SQLite llena de forma segura.
"""

from base_datos import BaseDatos
from modelo import Estudiante


class RepositorioEstudiantes:
    """Todas las operaciones sobre la tabla `estudiantes`."""

    def __init__(self, bd: BaseDatos):
        self.bd = bd

    # -----------------------------------------------------------------------
    # C — CREATE
    # -----------------------------------------------------------------------
    def crear(self, estudiante: Estudiante) -> int:
        """Inserta un estudiante nuevo y devuelve el id que le dio SQLite."""
        cursor = self.bd.ejecutar(
            "INSERT INTO estudiantes (nombre, correo, telefono, edad, carrera) "
            "VALUES (?, ?, ?, ?, ?)",
            (estudiante.nombre, estudiante.correo, estudiante.telefono,
             estudiante.edad, estudiante.carrera),
        )
        return cursor.lastrowid  # el id recién creado

    # -----------------------------------------------------------------------
    # R — READ
    # -----------------------------------------------------------------------
    def listar(self, busqueda: str = "") -> list[Estudiante]:
        """
        Devuelve todos los estudiantes, o solo los que coinciden con `busqueda`.

        LIKE '%ana%' encuentra «Ana», «Mariana», «Ingeniería Ana»...
        El % significa «cualquier cosa antes o después».
        """
        if busqueda:
            patron = f"%{busqueda}%"   # aquí SÍ usamos f-string: es el VALOR, no el SQL
            filas = self.bd.consultar(
                "SELECT * FROM estudiantes "
                "WHERE nombre LIKE ? OR correo LIKE ? OR carrera LIKE ? "
                "ORDER BY id DESC",
                (patron, patron, patron),
            )
        else:
            filas = self.bd.consultar("SELECT * FROM estudiantes ORDER BY id DESC")

        # «List comprehension»: convierte cada fila en un objeto Estudiante.
        return [Estudiante.desde_fila(fila) for fila in filas]

    def obtener(self, id_estudiante: int) -> Estudiante | None:
        """Busca un estudiante por su id. Devuelve None si no existe."""
        filas = self.bd.consultar("SELECT * FROM estudiantes WHERE id = ?", (id_estudiante,))
        return Estudiante.desde_fila(filas[0]) if filas else None

    def contar_por_carrera(self) -> list[tuple[str, int]]:
        """Para el gráfico de barras: [('Agronomía', 4), ('Medicina', 2), ...]."""
        filas = self.bd.consultar(
            "SELECT carrera, COUNT(*) AS total FROM estudiantes "
            "GROUP BY carrera ORDER BY total DESC"
        )
        return [(fila["carrera"], fila["total"]) for fila in filas]

    # -----------------------------------------------------------------------
    # U — UPDATE
    # -----------------------------------------------------------------------
    def actualizar(self, estudiante: Estudiante) -> bool:
        """Guarda los cambios de un estudiante existente. True si se modificó."""
        cursor = self.bd.ejecutar(
            "UPDATE estudiantes "
            "SET nombre = ?, correo = ?, telefono = ?, edad = ?, carrera = ? "
            "WHERE id = ?",   # ⚠️ sin WHERE se modificarían TODAS las filas
            (estudiante.nombre, estudiante.correo, estudiante.telefono,
             estudiante.edad, estudiante.carrera, estudiante.id),
        )
        return cursor.rowcount == 1

    # -----------------------------------------------------------------------
    # D — DELETE
    # -----------------------------------------------------------------------
    def eliminar(self, id_estudiante: int) -> bool:
        """Borra un estudiante por su id. True si se borró."""
        cursor = self.bd.ejecutar(
            "DELETE FROM estudiantes WHERE id = ?",  # ⚠️ sin WHERE se borra TODO
            (id_estudiante,),
        )
        return cursor.rowcount == 1
