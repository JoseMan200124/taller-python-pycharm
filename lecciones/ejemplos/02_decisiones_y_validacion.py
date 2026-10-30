"""Ejemplo corto de la lección 02 — if/elif/else, try/except y while."""

nota = 75
if nota >= 90:
    print("Excelente")
elif nota >= 61:
    print("Aprobado")
else:
    print("Reprobado")

texto = "veinte"
try:
    numero = int(texto)          # aquí ocurre un ValueError...
except ValueError:
    print(f"«{texto}» no es un número, pero el programa no se cayó")

# Preguntar HASTA que la respuesta sea válida
while True:
    respuesta = input("Edad (10 a 120): ")
    try:
        edad = int(respuesta)
    except ValueError:
        print("  Escribe solo números")
        continue                 # vuelve al inicio del while
    if 10 <= edad <= 120:
        break                    # sale del while
    print("  Debe estar entre 10 y 120")

print(f"Edad registrada: {edad}")
