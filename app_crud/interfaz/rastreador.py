"""
rastreador.py — Grabar qué líneas de código se ejecutan DE VERDAD.
===================================================================

Python permite instalar un «espía» con `sys.settrace(funcion)`.
A partir de ese momento, el intérprete avisa a esa función cada vez que:

    "call"      → entra a una función
    "line"      → está a punto de ejecutar una línea
    "return"    → sale de una función
    "exception" → ocurre un error

Es exactamente la herramienta que usan los depuradores (como el de PyCharm).
Nosotros la usamos para GRABAR el recorrido de cada botón y luego
reproducirlo, paso a paso, en el Visor de código.

    clic en «Crear»
         │
         ▼
    sys.settrace(espía) ──► crear() línea 152 ──► validar_estudiante() línea 30 ...
         │                     (cada línea queda anotada en una lista de Pasos)
         ▼
    sys.settrace(None)  ──► el visor reproduce la lista con la línea brillando

⚠️ Mientras usas el Debug de PyCharm, el depurador ya ocupa settrace.
   En ese caso no grabamos nada para no estorbarle.
"""

import functools
import reprlib
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

from configuracion import CARPETA_APP

# Archivos que se muestran en el visor (en este orden aparecen las pestañas).
ARCHIVOS_VISIBLES = [
    "interfaz/ventana_principal.py",
    "validaciones.py",
    "repositorio.py",
    "base_datos.py",
    "modelo.py",
]

# Funciones que se ejecutan pero NO se recorren por dentro (son largas y
# repetitivas; mostrarlas haría el recorrido eterno). Se ven como un solo paso.
FUNCIONES_RESUMIDAS = {"refrescar"}

MAXIMO_PASOS = 300   # tope de seguridad por si algo entra en un ciclo largo

# reprlib = repr() «recortado»: así una lista enorme no llena la pantalla.
_recortador = reprlib.Repr()
_recortador.maxstring = 46
_recortador.maxother = 70


@dataclass
class Paso:
    """Una línea ejecutada, con su contexto."""
    archivo: str                 # "repositorio.py"
    linea: int                   # 45
    funcion: str                 # "crear"
    pila: list[str]              # ["ventana_principal.crear", "repositorio.crear"]
    variables: dict[str, str] = field(default_factory=dict)
    nota: str = ""               # texto extra: «se resume», «error», etc.
    es_error: bool = False


class Rastreador:
    def __init__(self):
        self._visibles = {(CARPETA_APP / ruta).resolve(): ruta for ruta in ARCHIVOS_VISIBLES}
        self._grabando = False
        self._pasos: list[Paso] = []
        self._pila: list[str] = []
        self._omitido = None     # marco (frame) que se está saltando, si hay uno
        self._cache: dict[str, tuple[str, str | None]] = {}

    # -----------------------------------------------------------------------
    # 🎬 API pública
    # -----------------------------------------------------------------------
    def grabar(self, funcion):
        """
        Ejecuta `funcion()` grabando sus líneas.
        Devuelve (resultado, pasos).  pasos = None si no se pudo grabar.
        """
        # Si ya estamos grabando (una acción provocó otra), la de adentro
        # se ejecuta normal: sus líneas quedan dentro de la grabación de afuera.
        if self._grabando or sys.gettrace() is not None:   # ← Debug de PyCharm activo
            return funcion(), None

        self._grabando = True
        self._pasos, self._pila, self._omitido = [], [], None
        sys.settrace(self._espia_global)
        try:
            resultado = funcion()
        finally:
            sys.settrace(None)          # ¡siempre quitar el espía!
            self._grabando = False
        return resultado, self._pasos

    # -----------------------------------------------------------------------
    # 🕵️ El espía
    # -----------------------------------------------------------------------
    def _espia_global(self, marco, evento, _arg):
        """Python lo llama al ENTRAR a cada función nueva ("call")."""
        if self._omitido is not None or len(self._pasos) >= MAXIMO_PASOS:
            return None

        tipo, ruta = self._clasificar(marco.f_code.co_filename)
        if tipo == "otro":
            return None   # código de Python mismo (sqlite3, tkinter...): no nos interesa
        if tipo == "app":
            # Archivos de la propia app que no mostramos (animaciones, tabla...):
            # los saltamos completos, incluido lo que ellos llamen.
            self._omitido = marco
            return self._espia_omitido

        nombre = marco.f_code.co_name
        etiqueta = f"{Path(ruta).stem}.{nombre}"

        if nombre in FUNCIONES_RESUMIDAS:
            self._anotar(marco, ruta, nota=f"↻ {nombre}() se ejecuta completa (la resumimos en un paso)")
            self._omitido = marco
            return self._espia_omitido

        self._pila.append(etiqueta)
        return self._espia_local

    def _espia_local(self, marco, evento, arg):
        """Python lo llama en cada línea de una función que SÍ mostramos."""
        if evento == "line" and len(self._pasos) < MAXIMO_PASOS:
            self._anotar(marco, self._clasificar(marco.f_code.co_filename)[1])
        elif evento == "exception":
            tipo, valor, _ = arg
            self._anotar(marco, self._clasificar(marco.f_code.co_filename)[1],
                         nota=f"⚠ {tipo.__name__}: {valor}", es_error=True)
        elif evento == "return" and self._pila:
            self._pila.pop()
        return self._espia_local

    def _espia_omitido(self, marco, evento, _arg):
        if evento == "return" and marco is self._omitido:
            self._omitido = None   # terminó la función que saltábamos
        return self._espia_omitido

    # -----------------------------------------------------------------------
    def _anotar(self, marco, ruta: str, nota: str = "", es_error: bool = False) -> None:
        variables = {}
        for nombre, valor in marco.f_locals.items():
            if nombre == "self" or nombre.startswith("_"):
                continue
            try:
                variables[nombre] = _recortador.repr(_legible(valor))
            except Exception:  # un repr() roto no debe tumbar la app
                variables[nombre] = "<?>"
        self._pasos.append(Paso(archivo=ruta, linea=marco.f_lineno, funcion=marco.f_code.co_name,
                                pila=list(self._pila), variables=variables,
                                nota=nota, es_error=es_error))

    def _clasificar(self, nombre_archivo: str) -> tuple[str, str | None]:
        """
        ¿De dónde es este código?
            ("visible", "repositorio.py") → se muestra en el visor
            ("app", None)                 → es de la app, pero no se muestra
            ("otro", None)                → es de Python o de una librería
        Se guarda en un diccionario (caché) porque se pregunta miles de veces.
        """
        if nombre_archivo not in self._cache:
            # Código generado al vuelo (dataclasses, python -c...) se llama "<string>":
            # no es un archivo real, así que nunca es «de la app».
            if nombre_archivo.startswith("<"):
                self._cache[nombre_archivo] = ("otro", None)
                return self._cache[nombre_archivo]
            try:
                ruta = Path(nombre_archivo).resolve()
            except (OSError, ValueError):
                ruta = None
            if ruta in self._visibles:
                self._cache[nombre_archivo] = ("visible", self._visibles[ruta])
            elif ruta is not None and ruta.is_relative_to(CARPETA_APP) and ruta.name != "rastreador.py":
                self._cache[nombre_archivo] = ("app", None)
            else:
                self._cache[nombre_archivo] = ("otro", None)
        return self._cache[nombre_archivo]


def _legible(valor):
    """Una fila de SQLite se imprime como <sqlite3.Row object at 0x...>; mejor como dict."""
    if isinstance(valor, sqlite3.Row):
        return dict(valor)
    if isinstance(valor, list) and valor and isinstance(valor[0], sqlite3.Row):
        return [dict(fila) for fila in valor]
    return valor


# ---------------------------------------------------------------------------
# 🎀 Decorador: «graba este método y muéstralo en el visor»
# ---------------------------------------------------------------------------
def mostrar_en_visor(metodo):
    """
    Un DECORADOR envuelve una función para agregarle comportamiento.
    Se usa así, encima del método:

        @mostrar_en_visor
        def crear(self): ...

    Y equivale a escribir:  crear = mostrar_en_visor(crear)
    """
    @functools.wraps(metodo)
    def envoltura(self, *args, **kwargs):
        resultado, pasos = self.rastreador.grabar(lambda: metodo(self, *args, **kwargs))
        if pasos is not None:
            self.visor.reproducir(pasos, operacion=metodo.__name__)
        return resultado
    return envoltura
