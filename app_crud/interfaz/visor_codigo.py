"""
visor_codigo.py — Una ventana tipo PyCharm donde BRILLA la línea que se ejecuta.
=================================================================================

    ┌─ Visor de código ──────────── ↺ Repetir  ‖ Pausa  Línea ▸  Velocidad ┐
    │ ventana_principal.py ● │ validaciones.py │ repositorio.py ● │ ... │  ← pestañas
    │  148  def crear(self) -> None:                                   │
    │  149      estudiante, errores = validar_estudiante(...)  ◄ brilla│  ← editor
    │  150      if errores:                                            │
    ├─ Pila de llamadas ──────────────┬─ Variables ────────────────────┤
    │ ▶ repositorio.crear             │ estudiante = Estudiante(...)   │  ← como el
    │   ventana_principal.crear       │ nuevo_id = 7                   │    Debug de
    ├─────────────────────────────────┴────────────────────────────────┤    PyCharm
    │ Paso 12 de 48 · repositorio.py:45 · crear()                       │
    └───────────────────────────────────────────────────────────────────┘

¿De dónde salen las líneas? De rastreador.py: cada botón se ejecuta con un
«espía» (sys.settrace) que anota cada línea real. Aquí solo REPRODUCIMOS
esa grabación, despacio, para que el ojo la pueda seguir.

Colores:
    línea que brilla   → la que se está ejecutando ahora
    rastro tenue       → líneas que ya se ejecutaron en este recorrido
    fondo rojo         → ahí ocurrió un error (por ejemplo, correo repetido)
"""

import io
import keyword
import tkinter as tk
import tokenize
from pathlib import Path
from tkinter import font as tkfont

from configuracion import CARPETA_APP, COLORES, VISOR_MS_POR_LINEA
from interfaz.animaciones import animar
from interfaz.estilos import FUENTES, mezclar
from interfaz.rastreador import ARCHIVOS_VISIBLES, Paso

C = COLORES  # abreviatura: en este archivo se usan muchos colores
ANCHO_MARGEN = 6  # «  148 » → los números de línea ocupan 6 caracteres

# Color de cada operación (el nombre del método decorado → color del CRUD).
COLOR_OPERACION = {
    "crear": C["crear"],
    "seleccionar": C["leer"],
    "buscar": C["leer"],
    "actualizar": C["actualizar"],
    "eliminar": C["eliminar"],
}

FUNCIONES_INTEGRADAS = {"print", "len", "int", "str", "float", "bool", "list", "dict", "tuple",
                        "set", "range", "enumerate", "zip", "isinstance", "getattr", "repr",
                        "round", "max", "min", "next", "super", "any", "all", "reversed"}
LITERALES = {"True", "False", "None"}

# En Python 3.12+ las f-strings se parten en varias piezas al «tokenizar».
TIPOS_CADENA = {tokenize.STRING} | {getattr(tokenize, nombre) for nombre in
                                    ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END")
                                    if hasattr(tokenize, nombre)}


def _apto_para_tk(codigo: str) -> str:
    """
    tkinter (Tk 8.6) no dibuja bien los emojis de los comentarios: salen como cuadritos
    y descuadran las columnas del coloreado. Los cambiamos por un punto «•».
    (Cada emoji es UN carácter de Python → el punto ocupa el mismo lugar.)
    """
    return "".join("•" if ord(letra) > 0xFFFF else letra
                   for letra in codigo.replace("\ufe0f", ""))


class VisorCodigo(tk.Toplevel):
    """Ventana aparte (Toplevel) que se puede mover a otra pantalla o al proyector."""

    def __init__(self, raiz: tk.Tk):
        super().__init__(raiz)
        self.title("Visor de código — así se ejecuta tu programa")
        self.configure(background=C["editor_fondo"])
        self.minsize(560, 480)
        # Cerrar con la X solo la ESCONDE; se vuelve a abrir con F2 o «Ver código».
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        # --- Estado de la reproducción -----------------------------------------
        self._pasos: list[Paso] = []
        self._indice = -1
        self._operacion = ""
        self._color = C["leer"]
        self._pendiente = None      # id del after() programado
        self._pausado = False
        self._visitados: set[str] = set()   # archivos por los que ya pasó el recorrido
        self.ms_por_linea = tk.IntVar(value=VISOR_MS_POR_LINEA)

        fuente = tkfont.Font(font=FUENTES["editor"])
        self._alto_linea = fuente.metrics("linespace") + 2

        # --- Construcción (de arriba hacia abajo) ------------------------------
        self._construir_barra_superior()
        self._construir_pestanas()
        self._construir_estado()           # se empaca abajo antes que el resto
        self._construir_panel_depuracion()
        self._construir_editores()

        self.bind("<space>", lambda _e: self.pausar_o_seguir())
        self.bind("<Right>", lambda _e: self.paso_siguiente())

        self._mostrar_pestana(ARCHIVOS_VISIBLES[0])
        self._escribir_estado("Pulsa un botón en la app (Crear, clic en una fila, Buscar…) "
                              "y aquí verás, línea por línea, el código que se ejecuta.")

    # =======================================================================
    # 🧱 Construcción
    # =======================================================================
    def _boton(self, padre, texto: str, comando) -> tk.Button:
        boton = tk.Button(padre, text=texto, command=comando, font=FUENTES["seccion"],
                          foreground=C["editor_texto"], background=C["editor_barra"],
                          activebackground=C["editor_borde"], activeforeground="white",
                          relief="flat", borderwidth=0, padx=10, pady=2, cursor="hand2")
        boton.pack(side="left", padx=2)
        return boton

    def _construir_barra_superior(self) -> None:
        barra = tk.Frame(self, background=C["editor_barra"], padx=14, pady=8)
        barra.pack(fill="x")

        tk.Label(barra, text="</>", font=FUENTES["insignia"], foreground=C["amarillo"],
                 background=C["editor_barra"]).pack(side="left")
        textos = tk.Frame(barra, background=C["editor_barra"])
        textos.pack(side="left", padx=10)
        self.titulo = tk.Label(textos, text="Visor de código", font=FUENTES["seccion"],
                               foreground="white", background=C["editor_barra"])
        self.titulo.pack(anchor="w")
        tk.Label(textos, text="Espacio = pausa · → = una línea", font=FUENTES["pequena"],
                 foreground=C["editor_comentario"], background=C["editor_barra"]).pack(anchor="w")

        controles = tk.Frame(barra, background=C["editor_barra"])
        controles.pack(side="right")
        self._boton(controles, "↺ Repetir", self.repetir)
        self.boton_pausa = self._boton(controles, "‖ Pausa", self.pausar_o_seguir)
        self._boton(controles, "Línea ▸", self.paso_siguiente)   # avanza una sola línea

        # Segunda fila: opciones (velocidad y «siempre encima»).
        opciones = tk.Frame(self, background=C["editor_barra"], padx=14)
        opciones.pack(fill="x")
        opciones_der = tk.Frame(opciones, background=C["editor_barra"])
        opciones_der.pack(side="right", pady=(0, 6))
        controles = opciones_der   # lo que sigue se acomoda en esta fila

        # «Siempre encima»: útil en pantallas chicas, donde el visor tapa parte de la app.
        self.encima = tk.BooleanVar(value=False)
        tk.Checkbutton(controles, text="Siempre encima", variable=self.encima,
                       command=lambda: self.attributes("-topmost", self.encima.get()),
                       font=FUENTES["pequena"], foreground=C["editor_texto"], background=C["editor_barra"],
                       selectcolor=C["editor_fondo"], activebackground=C["editor_barra"],
                       activeforeground="white", highlightthickness=0, borderwidth=0,
                       cursor="hand2").pack(side="left", padx=(10, 0))

        # Velocidad: tres botones tipo «interruptor» que comparten la misma variable.
        tk.Label(controles, text="   Velocidad:", font=FUENTES["pequena"], foreground=C["editor_comentario"],
                 background=C["editor_barra"]).pack(side="left")
        velocidades = tk.Frame(controles, background=C["editor_fondo"], padx=2, pady=2)
        velocidades.pack(side="left", padx=(6, 0))
        for texto, ms in (("Lento", 700), ("Normal", VISOR_MS_POR_LINEA), ("Rápido", 70)):
            tk.Radiobutton(velocidades, text=texto, value=ms, variable=self.ms_por_linea,
                           indicatoron=False, font=FUENTES["pequena"], padx=6, pady=3,
                           foreground=C["editor_texto"], background=C["editor_fondo"],
                           selectcolor=C["editor_borde"], activebackground=C["editor_borde"],
                           activeforeground="white", relief="flat", borderwidth=0,
                           offrelief="flat", cursor="hand2").pack(side="left")

    def _construir_pestanas(self) -> None:
        """Una pestaña por archivo. Un punto de color marca las que se visitaron."""
        barra = tk.Frame(self, background=C["editor_barra"])
        barra.pack(fill="x")
        self._pestanas: dict[str, dict] = {}
        for ruta in ARCHIVOS_VISIBLES:
            marco = tk.Frame(barra, background=C["editor_barra"], cursor="hand2")
            marco.pack(side="left")
            fila = tk.Frame(marco, background=C["editor_barra"])
            fila.pack(padx=9, pady=(6, 4))
            nombre = tk.Label(fila, text=Path(ruta).name, font=FUENTES["codigo"],
                              foreground=C["editor_comentario"], background=C["editor_barra"])
            nombre.pack(side="left")
            punto = tk.Label(fila, text="●", font=FUENTES["pequena"],
                             foreground=C["editor_barra"], background=C["editor_barra"])
            punto.pack(side="left", padx=(4, 0))
            subrayado = tk.Frame(marco, height=3, background=C["editor_barra"])
            subrayado.pack(fill="x")
            for widget in (marco, fila, nombre, punto):
                widget.bind("<Button-1>", lambda _e, r=ruta: self._mostrar_pestana(r))
            self._pestanas[ruta] = {"widgets": (marco, fila, nombre, punto),
                                    "nombre": nombre, "punto": punto, "subrayado": subrayado}

    def _construir_editores(self) -> None:
        """Un tk.Text por archivo, todos apilados en la misma celda (se «levanta» el visible)."""
        contenedor = tk.Frame(self, background=C["editor_fondo"])
        contenedor.pack(fill="both", expand=True)
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)

        self._editores: dict[str, tk.Text] = {}
        self._marcos: dict[str, tk.Frame] = {}
        for ruta in ARCHIVOS_VISIBLES:
            marco = tk.Frame(contenedor, background=C["editor_fondo"])
            marco.grid(row=0, column=0, sticky="nsew")
            texto = tk.Text(marco, font=FUENTES["editor"], wrap="none", background=C["editor_fondo"],
                            foreground=C["editor_texto"], relief="flat", borderwidth=0,
                            highlightthickness=0, padx=4, pady=8, cursor="arrow",
                            spacing1=1, spacing3=1, insertwidth=0,
                            selectbackground=C["editor_borde"])
            barra = tk.Scrollbar(marco, orient="vertical", command=texto.yview)
            texto.configure(yscrollcommand=barra.set)
            barra.pack(side="right", fill="y")
            texto.pack(side="left", fill="both", expand=True)

            self._configurar_etiquetas(texto)
            self._cargar_codigo(texto, CARPETA_APP / ruta)
            self._editores[ruta] = texto
            self._marcos[ruta] = marco

    def _construir_panel_depuracion(self) -> None:
        """Abajo: Pila de llamadas y Variables, como el panel Debug de PyCharm."""
        panel = tk.Frame(self, background=C["editor_borde"])
        panel.pack(side="bottom", fill="x")
        panel.columnconfigure(0, weight=2)
        panel.columnconfigure(1, weight=3)

        self.pila = self._caja_depuracion(panel, 0, "Pila de llamadas  (¿quién llamó a quién?)")
        self.variables = self._caja_depuracion(panel, 1, "Variables  (valores en este momento)")

    def _caja_depuracion(self, padre, columna: int, titulo: str) -> tk.Text:
        marco = tk.Frame(padre, background=C["editor_barra"], padx=12, pady=6)
        marco.grid(row=0, column=columna, sticky="nsew", padx=(0, 1) if columna == 0 else 0, pady=(1, 0))
        tk.Label(marco, text=titulo, font=FUENTES["pequena"], foreground=C["editor_comentario"],
                 background=C["editor_barra"]).pack(anchor="w")
        caja = tk.Text(marco, height=6, width=30, font=FUENTES["codigo"], wrap="none",
                       background=C["editor_barra"], foreground=C["editor_texto"], relief="flat",
                       borderwidth=0, highlightthickness=0, cursor="arrow", state="disabled")
        caja.pack(fill="both", expand=True)
        caja.tag_configure("actual", foreground="white", font=FUENTES["codigo_negrita"])
        caja.tag_configure("suave", foreground=C["editor_comentario"])
        caja.tag_configure("nombre", foreground=C["editor_definicion"])
        caja.tag_configure("cambio", foreground=C["amarillo"], font=FUENTES["codigo_negrita"])
        return caja

    def _construir_estado(self) -> None:
        marco = tk.Frame(self, background=C["editor_barra"])
        marco.pack(side="bottom", fill="x")
        # Barra de progreso dibujada en un Canvas de 4 px de alto.
        self.progreso = tk.Canvas(marco, height=4, background=C["editor_fondo"], highlightthickness=0)
        self.progreso.pack(fill="x")
        self.estado = tk.Label(marco, text="", anchor="w", justify="left", font=FUENTES["pequena"],
                               foreground=C["editor_texto"], background=C["editor_barra"],
                               padx=14, pady=6, wraplength=900)
        self.estado.pack(fill="x")
        marco.bind("<Configure>", lambda e: self.estado.configure(wraplength=e.width - 28))

    # =======================================================================
    # 🎨 Resaltado de sintaxis
    # =======================================================================
    @staticmethod
    def _configurar_etiquetas(texto: tk.Text) -> None:
        texto.tag_configure("margen", foreground=C["editor_numero"])
        for etiqueta, color in (("clave", "editor_clave"), ("cadena", "editor_cadena"),
                                ("comentario", "editor_comentario"), ("literal", "editor_literal"),
                                ("definicion", "editor_definicion"), ("self", "editor_self"),
                                ("integrada", "editor_integrada"), ("decorador", "editor_decorador")):
            texto.tag_configure(etiqueta, foreground=C[color])
        texto.tag_configure("comentario", font=FUENTES["editor_cursiva"])
        # El orden importa: las etiquetas creadas después se pintan ENCIMA.
        texto.tag_configure("ejecutada", background=C["editor_fondo"])
        texto.tag_configure("activa", background=C["editor_borde"])
        texto.tag_configure("error", background=C["eliminar"], foreground="white")
        texto.tag_configure("num_activo", foreground=C["amarillo"], font=FUENTES["editor_negrita"])
        # Un texto de varias líneas (docstring) también pinta los números de en medio;
        # subimos «margen» por encima de los colores para que los números sigan grises.
        texto.tag_raise("margen")
        texto.tag_raise("num_activo")

    @staticmethod
    def _cargar_codigo(texto: tk.Text, ruta: Path) -> None:
        """Lee el archivo, le pone números de línea y colorea con el módulo tokenize."""
        codigo = _apto_para_tk(ruta.read_text(encoding="utf-8"))
        for numero, linea in enumerate(codigo.splitlines(), start=1):
            texto.insert("end", f"{numero:>4}  ", "margen")
            texto.insert("end", linea + "\n")

        # tokenize parte el código en «fichas»: palabras, textos, números, comentarios...
        # Es lo mismo que usa PyCharm (en versión más sofisticada) para colorear.
        anterior = None
        try:
            for ficha in tokenize.generate_tokens(io.StringIO(codigo).readline):
                etiqueta = None
                if ficha.type == tokenize.COMMENT:
                    etiqueta = "comentario"
                elif ficha.type in TIPOS_CADENA:
                    etiqueta = "cadena"
                elif ficha.type == tokenize.NUMBER:
                    etiqueta = "literal"
                elif ficha.type == tokenize.NAME:
                    if anterior in ("def", "class"):
                        etiqueta = "definicion"
                    elif anterior == "@":
                        etiqueta = "decorador"
                    elif ficha.string in LITERALES:
                        etiqueta = "literal"
                    elif keyword.iskeyword(ficha.string):
                        etiqueta = "clave"
                    elif ficha.string in ("self", "cls"):
                        etiqueta = "self"
                    elif ficha.string in FUNCIONES_INTEGRADAS:
                        etiqueta = "integrada"
                elif ficha.type == tokenize.OP and ficha.string == "@":
                    etiqueta = "decorador"

                if etiqueta:
                    (fila_ini, col_ini), (fila_fin, col_fin) = ficha.start, ficha.end
                    texto.tag_add(etiqueta, f"{fila_ini}.{col_ini + ANCHO_MARGEN}",
                                  f"{fila_fin}.{col_fin + ANCHO_MARGEN}")
                if ficha.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                                      tokenize.DEDENT, tokenize.COMMENT):
                    anterior = ficha.string
        except (tokenize.TokenError, SyntaxError):
            pass  # si algo no se puede colorear, se ve sin color: no pasa nada

        texto.configure(state="disabled")  # solo lectura

    # =======================================================================
    # ▶ Reproducción
    # =======================================================================
    def reproducir(self, pasos: list[Paso], operacion: str) -> None:
        """Empieza a mostrar una grabación nueva (la llama el decorador @mostrar_en_visor)."""
        self._cancelar()
        self._pasos, self._indice, self._operacion = pasos, -1, operacion
        self._color = COLOR_OPERACION.get(operacion, C["leer"])
        self._pausado = False
        self.boton_pausa.configure(text="‖ Pausa")
        self.titulo.configure(text=f"Visor de código · {operacion}()", foreground=self._color)

        # Limpiar el recorrido anterior.
        for texto in self._editores.values():
            for etiqueta in ("ejecutada", "activa", "num_activo", "error"):
                texto.tag_remove(etiqueta, "1.0", "end")
            texto.tag_configure("ejecutada", background=mezclar(self._color, C["editor_fondo"], 0.84))
        self._visitados.clear()

        if not pasos:
            self._escribir_estado("Esta acción no ejecutó líneas de los archivos del visor.")
            return
        self._avanzar()

    def pausar_o_seguir(self) -> None:
        if not self._pasos:
            return
        if self._indice >= len(self._pasos) - 1:      # ya terminó → repetir
            self.repetir()
            return
        self._pausado = not self._pausado
        self.boton_pausa.configure(text="▶ Seguir" if self._pausado else "‖ Pausa")
        if self._pausado:
            self._cancelar()
        else:
            self._avanzar()

    def paso_siguiente(self) -> None:
        """Avanza UNA línea y deja la reproducción en pausa (como F8 en el Debug)."""
        if not self._pasos:
            return
        self._pausado = True
        self.boton_pausa.configure(text="▶ Seguir")
        self._cancelar()
        self._avanzar()

    def repetir(self) -> None:
        if self._pasos:
            self.reproducir(self._pasos, self._operacion)

    def _avanzar(self) -> None:
        self._pendiente = None
        if self._indice + 1 >= len(self._pasos):
            self._terminar()
            return
        self._indice += 1
        paso = self._pasos[self._indice]
        self._mostrar_paso(paso)
        if not self._pausado:
            # En notas y errores nos detenemos un poco más, para que se alcancen a leer.
            espera = self.ms_por_linea.get() * (5 if (paso.nota or paso.es_error) else 1)
            self._pendiente = self.after(espera, self._avanzar)

    def _terminar(self) -> None:
        self.boton_pausa.configure(text="↺ Otra vez")
        archivos = len({p.archivo for p in self._pasos})
        self._escribir_estado(f"✓ Recorrido completo: {len(self._pasos)} líneas ejecutadas en "
                              f"{archivos} archivos. Pulsa «Otra vez» para repetirlo.")

    def _cancelar(self) -> None:
        if self._pendiente:
            self.after_cancel(self._pendiente)
            self._pendiente = None

    # =======================================================================
    # 🔦 Mostrar un paso
    # =======================================================================
    def _mostrar_paso(self, paso: Paso) -> None:
        texto = self._editores[paso.archivo]
        self._visitados.add(paso.archivo)
        self._mostrar_pestana(paso.archivo)

        for editor in self._editores.values():
            editor.tag_remove("activa", "1.0", "end")
            editor.tag_remove("num_activo", "1.0", "end")

        inicio = f"{paso.linea}.0"
        fin = f"{paso.linea}.0 lineend +1c"   # +1c incluye el salto de línea → el brillo llega al borde
        texto.tag_add("ejecutada", inicio, fin)
        texto.tag_add("activa", inicio, fin)
        texto.tag_add("num_activo", inicio, f"{paso.linea}.{ANCHO_MARGEN}")
        if paso.es_error:
            texto.tag_add("error", inicio, fin)

        # ✨ Brillo: la línea se enciende fuerte y baja a un tono medio.
        fuerte = mezclar(self._color, C["editor_fondo"], 0.25)
        medio = mezclar(self._color, C["editor_fondo"], 0.58)
        duracion = min(260, self.ms_por_linea.get())
        animar(texto, duracion, lambda t: texto.tag_configure("activa", background=mezclar(fuerte, medio, t)))

        self._centrar(texto, paso.linea)
        self._pintar_pila(paso)
        self._pintar_variables(paso)

        archivo = Path(paso.archivo).name
        detalle = f"   {paso.nota}" if paso.nota else ""
        self._escribir_estado(f"Paso {self._indice + 1} de {len(self._pasos)}   ·   "
                              f"{archivo}, línea {paso.linea}   ·   dentro de {paso.funcion}(){detalle}")

    def _centrar(self, texto: tk.Text, linea: int) -> None:
        """Desplaza el editor (suavemente) para que la línea quede a media altura."""
        total = int(texto.index("end-1c").split(".")[0])
        visibles = max(1, texto.winfo_height() // self._alto_linea)
        destino = max(0.0, (linea - visibles / 2 - 1) / total)
        origen = texto.yview()[0]
        if abs(destino - origen) * total < 1:
            return
        animar(texto, 180, lambda t: texto.yview_moveto(origen + (destino - origen) * t))

    def _pintar_pila(self, paso: Paso) -> None:
        caja = self.pila
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        # La más reciente arriba, como en PyCharm.
        for posicion, funcion in enumerate(reversed(paso.pila)):
            if posicion == 0:
                caja.insert("end", f"▶ {funcion}\n", "actual")
            else:
                caja.insert("end", f"  {funcion}\n", "suave")
        caja.configure(state="disabled")

    def _pintar_variables(self, paso: Paso) -> None:
        anterior = self._pasos[self._indice - 1].variables if self._indice > 0 else {}
        caja = self.variables
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        if not paso.variables:
            caja.insert("end", "(sin variables locales todavía)", "suave")
        for nombre, valor in paso.variables.items():
            caja.insert("end", nombre, "nombre")
            caja.insert("end", " = ")
            # En amarillo las variables que acaban de aparecer o cambiar.
            caja.insert("end", f"{valor}\n", "cambio" if anterior.get(nombre) != valor else ())
        caja.configure(state="disabled")

    # =======================================================================
    # 🗂️ Pestañas y estado
    # =======================================================================
    def _mostrar_pestana(self, ruta: str) -> None:
        self._marcos[ruta].tkraise()
        for otra, pestana in self._pestanas.items():
            activa = otra == ruta
            fondo = C["editor_fondo"] if activa else C["editor_barra"]
            for widget in pestana["widgets"]:
                widget.configure(background=fondo)
            pestana["nombre"].configure(foreground="white" if activa else C["editor_comentario"])
            # El punto se ve solo en los archivos visitados (si no, toma el color del fondo).
            pestana["punto"].configure(foreground=self._color if otra in self._visitados else fondo)
            pestana["subrayado"].configure(background=self._color if activa else C["editor_barra"])

    def _escribir_estado(self, mensaje: str) -> None:
        self.estado.configure(text=mensaje)
        self.progreso.delete("all")
        if self._pasos:
            ancho = self.progreso.winfo_width() * (self._indice + 1) / len(self._pasos)
            self.progreso.create_rectangle(0, 0, ancho, 4, fill=self._color, outline="")
