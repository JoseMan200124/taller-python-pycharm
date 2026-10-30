"""Ejemplo corto de la lección 04 — el CRUD con SQL en una base de datos SQLite."""
import sqlite3

conexion = sqlite3.connect(":memory:")   # en la lección: "leccion04.db" (un archivo)
conexion.execute("""CREATE TABLE estudiantes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    edad   INTEGER)""")

# C — INSERT: los ? se llenan con la tupla de valores
conexion.execute("INSERT INTO estudiantes (nombre, edad) VALUES (?, ?)", ("Ana", 21))
conexion.execute("INSERT INTO estudiantes (nombre, edad) VALUES (?, ?)", ("Carlos", 24))
conexion.commit()                        # guardar los cambios

# R — SELECT
filas = conexion.execute("SELECT id, nombre, edad FROM estudiantes").fetchall()
for id_, nombre, edad in filas:
    print(f"#{id_} {nombre}, {edad} años")

# U — UPDATE (¡siempre con WHERE!)
conexion.execute("UPDATE estudiantes SET edad = edad + 1 WHERE nombre = ?", ("Ana",))

# D — DELETE
conexion.execute("DELETE FROM estudiantes WHERE nombre = ?", ("Carlos",))
conexion.commit()

total = conexion.execute("SELECT COUNT(*) FROM estudiantes").fetchone()[0]
print("Total en la tabla:", total)
conexion.close()
