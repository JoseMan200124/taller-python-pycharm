"""Ejemplo corto de la lección 01 — variables, tipos, operaciones, f-strings e input()."""

print("¡Hola, mundo!")

nombre = "Ana"          # str   → texto
edad = 21               # int   → número entero
estatura = 1.62         # float → número con decimales
es_estudiante = True    # bool  → True o False

print(type(edad))
print(10 // 3, 10 % 3, 2 ** 10)    # división entera, residuo y potencia
print(f"{nombre} tiene {edad} años y mide {estatura} m.")

tu_nombre = input("¿Cómo te llamas? ")
tu_edad = int(input("¿Cuántos años tienes? "))   # input() devuelve texto: lo convertimos
print(f"Mucho gusto, {tu_nombre}. En 10 años tendrás {tu_edad + 10}.")
