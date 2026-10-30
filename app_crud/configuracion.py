"""
configuracion.py — El «panel de control» de la aplicación.
=============================================================

Aquí vive TODO lo que podríamos querer cambiar sin tocar la lógica:
rutas, colores, textos y listas de opciones.

💡 Idea para la clase:
    Si un alumno quiere cambiar el color principal o agregar una carrera,
    solo edita este archivo. Así se enseña el principio de
    «separar la configuración del código».
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# 📁 Rutas
# ---------------------------------------------------------------------------
# Path(__file__) es la ruta de ESTE archivo. .parent es su carpeta.
# Así la base de datos se crea junto al código, sin importar desde dónde
# se ejecute el programa (PyCharm, terminal, doble clic...).
CARPETA_APP = Path(__file__).resolve().parent
RUTA_BD = CARPETA_APP / "taller.db"

# ---------------------------------------------------------------------------
# 🏷️ Textos
# ---------------------------------------------------------------------------
TITULO_APP = "Registro de Estudiantes"
SUBTITULO_APP = "Taller de Programación de Lenguaje Python con IDE PyCharm"

# Opciones de la lista desplegable «Carrera».
CARRERAS = [
    "Ingeniería en Sistemas",
    "Agronomía",
    "Administración de Empresas",
    "Medicina",
    "Derecho",
    "Arquitectura",
    "Otra",
]

# ---------------------------------------------------------------------------
# 🎨 Paleta de colores
# ---------------------------------------------------------------------------
# Inspirada en el logo de Python (azul + amarillo).
# Cada letra del CRUD tiene su propio color: así el alumno
# «ve» qué operación ocurrió en la pantalla, en la tabla y en la consola SQL.
COLORES = {
    # Superficies
    "fondo": "#EEF2F8",
    "tarjeta": "#FFFFFF",
    "borde": "#D5DCE8",
    "encabezado": "#1F3A68",      # azul profundo de Python
    "encabezado_texto": "#FFFFFF",
    "amarillo": "#FFD43B",        # amarillo de Python

    # Texto
    "texto": "#1C2333",
    "texto_suave": "#5F6B82",
    "error": "#C62828",
    "campo_error": "#FDECEC",

    # Las 4 operaciones del CRUD
    "crear": "#1E9E5A",           # C — Create  → verde (algo nace)
    "leer": "#2F6FDE",            # R — Read    → azul (solo miramos)
    "actualizar": "#E08A00",      # U — Update  → naranja (algo cambia)
    "eliminar": "#D64545",        # D — Delete  → rojo (cuidado)

    # Consola SQL (estilo terminal)
    "consola_fondo": "#111722",
    "consola_texto": "#D6DEEB",
    "consola_suave": "#6E7A91",
    "consola_palabra": "#C792EA",  # palabras clave SQL
    "consola_valor": "#FFD43B",    # valores enviados

    # Visor de código (imita el tema oscuro de PyCharm)
    "editor_fondo": "#1E1F22",
    "editor_barra": "#2B2D30",
    "editor_borde": "#393B40",
    "editor_texto": "#BCBEC4",
    "editor_numero": "#4B5059",
    "editor_clave": "#CF8E6D",     # def, if, return...
    "editor_cadena": "#6AAB73",    # "textos"
    "editor_comentario": "#7A7E85",
    "editor_literal": "#2AACB8",   # números, True, None
    "editor_definicion": "#56A8F5",  # nombre de funciones y clases
    "editor_self": "#94558D",
    "editor_integrada": "#8888C6",   # print, len, int...
    "editor_decorador": "#B3AE60",
}

# Información de cada operación del CRUD: letra, nombre y color.
# La usan el semáforo del encabezado, la consola y la pizarra.
OPERACIONES = {
    "INSERT": {"letra": "C", "nombre": "Create · Crear", "color": COLORES["crear"]},
    "SELECT": {"letra": "R", "nombre": "Read · Leer", "color": COLORES["leer"]},
    "UPDATE": {"letra": "U", "nombre": "Update · Actualizar", "color": COLORES["actualizar"]},
    "DELETE": {"letra": "D", "nombre": "Delete · Eliminar", "color": COLORES["eliminar"]},
}

# ---------------------------------------------------------------------------
# ⏱️ Animaciones (milisegundos)
# ---------------------------------------------------------------------------
# Si una computadora del laboratorio es lenta, se pueden subir estos valores
# o poner ANIMACIONES_ACTIVAS = False.
ANIMACIONES_ACTIVAS = True
DURACION_TOAST = 2600         # cuánto se queda visible el aviso flotante
VELOCIDAD_ESCRITURA = 12      # ms por letra en la «pizarra»

# ---------------------------------------------------------------------------
# 🔦 Visor de código (la ventana que muestra qué línea se está ejecutando)
# ---------------------------------------------------------------------------
VISOR_AL_INICIAR = True       # abrir el visor junto con la app
VISOR_MS_POR_LINEA = 260      # velocidad inicial de la reproducción
