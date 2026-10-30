"""
grabar_lecciones.py — Graba, línea por línea, cómo se ejecutan los ejemplos.
============================================================================

La sección «Las lecciones, paso a paso» de la página muestra los ejemplos
cortos de `lecciones/ejemplos/` ejecutándose una línea a la vez, con sus
variables, lo que imprimen y (si usan SQLite) cómo queda la tabla.

No es una simulación escrita a mano: este script EJECUTA cada ejemplo con
Python y lo graba con `sys.settrace`, el mismo mecanismo que usa el depurador
de PyCharm. Lo que el ejemplo pide con input() se responde con las
`entradas` de abajo, y en los ejemplos con ventana (06 y 07) un tkinter
«de mentira» reproduce lo que haría el usuario: escribir y hacer clic.

▶ Ejecútalo cada vez que cambies un ejemplo, y después construir.py:
      python presentacion/grabar_lecciones.py
      python presentacion/construir.py

Escribe presentacion/lecciones.json, que construir.py inserta en la página.
"""

import json
import reprlib
import sqlite3
import sys
import types
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
EJEMPLOS = CARPETA.parent / "lecciones" / "ejemplos"
SALIDA = CARPETA / "lecciones.json"
REPO = "https://github.com/JoseMan200124/taller-python-pycharm/blob/main/"
NOMBRE_CODIGO = "<ejemplo>"   # así reconocemos las líneas del ejemplo dentro del rastreo
MAX_PASOS = 500

LECCIONES = [
    {"archivo": "01_hola_python.py", "leccion": "lecciones/01_hola_python.py",
     "titulo": "Hola, Python",
     "idea": "Las variables son cajitas con nombre; input() siempre devuelve texto.",
     "entradas": ["Luis", "19"]},
    {"archivo": "02_decisiones_y_validacion.py", "leccion": "lecciones/02_decisiones_y_validacion.py",
     "titulo": "Decisiones y validación",
     "idea": "if elige un camino; try/except atrapa el error; while repite hasta que el dato sirve.",
     "entradas": ["veinte", "5", "20"]},
    {"archivo": "03_crud_en_memoria.py", "leccion": "lecciones/03_crud_en_memoria.py",
     "titulo": "CRUD en memoria",
     "idea": "Una lista de diccionarios funciona como una tabla… hasta que cierras el programa.",
     "entradas": []},
    {"archivo": "04_sqlite_primeros_pasos.py", "leccion": "lecciones/04_sqlite_primeros_pasos.py",
     "titulo": "SQLite: primeros pasos",
     "idea": "INSERT, SELECT, UPDATE y DELETE: mira la tabla cambiar con cada línea.",
     "entradas": []},
    {"archivo": "05_crud_consola_sqlite.py", "leccion": "lecciones/05_crud_consola_sqlite.py",
     "titulo": "CRUD con funciones",
     "idea": "Cada operación es una función; el correo repetido lo rechaza SQLite, no Python.",
     "entradas": []},
    {"archivo": "06_primera_ventana.py", "leccion": "lecciones/06_primera_ventana.py",
     "titulo": "Primera ventana",
     "idea": "mainloop() espera; cada clic llama a la función que le diste con command=.",
     "entradas": [],
     "eventos": [("clic", "Saludar"), ("escribir", 0, "Ana"), ("clic", "Saludar"), ("clic", "Saludar")]},
    {"archivo": "07_crud_grafico_un_archivo.py", "leccion": "lecciones/07_crud_grafico_un_archivo.py",
     "titulo": "CRUD gráfico",
     "idea": "La ventana, la validación y el SQL juntos: el mismo camino que la app final.",
     "entradas": [],
     "eventos": [("escribir", 0, "Ana"), ("escribir", 1, "veinte"), ("clic", "Crear"),
                 ("escribir", 1, "21"), ("clic", "Crear"),
                 ("escribir", 0, "Carlos"), ("escribir", 1, "24"), ("clic", "Crear")]},
]


# ---------------------------------------------------------------------------
# Cómo se ven los valores en el panel «Variables»
# ---------------------------------------------------------------------------
_corto = reprlib.Repr()
_corto.maxstring = 48
_corto.maxother = 48
_corto.maxlist = _corto.maxtuple = 6
_corto.maxdict = 5
_corto.maxlevel = 3


def legible(valor) -> str:
    if isinstance(valor, sqlite3.Connection):
        return "<conexión SQLite>"
    if isinstance(valor, sqlite3.Cursor):
        return "<cursor SQLite>"
    if isinstance(valor, sqlite3.Row):
        return _corto.repr(dict(valor))
    if isinstance(valor, list) and valor and isinstance(valor[0], sqlite3.Row):
        return _corto.repr([dict(f) for f in valor])
    if isinstance(valor, BaseException):
        return f"{type(valor).__name__}: {valor}"
    if isinstance(valor, (_Variable, _Widget, _Tk)):
        return repr(valor)
    texto = _corto.repr(valor)
    return f"<{type(valor).__name__}>" if " at 0x" in texto else texto


def variables_visibles(espacio: dict) -> dict:
    """Solo lo que escribió el alumno: sin módulos, funciones ni nombres internos."""
    return {nombre: legible(valor) for nombre, valor in espacio.items()
            if not nombre.startswith("__")
            and not isinstance(valor, (types.ModuleType, types.FunctionType, types.MethodType,
                                      types.BuiltinFunctionType, type))}


# ---------------------------------------------------------------------------
# Un tkinter «de mentira» para grabar los ejemplos con ventana
# ---------------------------------------------------------------------------
# Tiene solo lo que usan los ejemplos 06 y 07, con los mismos nombres que el
# tkinter real. mainloop() no espera clics: reproduce los `eventos`.
class _Variable:
    def __init__(self, master=None, value=None, name=None):
        self._valor = self._inicial if value is None else value

    def get(self):
        return self._valor

    def set(self, valor):
        self._valor = valor

    def __repr__(self):
        return f"{type(self).__name__}({self._valor!r})"


class _StringVar(_Variable):
    _inicial = ""


class _IntVar(_Variable):
    _inicial = 0


class _Widget:
    def __init__(self, master=None, **opciones):
        self.opciones = opciones
        master.widgets.append(self)

    def pack(self, **_):
        pass

    def grid(self, **_):
        pass

    def __repr__(self):
        return f"<{type(self).__name__}>"

    def foto(self) -> dict:
        variable = self.opciones.get("textvariable")
        texto = variable.get() if variable is not None else self.opciones.get("text", "")
        return {"tipo": type(self).__name__, "texto": str(texto)}


class _Label(_Widget):
    pass


class _Entry(_Widget):
    pass


class _Button(_Widget):
    pass


class _Listbox(_Widget):
    def __init__(self, master=None, **opciones):
        super().__init__(master, **opciones)
        self.filas = []

    def insert(self, indice, texto):
        self.filas.append(texto) if indice == "end" else self.filas.insert(int(indice), texto)

    def delete(self, primero, ultimo=None):
        fin = len(self.filas) if ultimo == "end" else (int(ultimo) + 1 if ultimo is not None else int(primero) + 1)
        del self.filas[int(primero):fin]

    def foto(self) -> dict:
        return {"tipo": "Listbox", "filas": list(self.filas)}


class _Tk:
    def __init__(self):
        self.widgets = []
        self.titulo = "tk"
        _GRABANDO.ventana = self

    def title(self, texto):
        self.titulo = texto

    def geometry(self, _):
        pass

    def __repr__(self):
        return "<Tk>"

    def foto(self) -> dict:
        return {"titulo": self.titulo, "widgets": [w.foto() for w in self.widgets]}

    def mainloop(self):
        marco = sys._getframe(1)           # la línea «ventana.mainloop()» del ejemplo
        entradas = [w for w in self.widgets if isinstance(w, _Entry)]
        for evento in _GRABANDO.eventos:
            if evento[0] == "escribir":
                _, n, texto = evento
                entradas[n].opciones["textvariable"].set(texto)
                _GRABANDO.paso(marco, evento=f"⌨ escribes «{texto}»", resalta=("Entry", n))
            else:
                boton = next(w for w in self.widgets if isinstance(w, _Button) and w.opciones.get("text") == evento[1])
                _GRABANDO.paso(marco, evento=f"🖱 clic en «{evento[1]}»", resalta=("Button", evento[1]))
                boton.opciones["command"]()


# En el panel de variables deben verse con su nombre de tkinter: StringVar('Ana'), no _StringVar.
for _clase in (_StringVar, _IntVar, _Label, _Entry, _Button, _Listbox, _Tk):
    _clase.__name__ = _clase.__qualname__ = _clase.__name__.lstrip("_")


def _tkinter_falso() -> types.ModuleType:
    modulo = types.ModuleType("tkinter")
    modulo.Tk, modulo.StringVar, modulo.IntVar = _Tk, _StringVar, _IntVar
    modulo.Label, modulo.Entry, modulo.Button, modulo.Listbox = _Label, _Entry, _Button, _Listbox
    modulo.END = "end"
    return modulo


# ---------------------------------------------------------------------------
# El grabador
# ---------------------------------------------------------------------------
class Grabador:
    def __init__(self, entradas, eventos):
        self.entradas = list(entradas)
        self.eventos = list(eventos)
        self.salida = []          # [["out" | "in", texto], ...]
        self.pasos = []
        self.ventana = None
        self.tabla = None

    # Consola: print() escribe aquí; input() responde con las entradas
    def write(self, texto):
        if self.salida and self.salida[-1][0] == "out":
            self.salida[-1][1] += texto
        else:
            self.salida.append(["out", texto])

    def flush(self):
        pass

    def input(self, mensaje=""):
        self.write(str(mensaje))
        respuesta = self.entradas.pop(0)
        self.salida.append(["in", respuesta])
        self.write("\n")
        return respuesta

    def caracteres(self) -> int:
        return sum(len(t) for _, t in self.salida)

    def foto_tabla(self, marco):
        """Lee la tabla `estudiantes` de la conexión SQLite que tenga el ejemplo."""
        while marco is not None and marco.f_code.co_filename == NOMBRE_CODIGO:
            for valor in list(marco.f_locals.values()) + list(marco.f_globals.values()):
                if isinstance(valor, sqlite3.Connection):
                    try:
                        cursor = valor.execute("SELECT * FROM estudiantes")
                        self.tabla = {"columnas": [d[0] for d in cursor.description],
                                      "filas": [list(f) for f in cursor.fetchall()]}
                    except sqlite3.Error:
                        pass      # la tabla aún no existe, o la conexión ya se cerró
                    return
            marco = marco.f_back

    def paso(self, marco, evento=None, resalta=None):
        if len(self.pasos) >= MAX_PASOS:
            raise RuntimeError("El ejemplo dio demasiados pasos: ¿hay un ciclo infinito?")
        pila, m = [], marco
        while m is not None and m.f_code.co_filename == NOMBRE_CODIGO:
            pila.append(m.f_code.co_name if m.f_code.co_name != "<module>" else "módulo")
            m = m.f_back
        en_funcion = marco.f_code.co_name != "<module>"
        self.foto_tabla(marco)
        paso = {
            "linea": marco.f_lineno,
            "funcion": marco.f_code.co_name if en_funcion else None,
            "pila": pila,
            "locales": variables_visibles(marco.f_locals) if en_funcion else None,
            "globales": variables_visibles(marco.f_globals),
            "salida": self.caracteres(),
        }
        if evento:
            paso["evento"] = evento
        if resalta:
            paso["resalta"] = list(resalta)
        if self.ventana is not None:
            paso["ventana"] = self.ventana.foto()
        if self.tabla is not None:
            paso["tabla"] = self.tabla
        self.pasos.append(paso)

    def espia(self, marco, evento, _arg):
        if marco.f_code.co_filename != NOMBRE_CODIGO:
            return None
        if evento == "line":
            self.paso(marco)
        return self.espia


_GRABANDO: Grabador = None


def grabar(config: dict) -> dict:
    global _GRABANDO
    codigo = (EJEMPLOS / config["archivo"]).read_text(encoding="utf-8")
    grabador = _GRABANDO = Grabador(config.get("entradas", []), config.get("eventos", []))
    espacio = {"__name__": "__main__", "input": grabador.input}
    tkinter_real = sys.modules.get("tkinter")
    sys.modules["tkinter"] = _tkinter_falso()
    stdout = sys.stdout
    try:
        sys.stdout = grabador
        sys.settrace(grabador.espia)
        exec(compile(codigo, NOMBRE_CODIGO, "exec"), espacio)
    finally:
        sys.settrace(None)
        sys.stdout = stdout
        if tkinter_real is not None:
            sys.modules["tkinter"] = tkinter_real
        else:
            del sys.modules["tkinter"]

    # Último paso: el programa terminó (sin línea resaltada)
    final = {"linea": None, "funcion": None, "pila": [], "locales": None,
             "globales": variables_visibles(espacio), "salida": grabador.caracteres(), "fin": True}
    if grabador.ventana is not None:
        final["ventana"] = grabador.ventana.foto()
    if grabador.tabla is not None:
        final["tabla"] = grabador.tabla
    grabador.pasos.append(final)
    if grabador.entradas:
        raise RuntimeError(f"{config['archivo']}: sobraron entradas sin usar: {grabador.entradas}")

    return {
        "id": config["archivo"][:2],
        "titulo": config["titulo"],
        "idea": config["idea"],
        "archivo": f"lecciones/ejemplos/{config['archivo']}",
        "leccion": config["leccion"],
        "enlace": REPO + config["leccion"],
        "codigo": codigo,
        "salida": grabador.salida,
        "pasos": grabador.pasos,
    }


def grabar_todas() -> list[dict]:
    return [grabar(config) for config in LECCIONES]


if __name__ == "__main__":
    lecciones = grabar_todas()
    SALIDA.write_text(json.dumps(lecciones, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for l in lecciones:
        print(f"✔ {l['archivo']}: {len(l['pasos'])} pasos")
    print(f"✔ {SALIDA}")
