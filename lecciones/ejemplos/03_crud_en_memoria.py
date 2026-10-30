"""Ejemplo corto de la lección 03 — listas, diccionarios y un CRUD en memoria."""

estudiantes = [
    {"id": 1, "nombre": "Ana", "edad": 22},
    {"id": 2, "nombre": "Carlos", "edad": 24},
]
siguiente_id = 3


def buscar(id_buscado):
    for e in estudiantes:
        if e["id"] == id_buscado:
            return e
    return None                  # None = «no lo encontré»


# C — Create
estudiantes.append({"id": siguiente_id, "nombre": "Sofía", "edad": 19})
siguiente_id += 1

# R — Read
for e in estudiantes:
    print(e["id"], e["nombre"], e["edad"])

# U — Update
ana = buscar(1)
ana["edad"] = 23

# D — Delete
estudiantes.remove(buscar(2))
print("Quedan", len(estudiantes), "estudiantes")
