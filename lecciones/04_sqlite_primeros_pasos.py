"""
LECCIÓN 04 — SQLite: datos que sobreviven al cerrar el programa 💾
==================================================================
⏱ 20 minutos

Objetivo: crear una base de datos, una tabla, y hacer el CRUD con SQL.

¿Qué es SQL?  El idioma para hablar con bases de datos.
¿Qué es SQLite? Una base de datos que vive en UN archivo (.db).
               Python ya la trae incluida: no hay que instalar nada.

           Python                         SQLite (archivo .db)
    ┌──────────────────┐   SQL      ┌─────────────────────────────┐
    │ conexion.execute │ ─────────► │ tabla estudiantes           │
    │   ("INSERT ...") │ ◄───────── │ ┌────┬────────┬───────────┐ │
    └──────────────────┘ resultado  │ │ id │ nombre │ correo    │ │
                                    │ ├────┼────────┼───────────┤ │
                                    │ │ 1  │ Ana    │ ana@...   │ │
                                    │ └────┴────────┴───────────┘ │
                                    └─────────────────────────────┘

Las 4 palabras mágicas de SQL:
    INSERT  → C   crear
    SELECT  → R   leer
    UPDATE  → U   actualizar
    DELETE  → D   eliminar

▶ Ejecuta este archivo DOS veces y observa que los datos de la primera
  vez siguen ahí. ¡Eso no pasaba en la lección 03!
  En PyCharm verás aparecer el archivo «leccion04.db» en la carpeta.
"""

import sqlite3   # módulo incluido en Python: conectarse a SQLite

# ─────────────────────────────────────────────────────────────────────────────
# 1. Conectar (si el archivo no existe, SQLite lo crea)
# ─────────────────────────────────────────────────────────────────────────────
conexion = sqlite3.connect("leccion04.db")
print("✅ Conectado a leccion04.db")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Crear la tabla (solo si no existe todavía)
# ─────────────────────────────────────────────────────────────────────────────
conexion.execute("""
    CREATE TABLE IF NOT EXISTS estudiantes (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,  -- número único y automático
        nombre  TEXT NOT NULL,                      -- obligatorio
        correo  TEXT NOT NULL UNIQUE,               -- obligatorio y sin repetir
        edad    INTEGER
    )
""")
# (Dentro de un texto SQL, los comentarios se escriben con -- en lugar de #)

# ─────────────────────────────────────────────────────────────────────────────
# 3. C — INSERT: crear un registro
# ─────────────────────────────────────────────────────────────────────────────
# Los ? son «huecos» que SQLite llena con la tupla de valores.
# ¡NUNCA pegues los valores con f-strings dentro del SQL! (ver lección 05)
try:
    conexion.execute(
        "INSERT INTO estudiantes (nombre, correo, edad) VALUES (?, ?, ?)",
        ("Ana Pérez", "ana@correo.com", 21),
    )
    conexion.execute(
        "INSERT INTO estudiantes (nombre, correo, edad) VALUES (?, ?, ?)",
        ("Carlos Méndez", "carlos@correo.com", 24),
    )
    conexion.commit()   # 💾 commit = «guardar cambios en el archivo»
    print("✅ Dos estudiantes insertados")
except sqlite3.IntegrityError:
    # La segunda vez que ejecutas, los correos ya existen (UNIQUE) y SQLite dice que no.
    print("ℹ Los estudiantes ya existían (el correo es UNIQUE). ¡Los datos sobrevivieron!")

# ─────────────────────────────────────────────────────────────────────────────
# 4. R — SELECT: leer registros
# ─────────────────────────────────────────────────────────────────────────────
cursor = conexion.execute("SELECT id, nombre, correo, edad FROM estudiantes")
filas = cursor.fetchall()   # lista de tuplas: [(1, 'Ana Pérez', 'ana@...', 21), ...]

print("\n📋 Estudiantes en la base de datos:")
for id_, nombre, correo, edad in filas:     # «desempaquetar» cada tupla
    print(f"   #{id_}  {nombre:<15} {correo:<20} {edad} años")

# SELECT con condición (WHERE)
mayores = conexion.execute("SELECT nombre FROM estudiantes WHERE edad > ?", (22,)).fetchall()
print("\n🔎 Mayores de 22:", [fila[0] for fila in mayores])
# ⚠️ Fíjate en la coma de (22,) → una tupla de UN elemento necesita la coma.

# ─────────────────────────────────────────────────────────────────────────────
# 5. U — UPDATE: modificar
# ─────────────────────────────────────────────────────────────────────────────
conexion.execute("UPDATE estudiantes SET edad = edad + 1 WHERE correo = ?", ("ana@correo.com",))
conexion.commit()
print("\n🎂 ¡Ana cumplió años!")
# ⚠️ Sin WHERE, el UPDATE modificaría a TODOS los estudiantes.

# ─────────────────────────────────────────────────────────────────────────────
# 6. D — DELETE: eliminar
# ─────────────────────────────────────────────────────────────────────────────
# Lo dejamos comentado para que los datos se queden. Quita el # para probarlo.
# conexion.execute("DELETE FROM estudiantes WHERE correo = ?", ("carlos@correo.com",))
# conexion.commit()

# Contar con SQL
total = conexion.execute("SELECT COUNT(*) FROM estudiantes").fetchone()[0]
print(f"\n📊 Total en la tabla: {total}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. Cerrar la conexión (buena costumbre)
# ─────────────────────────────────────────────────────────────────────────────
conexion.close()

# ─────────────────────────────────────────────────────────────────────────────
# 🔭 PYCHARM PRO-TIP: abre «leccion04.db» con el panel Database
#    (PyCharm Professional) o con la extensión gratuita «Database Navigator»,
#    o con el programa gratuito «DB Browser for SQLite». ¡Verás la tabla!
#
# 🎯 RETO (4 min): agrega una columna «carrera» a la tabla.
#    Pista: borra leccion04.db (porque la tabla ya existe) y cambia el CREATE TABLE.
# ─────────────────────────────────────────────────────────────────────────────
