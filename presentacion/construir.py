"""
construir.py — Arma la página web del taller con el código Python REAL.
========================================================================

La página (presentacion/index.html) muestra en su «Visor de código» los
archivos de app_crud/. Para no copiarlos a mano, este script:

    1. lee plantilla.html y motor.js,
    2. lee los archivos .py que se muestran en el visor,
    3. los mete dentro de la página como JSON,
    4. escribe index.html (lista para abrir con doble clic en el navegador).

▶ Ejecútalo cada vez que cambies el código de app_crud/:
      python presentacion/construir.py

  Opcional: python presentacion/construir.py ruta/fragmento.html
  escribe además una versión sin <html>/<head> (la que se publica en línea).
"""

import json
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
APP = CARPETA.parent / "app_crud"

# Los mismos archivos (y en el mismo orden) que el visor de la app de escritorio.
ARCHIVOS = [
    "interfaz/ventana_principal.py",
    "validaciones.py",
    "repositorio.py",
    "base_datos.py",
    "modelo.py",
]


def construir() -> str:
    plantilla = (CARPETA / "plantilla.html").read_text(encoding="utf-8")
    motor = (CARPETA / "motor.js").read_text(encoding="utf-8")
    fuentes = {ruta: (APP / ruta).read_text(encoding="utf-8") for ruta in ARCHIVOS}

    # «</» se escapa para que un texto del código nunca cierre el <script> antes de tiempo.
    datos = json.dumps(fuentes, ensure_ascii=False).replace("</", "<\\/")
    return plantilla.replace("__FUENTES__", datos).replace("__MOTOR__", motor)


def documento_completo(fragmento: str) -> str:
    """Envuelve el fragmento con <!doctype>, <head> y <body> para abrirlo localmente."""
    cabeza, cuerpo = fragmento.split("</style>", 1)
    return ("<!doctype html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"{cabeza}</style>\n</head>\n<body>\n{cuerpo}\n</body>\n</html>\n")


if __name__ == "__main__":
    fragmento = construir()
    (CARPETA / "index.html").write_text(documento_completo(fragmento), encoding="utf-8")
    print(f"✔ {CARPETA / 'index.html'}")
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(fragmento, encoding="utf-8")
        print(f"✔ {sys.argv[1]}")
