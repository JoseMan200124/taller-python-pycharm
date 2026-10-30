# Guía del instructor

**Taller de Programación de Lenguaje Python con IDE PyCharm**
CRUD con interfaz gráfica conectada a una base de datos SQLite · Grupo de unos 80 alumnos

---

## La idea en una frase

Los alumnos construyen el mismo sistema tres veces, cada vez más completo:

1. **En memoria** (lección 03): entienden el CRUD sin distracciones… y ven que al cerrar se pierde todo.
2. **Con SQLite en consola** (lecciones 04 y 05): los datos sobreviven.
3. **Con ventana** (lecciones 06 y 07): un sistema «de verdad» en un solo archivo.

Al final se abre **`app_crud/`**: el mismo sistema, ordenado en capas, con animaciones y una consola que muestra el SQL de cada clic. Es la «versión profesional» que se proyecta y se recorre juntos.

---

## Agenda completa (4 horas)

| Hora | Bloque | Archivo | Qué hacen los alumnos |
|---|---|---|---|
| 0:00 | Bienvenida y demostración | `app_crud/main.py` | Miran: el instructor crea, edita y borra en la app final. Meta del día: «al terminar, ustedes entienden cada línea de esto». |
| 0:10 | PyCharm en 5 minutos | — | Abrir proyecto, panel de archivos, Run, consola. |
| 0:15 | Hola, Python | `lecciones/01_hola_python.py` | Variables, tipos, f-strings, `input()`. Reto: edad en 2030. |
| 0:30 | Decisiones y validación | `lecciones/02_decisiones_y_validacion.py` | `if`, `while`, `try/except`. **Primer uso del Debug** (F8). |
| 0:45 | CRUD en memoria | `lecciones/03_crud_en_memoria.py` | Listas y diccionarios, menú. Cierran el programa y pierden los datos. |
| 1:10 | **Descanso** | | |
| 1:20 | SQLite primeros pasos | `lecciones/04_sqlite_primeros_pasos.py` | Ejecutan dos veces: los datos siguen ahí. |
| 1:40 | CRUD en consola con SQLite | `lecciones/05_crud_consola_sqlite.py` | Funciones, `with conexion`. **Demo de inyección SQL** (opción 6). |
| 2:05 | Primera ventana | `lecciones/06_primera_ventana.py` | Eventos, `StringVar`, `grid`, `command=`. |
| 2:25 | **Descanso** | | |
| 2:35 | CRUD gráfico en un archivo | `lecciones/07_crud_grafico_un_archivo.py` | El corazón del taller. Lo recorren por bloques numerados. |
| 3:10 | La versión profesional | `app_crud/` | Recorrido de capas + breakpoint en `crear()` siguiendo el dato. |
| 3:35 | Retos | `retos/RETOS.md` | En parejas, nivel a elección. |
| 3:55 | Cierre | | Preguntas y entrega de diplomas. |

### Versión corta (2 h 30 min)

Saltar la lección 03 (mencionarla como tarea), dar la 01 y la 02 juntas en 20 minutos y llegar directo a la 04. El resto igual, sin bloque de retos.

---

## Cómo dar cada bloque

**Patrón para todas las lecciones:**

1. **Proyectar** el archivo y leer el comentario de arriba (los diagramas ASCII están pensados para pantalla grande).
2. **Ejecutar** antes de explicar: que vean el resultado primero.
3. **Recorrer** el código por bloques (cada bloque está separado con `───`).
4. **Reto rápido** al final de cada archivo: 3 a 5 minutos, con cronómetro visible.

**Con 80 personas:**

- Pide que se sienten en **parejas**: uno escribe, el otro lee y revisa. Cambian de rol en cada lección.
- Cada archivo de `lecciones/` es un **punto de control**: quien se atrase abre el siguiente archivo y sigue desde ahí. Nadie se queda fuera.
- Ten 2 o 3 **ayudantes** recorriendo el salón. Señal acordada: la tapa de la laptop a medio cerrar = «necesito ayuda».
- Los errores más comunes a esta escala: indentación, olvidar los paréntesis en `print`, y `command=funcion()` con paréntesis. Anúncialos antes de que pasen.

---

## Momentos clave (los que más se recuerdan)

**1. «Se perdió todo» (lección 03).** Que cada quien cree 2 estudiantes, cierre el programa y lo vuelva a abrir. La frustración es la mejor introducción a la base de datos.

**2. «Los datos sobrevivieron» (lección 04).** Ejecutar dos veces. Mostrar el archivo `leccion04.db` que apareció en el panel de PyCharm.

**3. La inyección SQL (lección 05, opción 6).** Escribir `' OR '1'='1` en vivo. La versión con f-string devuelve **todos** los registros; la versión con `?` devuelve cero. Remata con: «por eso en todo el taller usamos `?`».

**4. Seguir un dato con el Debug (`app_crud/`).**
   - Abrir `app_crud/interfaz/ventana_principal.py` y poner un breakpoint en la primera línea de `crear()`.
   - Ejecutar `main.py` con **Debug** (el insecto).
   - Llenar el formulario y pulsar **Crear**.
   - Avanzar con `F7` (entrar en la función) y `F8` (pasar por encima) por `validaciones.py → repositorio.py → base_datos.py`.
   - En el panel **Variables** se ve el objeto `Estudiante` viajando de una capa a otra.

**5. El Visor de código: ver el programa «por dentro».** Al abrir `app_crud/main.py` aparece una segunda ventana con el código (en pantallas de 1800 px o más se acomoda sola al lado de la app; en pantallas normales flota a la derecha y se puede fijar con «Siempre encima»). Cada botón que pulsas se graba y se reproduce ahí:
   - la **línea que se ejecuta brilla** y las ya ejecutadas quedan con un rastro tenue,
   - las **pestañas** cambian solas de archivo (`ventana_principal.py → validaciones.py → repositorio.py → base_datos.py`) y un punto marca los visitados,
   - abajo se ven la **pila de llamadas** (quién llamó a quién) y las **variables** con su valor en ese momento; en amarillo las que acaban de cambiar,
   - un error (por ejemplo, correo repetido) se pinta en **rojo** y se ve cómo «sube» de `base_datos.py` a `repositorio.py` y a la ventana.

   Controles: `Espacio` pausa, `→` avanza una línea (como F8), y hay velocidad Lento / Normal / Rápido. Sugerencia: pon **Lento** para la primera vez que pulsas «Crear» y narra en voz alta lo que va brillando.

   En la página web (`presentacion/index.html`) el visor arranca en **Paso a paso**: al pulsar un botón se detiene en la primera línea y avanza solo cuando tú quieres (`Siguiente ▸` o `→`; `◂ Atrás` o `←` para regresar; clic en la barra de progreso para saltar). «Reproducir» lo deja correr a la velocidad elegida, `A− / A+` agranda la letra para el proyector y la «Ruta del dato» marca en amarillo la capa de la línea actual.

   Arriba de la app, la sección **«Las lecciones, paso a paso»** tiene un ejemplo corto de cada lección (`lecciones/ejemplos/`) con los mismos controles. Úsala al empezar cada bloque de la agenda: abre la pestaña de la lección, avanza línea por línea y pregunta «¿qué valor tendrá esta variable después de esta línea?» antes de pulsar `Siguiente ▸`. Después los alumnos abren el archivo completo en PyCharm.

   Es el puente perfecto hacia el depurador real: primero lo ven automático en el visor y luego lo hacen ellos con breakpoints. (Mientras se usa el Debug de PyCharm, el visor se pausa solo para no estorbar al depurador.)

**6. La app final como pizarra.** En `app_crud` cada botón:
   - enciende su letra en el semáforo **C R U D** del encabezado,
   - dibuja la **Ruta del dato** (Ventana → Validar → Repositorio → SQL → taller.db),
   - escribe en **«¿Qué acaba de pasar?»** la explicación en español,
   - muestra el SQL exacto en la **Consola SQL en vivo**, con los `?` y los valores aparte.

   Provoca errores a propósito: deja campos vacíos (la ruta se detiene en *Validar*) y repite un correo (se detiene en *SQL* porque SQLite lo rechaza por `UNIQUE`). Así se ve la diferencia entre validar en Python y las reglas de la base de datos.

---

## Arquitectura de `app_crud/` (para proyectar)

```
app_crud/
├── main.py              ▶ arranca todo
├── configuracion.py     colores, rutas, textos, carreras
├── base_datos.py        conexión SQLite + aviso de cada SQL a la consola
├── modelo.py            qué ES un Estudiante (dataclass)
├── repositorio.py       el CRUD: crear, listar, obtener, actualizar, eliminar
├── validaciones.py      revisar los datos antes de guardar
├── datos_ejemplo.py     6 estudiantes de muestra la primera vez
└── interfaz/
    ├── ventana_principal.py   director de orquesta: une las piezas
    ├── encabezado.py          título + semáforo C R U D
    ├── formulario.py          campos y botones
    ├── tabla.py               lista de estudiantes + buscador
    ├── ruta_dato.py           animación del viaje del dato
    ├── pizarra.py             «¿Qué acaba de pasar?»
    ├── consola_sql.py         el SQL en vivo
    ├── grafico.py             barras por carrera (Canvas, sin librerías)
    ├── animaciones.py         motor de animación con after()
    ├── rastreador.py          graba las líneas ejecutadas (sys.settrace)
    ├── visor_codigo.py        ventana tipo PyCharm que las reproduce
    └── estilos.py             el «CSS» de tkinter
```

Regla que conviene repetir: **cada archivo tiene un solo trabajo**. La ventana no sabe SQL; el repositorio no sabe de botones.

### Cómo presentar la división (5 minutos, antes de abrir los archivos)

1. Proyecta la lección 07 y pregunta: *«¿Qué pasa si mañana el jefe dice "cambien a MySQL"?»*. Que respondan: hay que buscar SQL por todo el archivo.
2. Cuenta la analogía del restaurante: el mesero (ventana), el que revisa la orden (validaciones), el cocinero (repositorio), la bodega (base de datos) y la comanda (modelo).
3. Muestra la tabla «Cada pieza ya apareció en una lección»: nada es nuevo, solo está ordenado.
4. Explica los cinco archivos del visor **de abajo hacia arriba** (`modelo → base_datos → repositorio → validaciones → ventana_principal`, solo `crear()`). Luego sigue un clic en el visor **de arriba hacia abajo**.
5. Corre las pruebas y cierra: *«Esto solo se puede hacer porque separamos.»*

La justificación completa (las 13 buenas prácticas y dónde se ve cada una) está en [`ARQUITECTURA.md` → ¿Por qué está dividido así?](ARQUITECTURA.md#por-qué-está-dividido-así).

Para empezar con la base vacía: cerrar la app y borrar `app_crud/taller.db`.

---

## Pruebas automáticas (bonus)

Clic derecho sobre la carpeta `tests` → **Run 'Python tests in tests'**. Son 9 pruebas del CRUD y las validaciones; incluyen una que confirma que la inyección SQL no funciona. Sirve para mostrar que el código profesional se prueba solo.

---

## Lista de verificación previa

- [ ] Enviar a los alumnos `docs/INSTALACION.md` y la carpeta del proyecto **3 días antes**.
- [ ] Pedir que ejecuten `verificar_entorno.py` y que manden captura si sale algo en rojo.
- [ ] Probar el proyector a la resolución real: la app se abre maximizada y está pensada para 1366 × 768 o más.
- [ ] Subir el tamaño de letra del editor de PyCharm para proyectar: **Settings → Editor → Font → 18**.
- [ ] Tener una copia del proyecto en USB por si falla la red.
- [ ] Abrir `presentacion/index.html` en el navegador como apoyo visual (funciona sin internet, salvo las fuentes).
