"""
LECCIÓN 05 — CRUD completo en consola con SQLite + funciones 🧰
================================================================
⏱ 25 minutos

Objetivo: unir todo lo anterior. El menú de la lección 03, pero ahora
los datos se guardan en SQLite (lección 04) y el código está ordenado
en FUNCIONES, una por operación.

    menú ──► crear()      ──► INSERT
         ──► listar()     ──► SELECT
         ──► actualizar() ──► UPDATE
         ──► eliminar()   ──► DELETE

Novedades:
    • def con parámetros y return
    • with conexion:  → transacción automática (commit o rollback)
    • sqlite3.Row     → leer columnas por nombre: fila["nombre"]
    • 💉 Demostración de INYECCIÓN SQL (y por qué usamos ?)
"""

import sqlite3
from pathlib import Path

# La BD se crea junto a este archivo, sin importar desde dónde se ejecute.
RUTA_BD = Path(__file__).parent / "leccion05.db"


# ═════════════════════════════════════════════════════════════════════════════
# Conexión
# ═════════════════════════════════════════════════════════════════════════════
def conectar() -> sqlite3.Connection:
    """Abre la BD, prepara la tabla y la devuelve lista para usar."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row      # fila["nombre"] en vez de fila[1]
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre  TEXT NOT NULL,
            correo  TEXT NOT NULL UNIQUE,
            edad    INTEGER CHECK (edad BETWEEN 10 AND 120)
        )
    """)
    return conexion


# ═════════════════════════════════════════════════════════════════════════════
# Funciones del CRUD — reciben la conexión y los datos, devuelven un resultado
# ═════════════════════════════════════════════════════════════════════════════
def crear(conexion, nombre: str, correo: str, edad: int) -> int:
    """C — Inserta y devuelve el id nuevo."""
    with conexion:   # ✔ todo bien → COMMIT   ✘ error → ROLLBACK
        cursor = conexion.execute(
            "INSERT INTO estudiantes (nombre, correo, edad) VALUES (?, ?, ?)",
            (nombre, correo, edad),
        )
    return cursor.lastrowid


def listar(conexion, texto: str = "") -> list:
    """R — Todos, o solo los que contienen `texto` en el nombre."""
    return conexion.execute(
        "SELECT * FROM estudiantes WHERE nombre LIKE ? ORDER BY nombre",
        (f"%{texto}%",),
    ).fetchall()


def actualizar(conexion, id_: int, nombre: str, correo: str, edad: int) -> bool:
    """U — Devuelve True si encontró y modificó al estudiante."""
    with conexion:
        cursor = conexion.execute(
            "UPDATE estudiantes SET nombre = ?, correo = ?, edad = ? WHERE id = ?",
            (nombre, correo, edad, id_),
        )
    return cursor.rowcount == 1   # rowcount = cuántas filas se tocaron


def eliminar(conexion, id_: int) -> bool:
    """D — Devuelve True si lo borró."""
    with conexion:
        cursor = conexion.execute("DELETE FROM estudiantes WHERE id = ?", (id_,))
    return cursor.rowcount == 1


# ═════════════════════════════════════════════════════════════════════════════
# 💉 Demostración: inyección SQL
# ═════════════════════════════════════════════════════════════════════════════
def demo_inyeccion(conexion) -> None:
    """
    Compara dos formas de buscar por nombre exacto.
    Escribe como nombre:   ' OR '1'='1
    """
    texto = input("  Nombre exacto a buscar (prueba con  ' OR '1'='1  ): ")

    # ❌ PELIGROSO: pegar el texto del usuario dentro del SQL
    sql_peligroso = f"SELECT * FROM estudiantes WHERE nombre = '{texto}'"
    print(f"\n  ❌ SQL armado con f-string:\n     {sql_peligroso}")
    filas = conexion.execute(sql_peligroso).fetchall()
    print(f"     → devolvió {len(filas)} filas  (¡si pusiste el truco, devolvió TODAS!)")

    # ✅ SEGURO: el texto viaja aparte, como dato, nunca como código
    filas = conexion.execute("SELECT * FROM estudiantes WHERE nombre = ?", (texto,)).fetchall()
    print("\n  ✅ SQL con parámetro:\n     SELECT * FROM estudiantes WHERE nombre = ?")
    print(f"     → devolvió {len(filas)} filas  (busca literalmente ese texto raro)\n")


# ═════════════════════════════════════════════════════════════════════════════
# Funciones de apoyo para la consola
# ═════════════════════════════════════════════════════════════════════════════
def pedir_entero(mensaje: str) -> int:
    """Pregunta hasta recibir un número entero (lección 02)."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  ⚠ Escribe un número.")


def imprimir_tabla(filas) -> None:
    if not filas:
        print("  (sin resultados)\n")
        return
    print(f"\n  {'ID':<4}{'NOMBRE':<22}{'CORREO':<26}EDAD")
    print("  " + "─" * 56)
    for f in filas:
        print(f"  {f['id']:<4}{f['nombre']:<22}{f['correo']:<26}{f['edad']}")
    print()


# ═════════════════════════════════════════════════════════════════════════════
# Programa principal
# ═════════════════════════════════════════════════════════════════════════════
def main() -> None:
    conexion = conectar()
    print(f"💾 Base de datos: {RUTA_BD}")

    while True:
        print("┌─────────── CRUD + SQLite ───────────┐")
        print("│ 1 Listar   2 Buscar   3 Crear        │")
        print("│ 4 Editar   5 Eliminar 6 Demo 💉      │")
        print("│ 0 Salir                              │")
        print("└──────────────────────────────────────┘")
        opcion = input("Opción: ").strip()

        try:
            if opcion == "1":
                imprimir_tabla(listar(conexion))

            elif opcion == "2":
                imprimir_tabla(listar(conexion, input("  Texto a buscar: ")))

            elif opcion == "3":
                nuevo = crear(conexion, input("  Nombre: "), input("  Correo: "), pedir_entero("  Edad: "))
                print(f"  ✅ Creado con id {nuevo}\n")

            elif opcion == "4":
                id_ = pedir_entero("  ID a editar: ")
                ok = actualizar(conexion, id_, input("  Nuevo nombre: "),
                                input("  Nuevo correo: "), pedir_entero("  Nueva edad: "))
                print("  ✏️ Actualizado\n" if ok else "  ❌ No existe ese id\n")

            elif opcion == "5":
                id_ = pedir_entero("  ID a eliminar: ")
                print("  🗑️ Eliminado\n" if eliminar(conexion, id_) else "  ❌ No existe ese id\n")

            elif opcion == "6":
                demo_inyeccion(conexion)

            elif opcion == "0":
                break

        # Errores que vienen de las reglas de la tabla (UNIQUE, CHECK, NOT NULL)
        except sqlite3.IntegrityError as error:
            print(f"  ❌ La base de datos rechazó el dato: {error}\n")

    conexion.close()
    print("👋 ¡Hasta luego! Tus datos quedaron guardados.")


# Solo se ejecuta main() si corres ESTE archivo directamente.
if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 RETO (5 min): crea una edad fuera de rango (ej. 5).
#    ¿Quién la rechazó: Python o SQLite? (pista: CHECK en la tabla)
# ─────────────────────────────────────────────────────────────────────────────
