"""
ventana_principal.py — El «director de orquesta».
==================================================

Esta clase arma la ventana con todas las piezas y decide qué pasa
cuando el usuario hace algo. El recorrido de cada acción es siempre igual:

    ① el usuario hace clic          (formulario.py / tabla.py)
    ② se validan los datos          (validaciones.py)
    ③ se llama al CRUD              (repositorio.py)
    ④ se ejecuta el SQL             (base_datos.py → taller.db)
    ⑤ se refresca y se anima todo   (tabla, gráfico, pizarra, aviso)

🔦 Los métodos marcados con  @mostrar_en_visor  se GRABAN mientras se
   ejecutan y luego se reproducen en el Visor de código (F2), con la
   línea que se ejecuta brillando. Ver rastreador.py y visor_codigo.py.

💡 Para la clase: pon un «breakpoint» (clic en el margen izquierdo de
   PyCharm) en `crear()` y ejecuta con el botón del insecto (Debug).
   Podrás seguir el dato paso a paso por los cinco archivos.
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from base_datos import BaseDatos
from configuracion import COLORES, OPERACIONES, TITULO_APP, VISOR_AL_INICIAR
from repositorio import RepositorioEstudiantes
from validaciones import validar_estudiante
from interfaz.animaciones import Toast, contar_hasta
from interfaz.consola_sql import ConsolaSQL
from interfaz.encabezado import Encabezado
from interfaz.estilos import FUENTES, configurar_estilos
from interfaz.formulario import Formulario
from interfaz.grafico import GraficoCarreras
from interfaz.pizarra import Pizarra
from interfaz.rastreador import Rastreador, mostrar_en_visor
from interfaz.ruta_dato import RutaDelDato
from interfaz.tabla import TablaEstudiantes
from interfaz.visor_codigo import VisorCodigo


class Aplicacion(tk.Tk):
    """La ventana principal. Hereda de tk.Tk, así que ES una ventana."""

    def __init__(self, bd: BaseDatos, repo: RepositorioEstudiantes):
        super().__init__()
        self.bd = bd
        self.repo = repo
        self.id_seleccionado: int | None = None   # ¿qué estudiante se está editando?
        self._total_mostrado = 0

        self.title(TITULO_APP)
        self.geometry("1280x720")
        self.minsize(1120, 660)
        configurar_estilos(self)

        self.rastreador = Rastreador()   # el «espía» que graba las líneas ejecutadas
        self._construir()
        self.visor = VisorCodigo(self)   # ventana aparte con el código
        self._acomodar_ventanas()
        self._atajos_de_teclado()

        # La consola escucha a la base de datos desde AHORA.
        self.bd.agregar_oyente(self.consola.registrar)

        # Primera lectura: llenar tabla, gráfico y contador.
        total = self.refrescar()
        self.pizarra.bienvenida(total)

        # Al cerrar la ventana con la X, cerramos bien la base de datos.
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # =======================================================================
    # 🧱 Construcción de la ventana
    # =======================================================================
    def _construir(self) -> None:
        self.encabezado = Encabezado(self, al_ver_codigo=self.mostrar_visor)
        self.encabezado.pack(fill="x")

        # --- Barra de estado (abajo). Se empaca ANTES que el cuerpo para que
        #     nunca quede aplastada si la ventana es pequeña. -----------------------
        barra = ttk.Frame(self, padding=(16, 0, 16, 10))
        barra.pack(side="bottom", fill="x")
        self.contador = ttk.Label(barra, text="0 estudiantes", style="Barra.TLabel")
        self.contador.pack(side="left")
        ttk.Label(barra, text=f"Base de datos: {self.bd.ruta}", style="Barra.TLabel").pack(side="right")
        ttk.Label(barra, text="Enter = guardar · Esc = limpiar · Supr = eliminar · F2 = código   ",
                  style="Barra.TLabel").pack(side="right")

        cuerpo = ttk.Frame(self, padding=16)
        cuerpo.pack(fill="both", expand=True)
        # Columna 0 = formulario (ancho fijo) · Columna 1 = todo lo demás (se estira).
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        # --- Columna izquierda: el formulario ------------------------------------
        self.formulario = Formulario(
            cuerpo,
            al_crear=self.crear,
            al_actualizar=self.actualizar,
            al_eliminar=self.eliminar,
            al_limpiar=self.limpiar,
        )
        self.formulario.grid(row=0, column=0, sticky="nw", padx=(0, 16))

        # --- Columna derecha (de arriba hacia abajo):
        #     tabla  →  ruta del dato  →  pizarra + pestañas ----------------------
        derecha = ttk.Frame(cuerpo)
        derecha.grid(row=0, column=1, sticky="nsew")
        derecha.columnconfigure(0, weight=2)
        derecha.columnconfigure(1, weight=3)
        derecha.rowconfigure(0, weight=3)   # la tabla se lleva más espacio extra
        derecha.rowconfigure(2, weight=2)

        self.tabla = TablaEstudiantes(derecha, al_seleccionar=self.seleccionar, al_buscar=self.buscar)
        self.tabla.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.ruta = RutaDelDato(derecha)
        self.ruta.grid(row=1, column=0, columnspan=2, sticky="ew", pady=12)

        self.pizarra = Pizarra(derecha)
        self.pizarra.grid(row=2, column=0, sticky="nsew", padx=(0, 16))

        pestanas = ttk.Notebook(derecha)
        pestanas.grid(row=2, column=1, sticky="nsew")
        self.consola = ConsolaSQL(pestanas)
        self.grafico = GraficoCarreras(pestanas)
        pestanas.add(self.consola, text=" Consola SQL ")
        pestanas.add(self.grafico, text=" Por carrera ")

        self.toast = Toast(self)

    def _acomodar_ventanas(self) -> None:
        """
        Pantalla ancha (≥ 1800 px): app a la izquierda y visor a la derecha.
        Pantalla normal: app maximizada y el visor flotando a la derecha
        (muévelo, achícalo, fíjalo «siempre encima» o ciérralo; F2 lo vuelve a abrir).
        """
        ancho, alto = self.winfo_screenwidth(), self.winfo_screenheight()
        if ancho >= 1800:
            ancho_visor = min(820, ancho - 1150)
            self.geometry(f"{ancho - ancho_visor - 12}x{alto - 110}+0+0")
            self.visor.geometry(f"{ancho_visor}x{alto - 110}+{ancho - ancho_visor}+0")
        else:
            self._maximizar()
            ancho_visor = min(700, ancho // 2)
            self.visor.geometry(f"{ancho_visor}x{min(alto - 120, 840)}+{ancho - ancho_visor - 10}+40")
        if not VISOR_AL_INICIAR:
            self.visor.withdraw()

    def mostrar_visor(self) -> None:
        """F2 o botón «Ver código»: abre el visor y lo trae al frente (se cierra con su X)."""
        self.visor.deiconify()
        self.visor.lift()

    def _maximizar(self) -> None:
        """Abre la ventana maximizada (ideal para proyectar en clase)."""
        try:
            self.state("zoomed")                # Windows y macOS
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)  # Linux
            except tk.TclError:
                pass                            # si no se puede, se queda en 1280x720

    def _atajos_de_teclado(self) -> None:
        # bind() conecta una tecla con una función.
        self.bind("<Return>", lambda _e: self.actualizar() if self.id_seleccionado else self.crear())
        self.bind("<Escape>", lambda _e: self.limpiar())
        self.bind("<F2>", lambda _e: self.mostrar_visor())
        self.bind("<Delete>", self._suprimir)

    def _suprimir(self, evento) -> None:
        # Si el cursor está dentro de un campo de texto, Supr borra letras, no estudiantes.
        if self.id_seleccionado and not isinstance(evento.widget, (tk.Entry, ttk.Entry)):
            self.eliminar()

    # =======================================================================
    # 🔁 Refrescar: volver a leer la BD y pintar todo
    # =======================================================================
    def refrescar(self, busqueda: str = "", con_grafico: bool = True) -> int:
        """Relee la BD y repinta. `con_grafico=False` en búsquedas: los datos no cambiaron."""
        # Si hay búsqueda, el SELECT es la acción principal; si no, es un simple refresco.
        with self.bd.motivo(None if busqueda else "refresco"):
            if con_grafico:
                self.grafico.actualizar(self.repo.contar_por_carrera())
            estudiantes = self.repo.listar(busqueda)
        self.tabla.mostrar(estudiantes)

        total = len(estudiantes)
        plantilla = "{} estudiantes" if not busqueda else "{} coincidencias"
        contar_hasta(self.contador, self._total_mostrado, total, plantilla)
        self._total_mostrado = total
        return total

    # =======================================================================
    # C — CREAR
    # =======================================================================
    @mostrar_en_visor
    def crear(self) -> None:
        estudiante, errores = validar_estudiante(self.formulario.leer())
        if errores:
            self.formulario.mostrar_errores(errores)
            self.ruta.recorrer(COLORES["error"], hasta=1, fallo=True)   # se frena en «Validar»
            self._avisar_error("Revisa los campos en rojo",
                               "La validación detuvo el guardado ANTES de llegar a la base de datos. "
                               "Así protegemos los datos.")
            return
        try:
            nuevo_id = self.repo.crear(estudiante)
        except sqlite3.IntegrityError:
            # UNIQUE en la columna correo: SQLite no deja repetirlo.
            self.formulario.mostrar_errores({"correo": "Ese correo ya está registrado."})
            self.ruta.recorrer(COLORES["error"], hasta=3, fallo=True)   # SQLite lo rechazó
            self._avisar_error("SQLite dijo que no",
                               "La columna «correo» es UNIQUE: no puede haber dos iguales. "
                               "Mira el error en la Consola SQL.")
            return

        self._celebrar("INSERT", f"✓ {estudiante.nombre} creado (#{nuevo_id})")
        self.ruta.recorrer(COLORES["crear"])
        if self.tabla.busqueda.get():
            self.tabla.busqueda.set("")      # quitar el filtro también refresca la tabla
        else:
            self.refrescar()
        self.tabla.destellar(nuevo_id, COLORES["crear"])
        self.formulario.vaciar()
        self.pizarra.explicar_crear(estudiante, nuevo_id)

    # =======================================================================
    # R — LEER (seleccionar una fila / buscar)
    # =======================================================================
    @mostrar_en_visor
    def seleccionar(self, id_estudiante: int) -> None:
        estudiante = self.repo.obtener(id_estudiante)
        if estudiante is None:
            return
        self.id_seleccionado = id_estudiante
        self.formulario.cargar(estudiante)
        self.encabezado.encender("SELECT")
        self.ruta.recorrer(COLORES["leer"], saltar={1})   # leer no necesita validar
        self.pizarra.explicar_leer(estudiante)

    @mostrar_en_visor
    def buscar(self, texto: str) -> None:
        total = self.refrescar(texto, con_grafico=False)
        if texto:
            self.encabezado.encender("SELECT")
            self.ruta.recorrer(COLORES["leer"], saltar={1})
            self.pizarra.explicar_busqueda(texto, total)

    # =======================================================================
    # U — ACTUALIZAR
    # =======================================================================
    @mostrar_en_visor
    def actualizar(self) -> None:
        if not self.id_seleccionado:
            return
        estudiante, errores = validar_estudiante(self.formulario.leer())
        if errores:
            self.formulario.mostrar_errores(errores)
            self.ruta.recorrer(COLORES["error"], hasta=1, fallo=True)
            self._avisar_error("Revisa los campos en rojo", "No se envió ningún UPDATE.")
            return

        anterior = self.repo.obtener(self.id_seleccionado)
        estudiante.id = self.id_seleccionado
        try:
            self.repo.actualizar(estudiante)
        except sqlite3.IntegrityError:
            self.formulario.mostrar_errores({"correo": "Ese correo ya lo usa otro estudiante."})
            self.ruta.recorrer(COLORES["error"], hasta=3, fallo=True)
            self._avisar_error("SQLite dijo que no", "El correo debe ser único (UNIQUE).")
            return

        # ¿Qué cambió? Comparamos campo por campo el antes y el después.
        cambios = [campo for campo in ("nombre", "correo", "telefono", "edad", "carrera")
                   if getattr(anterior, campo) != getattr(estudiante, campo)]

        self._celebrar("UPDATE", f"✎ {estudiante.nombre} actualizado")
        self.ruta.recorrer(COLORES["actualizar"])
        self.refrescar(self.tabla.busqueda.get().strip())
        self.tabla.destellar(estudiante.id, COLORES["actualizar"])
        self.pizarra.explicar_actualizar(estudiante, cambios)
        self.limpiar(explicar=False)

    # =======================================================================
    # D — ELIMINAR
    # =======================================================================
    @mostrar_en_visor
    def eliminar(self) -> None:
        if not self.id_seleccionado:
            return
        estudiante = self.repo.obtener(self.id_seleccionado)
        if estudiante is None:
            return
        # Siempre pedir confirmación antes de borrar.
        if not messagebox.askyesno("Eliminar estudiante",
                                   f"¿Seguro que quieres eliminar a «{estudiante.nombre}»?\n\n"
                                   "Esta acción no se puede deshacer.", icon="warning", parent=self):
            return

        self.repo.eliminar(estudiante.id)
        self._celebrar("DELETE", f"✕ {estudiante.nombre} eliminado")
        self.ruta.recorrer(COLORES["eliminar"], saltar={1})
        self.limpiar(explicar=False)
        self.refrescar(self.tabla.busqueda.get().strip())
        self.pizarra.explicar_eliminar(estudiante.nombre, estudiante.id)

    # =======================================================================
    # 🧹 Utilidades
    # =======================================================================
    def limpiar(self, explicar: bool = True) -> None:
        self.id_seleccionado = None
        self.tabla.quitar_seleccion()
        self.formulario.vaciar()
        if explicar:
            self.pizarra.explicar("SELECT", [
                ("Formulario listo\n", "SELECT"),
                ("Limpiar no toca la base de datos: solo vacía los campos de la pantalla.", "normal"),
            ])

    def _celebrar(self, operacion: str, mensaje: str) -> None:
        """Feedback visual de éxito: insignia que pulsa + aviso flotante."""
        self.encabezado.encender(operacion)
        self.toast.mostrar(mensaje, OPERACIONES[operacion]["color"])

    def _avisar_error(self, titulo: str, explicacion: str) -> None:
        self.toast.mostrar(f"⚠ {titulo}", COLORES["error"])
        self.pizarra.explicar_error(titulo, explicacion)

    def _cerrar(self) -> None:
        self.bd.cerrar()
        self.destroy()
