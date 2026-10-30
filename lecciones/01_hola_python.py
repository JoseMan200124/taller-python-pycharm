"""
LECCIÓN 01 — Hola, Python 👋
=============================
⏱ 15 minutos

Objetivo: escribir, ejecutar y entender nuestro primer programa.

▶ En PyCharm: clic derecho sobre este archivo → Run '01_hola_python'
   (o Ctrl+Shift+F10 en Windows/Linux · Ctrl+Shift+R en macOS).
   La salida aparece abajo, en la ventana «Run».

Lo que vas a aprender:
    1. print()     → mostrar algo en pantalla
    2. variables   → cajitas con nombre que guardan datos
    3. tipos       → texto (str), enteros (int), decimales (float), sí/no (bool)
    4. f-strings   → mezclar texto y variables
    5. input()     → pedirle datos al usuario
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. print() — el «hola mundo» de toda la vida
# ─────────────────────────────────────────────────────────────────────────────
# Todo lo que está después de un # es un COMENTARIO: Python lo ignora.
# Sirve para explicarle a otros humanos (y a tu yo del futuro) qué hace el código.
print("¡Hola, mundo!")
print("Bienvenidos al Taller de Python con PyCharm")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Variables — una cajita con etiqueta
# ─────────────────────────────────────────────────────────────────────────────
#
#       nombre ──► ┌──────────┐
#                  │  "Ana"   │
#                  └──────────┘
#
# El signo = NO significa «igual» como en matemáticas: significa «guarda».
nombre = "Ana"          # str   → texto, siempre entre comillas
edad = 21               # int   → número entero
estatura = 1.62         # float → número con decimales (se usa punto, no coma)
es_estudiante = True    # bool  → solo puede ser True o False

print(nombre, edad, estatura, es_estudiante)

# type() nos dice qué TIPO de dato hay dentro de la cajita.
print(type(nombre), type(edad), type(estatura), type(es_estudiante))

# ─────────────────────────────────────────────────────────────────────────────
# 3. Operaciones
# ─────────────────────────────────────────────────────────────────────────────
print(10 + 3)    # 13   suma
print(10 - 3)    # 7    resta
print(10 * 3)    # 30   multiplicación
print(10 / 3)    # 3.33 división (siempre da decimal)
print(10 // 3)   # 3    división entera
print(10 % 3)    # 1    residuo («módulo»): ¿es par? → numero % 2 == 0
print(2 ** 10)   # 1024 potencia

# Con texto, + PEGA y * REPITE:
print("Py" + "thon")   # Python
print("ja" * 3)        # jajaja

# ─────────────────────────────────────────────────────────────────────────────
# 4. f-strings — la forma moderna de armar mensajes
# ─────────────────────────────────────────────────────────────────────────────
# Una f antes de las comillas permite meter variables entre { }.
print(f"{nombre} tiene {edad} años y mide {estatura} m.")
print(f"El próximo año {nombre} tendrá {edad + 1} años.")   # ¡se puede calcular adentro!

# ─────────────────────────────────────────────────────────────────────────────
# 5. input() — el programa le pregunta al usuario
# ─────────────────────────────────────────────────────────────────────────────
# input() SIEMPRE devuelve texto (str), aunque el usuario escriba un número.
tu_nombre = input("¿Cómo te llamas? ")
tu_edad_texto = input("¿Cuántos años tienes? ")

# Para hacer cuentas, hay que CONVERTIR el texto a número con int().
tu_edad = int(tu_edad_texto)

print(f"Mucho gusto, {tu_nombre}. En 10 años tendrás {tu_edad + 10}.")

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 RETO RÁPIDO (3 min)
#    Pide el año en que naciste y calcula cuántos años cumples en 2030.
#    Pista: año_nacimiento = int(input("..."))
#
# 🐞 EXPERIMENTO: ejecuta el programa y escribe «veinte» en la edad.
#    ¿Qué error sale? (ValueError). En la lección 02 aprendemos a evitarlo.
# ─────────────────────────────────────────────────────────────────────────────
