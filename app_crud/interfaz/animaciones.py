"""
animaciones.py — Darle vida a la ventana.
==========================================

¿Cómo se anima algo en tkinter?
    No hay un «animate()». El truco es `widget.after(ms, funcion)`:
    «dentro de X milisegundos, llama a esta función». Si la función se
    vuelve a programar a sí misma, tenemos un CICLO DE ANIMACIÓN:

        paso 0 → after(16) → paso 1 → after(16) → ... → paso final
        (16 ms ≈ 60 cuadros por segundo)

    ⚠️ Nunca usar time.sleep() en una ventana: congela todo el programa.

Una curva de «easing» hace que el movimiento arranque rápido y frene suave,
como los objetos reales. Eso es lo que hace `suavizar()`.
"""

import tkinter as tk

from configuracion import ANIMACIONES_ACTIVAS, COLORES, DURACION_TOAST
from interfaz.estilos import FUENTES, mezclar

CUADRO_MS = 16  # ~60 fps


def suavizar(t: float) -> float:
    """Curva «ease-out cubic»: 0→0, 1→1, pero frena al final."""
    return 1 - (1 - t) ** 3


def animar(widget: tk.Misc, duracion_ms: int, al_avanzar, al_terminar=None) -> None:
    """
    Motor de animación genérico.

    Llama a `al_avanzar(t)` con t yendo de 0.0 a 1.0 durante `duracion_ms`.
    Todas las demás animaciones de este archivo usan esta función.
    """
    if not ANIMACIONES_ACTIVAS:
        al_avanzar(1.0)
        if al_terminar:
            al_terminar()
        return

    pasos = max(1, duracion_ms // CUADRO_MS)

    def paso(numero: int) -> None:
        if not widget.winfo_exists():   # la ventana pudo cerrarse a medio camino
            return
        al_avanzar(suavizar(numero / pasos))
        if numero < pasos:
            widget.after(CUADRO_MS, paso, numero + 1)
        elif al_terminar:
            al_terminar()

    paso(0)


# ---------------------------------------------------------------------------
# ✨ Destello de una fila de la tabla
# ---------------------------------------------------------------------------
def destellar_fila(tabla, iid: str, color: str, duracion_ms: int = 1400) -> None:
    """Pinta la fila del color de la operación y la desvanece a blanco."""
    etiqueta = f"destello_{iid}"
    originales = tabla.item(iid, "tags")   # p. ej. ("par",) para la fila cebra
    tabla.item(iid, tags=(etiqueta,))

    def avanzar(t: float) -> None:
        if tabla.exists(iid):
            tabla.tag_configure(etiqueta, background=mezclar(color, "#FFFFFF", t))

    def terminar() -> None:
        if tabla.exists(iid):
            tabla.item(iid, tags=originales)

    animar(tabla, duracion_ms, avanzar, terminar)


# ---------------------------------------------------------------------------
# 💓 Pulso de color (para las insignias C R U D del encabezado)
# ---------------------------------------------------------------------------
def pulsar(widget: tk.Widget, color_activo: str, color_reposo: str, duracion_ms: int = 900) -> None:
    """Enciende el widget con `color_activo` y lo apaga suavemente."""
    def avanzar(t: float) -> None:
        widget.configure(background=mezclar(color_activo, color_reposo, t))
    animar(widget, duracion_ms, avanzar)


# ---------------------------------------------------------------------------
# 🔢 Contador que «corre» de un número a otro
# ---------------------------------------------------------------------------
def contar_hasta(etiqueta: tk.Label, desde: int, hasta: int, plantilla: str = "{}",
                 duracion_ms: int = 500) -> None:
    def avanzar(t: float) -> None:
        etiqueta.configure(text=plantilla.format(round(desde + (hasta - desde) * t)))
    animar(etiqueta, duracion_ms, avanzar)


# ---------------------------------------------------------------------------
# 🍞 Aviso flotante («toast») que entra deslizándose desde la derecha
# ---------------------------------------------------------------------------
class Toast:
    """
    Un aviso pequeño que aparece abajo a la derecha y se va solo.

    Usa .place() (posición exacta en píxeles) en lugar de .grid()/.pack(),
    porque necesitamos moverlo cuadro por cuadro.
    """

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.marco = tk.Frame(raiz, background=COLORES["crear"], padx=2, pady=2)
        self.etiqueta = tk.Label(self.marco, font=FUENTES["seccion"], foreground="white",
                                 background=COLORES["crear"], padx=18, pady=10, justify="left")
        self.etiqueta.pack()
        self._turno = 0  # evita que un toast viejo cierre a uno nuevo

    def mostrar(self, mensaje: str, color: str) -> None:
        self._turno += 1
        turno = self._turno
        self.marco.configure(background=color)
        self.etiqueta.configure(text=mensaje, background=color)
        self.marco.lift()  # al frente de todo

        # Medimos el aviso para saber dónde ponerlo.
        self.raiz.update_idletasks()
        ancho, alto = self.marco.winfo_reqwidth(), self.marco.winfo_reqheight()
        margen = 24
        x_final = self.raiz.winfo_width() - ancho - margen
        x_inicio = self.raiz.winfo_width() + 10   # empieza fuera de la ventana
        y = self.raiz.winfo_height() - alto - 46

        def entrar(t: float) -> None:
            self.marco.place(x=x_inicio + (x_final - x_inicio) * t, y=y)

        def salir(t: float) -> None:
            if turno == self._turno:
                self.marco.place(x=x_final + (x_inicio - x_final) * t, y=y)

        def programar_salida() -> None:
            def salir_si_sigue_vigente() -> None:
                if turno == self._turno:   # si llegó otro aviso, ese se encarga
                    animar(self.marco, 300, salir)
            self.raiz.after(DURACION_TOAST, salir_si_sigue_vigente)

        animar(self.marco, 350, entrar, programar_salida)


# ---------------------------------------------------------------------------
# ⌨️ Efecto «máquina de escribir»
# ---------------------------------------------------------------------------
class MaquinaDeEscribir:
    """Escribe un texto letra por letra en un tk.Text."""

    def __init__(self, caja: tk.Text, velocidad_ms: int):
        self.caja = caja
        self.velocidad_ms = velocidad_ms
        self._pendiente = None  # id del after() en curso, para poder cancelarlo

    def escribir(self, partes: list[tuple[str, str]]) -> None:
        """
        `partes` es una lista de (texto, etiqueta_de_estilo), por ejemplo:
            [("Creaste ", "normal"), ("un registro", "resaltado")]
        """
        if self._pendiente:
            self.caja.after_cancel(self._pendiente)
        self.caja.configure(state="normal")
        self.caja.delete("1.0", "end")

        # Aplanamos a una lista de (letra, etiqueta).
        letras = [(letra, estilo) for texto, estilo in partes for letra in texto]

        if not ANIMACIONES_ACTIVAS:
            for texto, estilo in partes:
                self.caja.insert("end", texto, estilo)
            self.caja.configure(state="disabled")
            return

        def siguiente(i: int) -> None:
            # Escribimos de 2 en 2 letras para que no sea eterno.
            for letra, estilo in letras[i:i + 2]:
                self.caja.insert("end", letra, estilo)
            self.caja.see("end")   # si el texto no cabe, que se vea lo último
            if i + 2 < len(letras):
                self._pendiente = self.caja.after(self.velocidad_ms, siguiente, i + 2)
            else:
                self._pendiente = None
                self.caja.configure(state="disabled")

        siguiente(0)
