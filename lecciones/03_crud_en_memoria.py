"""
LECCIÓN 03 — Listas, diccionarios y nuestro primer CRUD (en memoria) 🧠
======================================================================
⏱ 25 minutos

Objetivo: guardar VARIOS estudiantes y hacer las 4 operaciones del CRUD
usando solo estructuras de Python (todavía sin base de datos).

    C → Create  (crear)       ─┐
    R → Read    (leer)         │  Casi TODO sistema que usas
    U → Update  (actualizar)   │  (bancos, redes sociales, tiendas)
    D → Delete  (eliminar)    ─┘  es un CRUD por dentro.

Lo que vas a aprender:
    1. Diccionario → un estudiante:  {"nombre": "Ana", "edad": 21}
    2. Lista       → muchos estudiantes: [ {...}, {...}, {...} ]
    3. for         → recorrer la lista
    4. Un MENÚ que se repite con while

⚠️ Spoiler: al cerrar el programa ¡se pierde todo! (vive en la memoria RAM).
   Ese «dolor» es la razón de la lección 05: guardar en una base de datos.
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. Un diccionario = una ficha con campos
# ─────────────────────────────────────────────────────────────────────────────
#       clave       valor
#      ┌─────────┬──────────────────┐
#      │ "nombre"│ "Ana Pérez"      │
#      │ "correo"│ "ana@correo.com" │
#      │ "edad"  │ 21               │
#      └─────────┴──────────────────┘
ana = {"id": 1, "nombre": "Ana Pérez", "correo": "ana@correo.com", "edad": 21}
print(ana["nombre"])      # leer un campo
ana["edad"] = 22          # cambiar un campo

# ─────────────────────────────────────────────────────────────────────────────
# 2. Una lista de diccionarios = una «tabla»
# ─────────────────────────────────────────────────────────────────────────────
estudiantes = [
    {"id": 1, "nombre": "Ana Pérez", "correo": "ana@correo.com", "edad": 22},
    {"id": 2, "nombre": "Carlos Méndez", "correo": "carlos@correo.com", "edad": 24},
]
siguiente_id = 3   # simulamos el AUTOINCREMENT de una base de datos


# ─────────────────────────────────────────────────────────────────────────────
# 3. Las 4 operaciones
# ─────────────────────────────────────────────────────────────────────────────
def mostrar_todos():                                   # R — Read
    print("\n  ID  NOMBRE                CORREO                 EDAD")
    print("  " + "─" * 56)
    for e in estudiantes:
        # :<20 = alinear a la izquierda en 20 espacios (para que se vea como tabla)
        print(f"  {e['id']:<3} {e['nombre']:<21} {e['correo']:<22} {e['edad']}")
    print(f"  Total: {len(estudiantes)}\n")


def buscar_por_id(id_buscado):
    for e in estudiantes:
        if e["id"] == id_buscado:
            return e
    return None   # None = «no encontré nada»


def crear():                                            # C — Create
    global siguiente_id   # vamos a MODIFICAR una variable de afuera de la función
    nombre = input("  Nombre: ")
    correo = input("  Correo: ")
    edad = int(input("  Edad: "))
    estudiantes.append({"id": siguiente_id, "nombre": nombre, "correo": correo, "edad": edad})
    print(f"  ✅ Creado con id {siguiente_id}")
    siguiente_id += 1


def actualizar():                                       # U — Update
    e = buscar_por_id(int(input("  ID a modificar: ")))
    if e is None:
        print("  ❌ No existe ese id")
        return
    # Truco: si el usuario deja vacío y da Enter, se conserva el valor anterior.
    e["nombre"] = input(f"  Nombre [{e['nombre']}]: ") or e["nombre"]
    e["correo"] = input(f"  Correo [{e['correo']}]: ") or e["correo"]
    edad = input(f"  Edad [{e['edad']}]: ")
    if edad:
        e["edad"] = int(edad)
    print("  ✏️ Actualizado")


def eliminar():                                         # D — Delete
    e = buscar_por_id(int(input("  ID a eliminar: ")))
    if e is None:
        print("  ❌ No existe ese id")
        return
    if input(f"  ¿Eliminar a {e['nombre']}? (s/n): ").lower() == "s":
        estudiantes.remove(e)
        print("  🗑️ Eliminado")


# ─────────────────────────────────────────────────────────────────────────────
# 4. El menú: un ciclo que se repite hasta elegir «Salir»
# ─────────────────────────────────────────────────────────────────────────────
# Un diccionario puede guardar FUNCIONES como valores. Así evitamos un if gigante.
opciones = {"1": mostrar_todos, "2": crear, "3": actualizar, "4": eliminar}

while True:
    print("╔══════════════════════════╗")
    print("║   CRUD EN MEMORIA        ║")
    print("╠══════════════════════════╣")
    print("║ 1. Ver todos      (R)    ║")
    print("║ 2. Crear          (C)    ║")
    print("║ 3. Actualizar     (U)    ║")
    print("║ 4. Eliminar       (D)    ║")
    print("║ 0. Salir                 ║")
    print("╚══════════════════════════╝")
    opcion = input("Elige: ")

    if opcion == "0":
        print("¡Adiós! (y adiós a todos los datos... 😱)")
        break
    if opcion in opciones:
        try:
            opciones[opcion]()      # ← los paréntesis EJECUTAN la función guardada
        except ValueError:
            print("  ⚠ Escribe un número válido")
    else:
        print("Opción no válida")

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 RETO (5 min): agrega la opción «5. Buscar por nombre».
#    Pista:  if texto.lower() in e["nombre"].lower(): ...
# ─────────────────────────────────────────────────────────────────────────────
