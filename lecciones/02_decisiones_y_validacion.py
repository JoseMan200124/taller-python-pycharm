"""
LECCIÓN 02 — Tomar decisiones y validar datos 🚦
================================================
⏱ 15 minutos

Objetivo: que el programa reaccione distinto según los datos,
y que NO se caiga si el usuario escribe algo raro.

Lo que vas a aprender:
    1. if / elif / else   → decisiones
    2. comparaciones      → ==  !=  <  >  <=  >=
    3. and / or / not     → combinar condiciones
    4. while              → repetir mientras algo sea cierto
    5. try / except       → atrapar errores antes de que «truenen» el programa

⚠️ En Python la INDENTACIÓN (los 4 espacios) es obligatoria:
   indica qué líneas están «dentro» del if.  PyCharm la pone solo al dar Enter.
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. if / elif / else
# ─────────────────────────────────────────────────────────────────────────────
#
#                 ┌─────────────┐
#                 │ ¿nota >= 90? │──sí──► "Excelente"
#                 └──────┬──────┘
#                        no
#                 ┌──────▼──────┐
#                 │ ¿nota >= 61? │──sí──► "Aprobado"
#                 └──────┬──────┘
#                        no ──────────► "Reprobado"
#
nota = 75

if nota >= 90:
    print("Excelente 🏆")
elif nota >= 61:          # elif = «si no, pero si...»
    print("Aprobado ✅")
else:                     # else = «en cualquier otro caso»
    print("Reprobado ❌")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Combinar condiciones
# ─────────────────────────────────────────────────────────────────────────────
edad = 20
tiene_carne = True

if edad >= 18 and tiene_carne:
    print("Puede inscribirse en el taller")

if edad < 10 or edad > 120:
    print("Esa edad no parece real")

# ─────────────────────────────────────────────────────────────────────────────
# 3. try / except — el «paracaídas»
# ─────────────────────────────────────────────────────────────────────────────
# int("veinte") provoca ValueError. Con try/except lo atrapamos.
texto = "veinte"
try:
    numero = int(texto)
    print("Convertido:", numero)
except ValueError:
    print(f"«{texto}» no es un número. ¡Pero el programa NO se cayó!")

# ─────────────────────────────────────────────────────────────────────────────
# 4. while + try — preguntar HASTA que la respuesta sea válida
# ─────────────────────────────────────────────────────────────────────────────
# Este patrón lo usarás muchísimo. Es exactamente lo que hace validaciones.py
# en la aplicación final, pero allá los errores se pintan en rojo en la ventana.
while True:                                   # ciclo infinito...
    respuesta = input("Escribe tu edad (10 a 120): ")
    try:
        edad = int(respuesta)
    except ValueError:
        print("  ⚠ Escribe solo números, por favor.")
        continue                              # vuelve al inicio del while

    if 10 <= edad <= 120:                     # ¡Python permite comparaciones encadenadas!
        break                                 # ...hasta que hacemos break
    print("  ⚠ La edad debe estar entre 10 y 120.")

print(f"Edad registrada: {edad}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Validar un correo (versión sencilla)
# ─────────────────────────────────────────────────────────────────────────────
correo = input("Tu correo: ").strip().lower()   # strip() quita espacios, lower() pasa a minúsculas

if "@" in correo and "." in correo.split("@")[-1]:
    print("Correo con buena pinta 📧")
else:
    print("Ese correo no parece válido")

# ─────────────────────────────────────────────────────────────────────────────
# 🎯 RETO RÁPIDO (4 min)
#    Pide un número de teléfono y valida que tenga exactamente 8 dígitos.
#    Pistas:  telefono.isdigit()  →  True si todo son dígitos
#             len(telefono)       →  cuántos caracteres tiene
#
# 🐞 PYCHARM: pon un «breakpoint» (clic en el margen, junto al número de línea
#    del while) y ejecuta con Debug (el insecto 🐞). Avanza con F8 y mira
#    cómo cambia la variable `edad` en el panel «Variables».
# ─────────────────────────────────────────────────────────────────────────────
