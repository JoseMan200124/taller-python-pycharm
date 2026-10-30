"""Ejemplo corto de la lección 05 — funciones + SQLite + por qué usamos ?."""
import sqlite3


def conectar():
    conexion = sqlite3.connect(":memory:")       # en la lección: "leccion05.db"
    conexion.row_factory = sqlite3.Row           # fila["nombre"] en vez de fila[1]
    conexion.execute("""CREATE TABLE estudiantes (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE)""")
    return conexion


def crear(conexion, nombre, correo):
    with conexion:                               # bien → COMMIT · error → ROLLBACK
        cursor = conexion.execute(
            "INSERT INTO estudiantes (nombre, correo) VALUES (?, ?)", (nombre, correo))
    return cursor.lastrowid


def listar(conexion, texto=""):
    return conexion.execute(
        "SELECT * FROM estudiantes WHERE nombre LIKE ?", (f"%{texto}%",)).fetchall()


conexion = conectar()
crear(conexion, "Ana", "ana@correo.com")
crear(conexion, "Carlos", "carlos@correo.com")
try:
    crear(conexion, "Otra Ana", "ana@correo.com")   # correo repetido
except sqlite3.IntegrityError as error:
    print("SQLite dijo que no:", error)

for fila in listar(conexion, "an"):
    print(fila["id"], fila["nombre"])

# Inyección SQL: el texto del usuario NUNCA se pega dentro del SQL
truco = "' OR '1'='1"
peligroso = conexion.execute(f"SELECT * FROM estudiantes WHERE nombre = '{truco}'").fetchall()
seguro = conexion.execute("SELECT * FROM estudiantes WHERE nombre = ?", (truco,)).fetchall()
print("Con f-string:", len(peligroso), "filas · con ?:", len(seguro), "filas")
