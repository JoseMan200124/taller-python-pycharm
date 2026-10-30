/*
 * motor.js — Reproduce, línea por línea, lo que hace el código Python de app_crud/.
 * ===============================================================================
 *
 * En la app de escritorio, las líneas se graban con sys.settrace. En el navegador
 * no hay Python, así que este motor «camina» por el MISMO código fuente (que se
 * inserta en la página con construir.py) siguiendo la misma lógica:
 *
 *     P('if errores:')   →  busca esa línea en el archivo real, a partir de donde va
 *                            la función, y anota un Paso con su número de línea,
 *                            la pila de llamadas y las variables locales.
 *
 * Cada función de Python tiene aquí su «gemela» en JavaScript que llama a P()
 * en el mismo orden en que Python ejecutaría las líneas.
 * Si alguien cambia el código Python y una línea ya no existe, se avisa en la
 * consola del navegador (Motor.faltantes) en lugar de romperse.
 */
const Motor = (() => {
  "use strict";

  // ───────────────────────── Código fuente y búsqueda de líneas ─────────────────
  let LINEAS = {};
  const faltantes = [];

  function cargarFuentes(fuentes) {
    LINEAS = {};
    for (const ruta in fuentes) LINEAS[ruta] = fuentes[ruta].split("\n");
  }

  function lineaDef(ruta, fn) {
    const i = LINEAS[ruta].findIndex((l) => l.trimStart().startsWith(`def ${fn}(`));
    return i + 1;
  }

  function buscarLinea(ruta, desde, texto) {
    const lineas = LINEAS[ruta];
    for (let i = desde - 1; i < lineas.length; i++) if (lineas[i].includes(texto)) return i + 1;
    return null;
  }

  // ───────────────────────── repr() al estilo Python ────────────────────────────
  function pyrepr(v, profundidad = 0) {
    if (v === null || v === undefined) return "None";
    if (v === true) return "True";
    if (v === false) return "False";
    if (typeof v === "number") return String(v);
    if (typeof v === "string") return "'" + v.replace(/\\/g, "\\\\").replace(/'/g, "\\'") + "'";
    if (profundidad > 2) return "...";
    if (Array.isArray(v)) return "[" + v.map((x) => pyrepr(x, profundidad + 1)).join(", ") + "]";
    if (v.__tupla) {
      const d = v.__tupla.map((x) => pyrepr(x, profundidad + 1));
      return "(" + d.join(", ") + (d.length === 1 ? ",)" : ")");
    }
    if (v.__tipo === "Estudiante") {
      return `Estudiante(nombre=${pyrepr(v.nombre)}, correo=${pyrepr(v.correo)}, telefono=${pyrepr(v.telefono)}, ` +
             `edad=${pyrepr(v.edad)}, carrera=${pyrepr(v.carrera)}, id=${pyrepr(v.id)}, creado_en=${pyrepr(v.creado_en)})`;
    }
    if (v.__tipo) return `<${v.__tipo} object>`;
    return "{" + Object.entries(v).map(([k, x]) => `${pyrepr(k)}: ${pyrepr(x, profundidad + 1)}`).join(", ") + "}";
  }
  const recortar = (t, n = 70) => (t.length > n ? t.slice(0, n - 3) + "..." : t);

  // ───────────────────────── Grabación ──────────────────────────────────────────
  let pasos = [], marcos = [];
  const tope = () => marcos[marcos.length - 1];
  const nombreCorto = (ruta) => ruta.split("/").pop().replace(".py", "");

  function entrar(ruta, fn, vars = {}) {
    const def = lineaDef(ruta, fn);
    marcos.push({ ruta, fn, cursor: def, vars: { ...vars }, etiqueta: `${nombreCorto(ruta)}.${fn}` });
  }
  function salir() { marcos.pop(); }
  function v(nombre, valor) { tope().vars[nombre] = valor; }

  function foto(vars) {
    const r = {};
    for (const [k, x] of Object.entries(vars)) r[k] = recortar(pyrepr(x));
    return r;
  }

  /** «Python está a punto de ejecutar esta línea». */
  function P(texto, opciones = {}) {
    const m = tope();
    const n = buscarLinea(m.ruta, m.cursor, texto);
    if (!n) { faltantes.push(`${m.ruta}: ${texto}`); console.warn("Motor: no encontré la línea", m.ruta, texto); return; }
    m.cursor = n;
    pasos.push({ archivo: m.ruta, linea: n, funcion: m.fn, pila: marcos.map((x) => x.etiqueta),
                 variables: foto(m.vars), nota: opciones.nota || "", error: false });
  }
  /** Un error (excepción) pasa por la línea actual de la función de arriba. */
  function E(nota) {
    const m = tope();
    pasos.push({ archivo: m.ruta, linea: m.cursor, funcion: m.fn, pila: marcos.map((x) => x.etiqueta),
                 variables: foto(m.vars), nota, error: true });
  }
  /** Una función que se ejecuta completa pero se muestra como un solo paso. */
  function resumir(ruta, fn, nota) {
    entrar(ruta, fn);
    const m = tope();
    pasos.push({ archivo: ruta, linea: m.cursor, funcion: fn, pila: marcos.map((x) => x.etiqueta),
                 variables: {}, nota, error: false });
    salir();
  }

  function grabar(funcion) {
    pasos = []; marcos = [];
    const resultado = funcion();
    return { resultado, pasos };
  }

  // ───────────────────────── La «base de datos» (tabla en memoria) ──────────────
  const CARRERAS = ["Ingeniería en Sistemas", "Agronomía", "Administración de Empresas",
                    "Medicina", "Derecho", "Arquitectura", "Otra"];
  const BD = { filas: [], siguienteId: 1, motivo: null, registro: [] };

  function sembrar() {
    const ejemplos = [
      ["Luis Fernando Ajú", "luis.aju@ejemplo.com", "4777-1200", 30, "Ingeniería en Sistemas"],
      ["Sofía Castillo", "sofia.castillo@ejemplo.com", "5012-4455", 22, "Administración de Empresas"],
      ["Diego Hernández", "diego.hdz@ejemplo.com", "3098-7766", 27, "Agronomía"],
      ["María José Ruiz", "mariajose.ruiz@ejemplo.com", "", 19, "Medicina"],
      ["Carlos Méndez", "carlos.mendez@ejemplo.com", "4410-2299", 24, "Agronomía"],
      ["Ana Lucía Pérez", "ana.perez@ejemplo.com", "5521-3344", 21, "Ingeniería en Sistemas"],
    ];
    BD.filas = ejemplos.map(([nombre, correo, telefono, edad, carrera], i) =>
      ({ id: i + 1, nombre, correo, telefono, edad, carrera, creado_en: "2026-10-19 09:00:00" }));
    BD.siguienteId = ejemplos.length + 1;
  }
  sembrar();

  function ahora() {
    const d = new Date(), p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  }
  const ms = () => +(0.05 + Math.random() * 0.4).toFixed(2);
  function anotarSQL(sql, parametros, filas, error = null) {
    BD.registro.push({ sql, parametros, filas, ms: ms(), error, motivo: BD.motivo, hora: new Date() });
  }
  const tupla = (arr) => ({ __tupla: arr });
  const comoEstudiante = (f) => ({ __tipo: "Estudiante", ...f });
  const RUTAS = { ventana: "interfaz/ventana_principal.py", val: "validaciones.py",
                  repo: "repositorio.py", bd: "base_datos.py", modelo: "modelo.py" };

  // ───────────────────────── base_datos.py ──────────────────────────────────────
  function bd_ms_desde() {
    entrar(RUTAS.bd, "_ms_desde"); P("return (time.perf_counter() - inicio) * 1000"); salir();
  }
  function bd_avisar() {
    entrar(RUTAS.bd, "_avisar");
    P('detalle["motivo"] = self._motivo');
    P("for funcion in self._oyentes:");
    P("funcion(detalle)", { nota: "→ la Consola SQL recibe el aviso y lo muestra" });
    salir();
  }
  /** sql, parametros y una función `efecto` que cambia la tabla (o lanza error). */
  function bd_ejecutar(sql, parametros, efecto) {
    entrar(RUTAS.bd, "ejecutar", { sql, parametros: tupla(parametros) });
    P("inicio = time.perf_counter()"); v("inicio", 13851.6366);
    P("try:");
    P("with self.conexion:");
    P("cursor = self.conexion.execute(sql, parametros)");
    let cursor;
    try {
      cursor = efecto();
    } catch (falla) {
      E(`⚠ sqlite3.IntegrityError: ${falla.message}`);
      P("except sqlite3.Error as error:", { nota: "with deshizo todo (ROLLBACK): la tabla quedó intacta" });
      v("error", { __tipo: "sqlite3.IntegrityError" });
      P("self._avisar(sql=sql, parametros=parametros, filas=0,"); bd_ms_desde(); bd_avisar();
      anotarSQL(sql, parametros, 0, falla.message);
      P("raise", { nota: "el error se lanza hacia arriba, a quien llamó" });
      salir();
      throw falla;
    }
    v("cursor", { __tipo: "sqlite3.Cursor" });
    P("self._avisar(sql=sql, parametros=parametros, filas=cursor.rowcount,"); bd_ms_desde(); bd_avisar();
    anotarSQL(sql, parametros, cursor.rowcount);
    P("return cursor", { nota: cursor.lastrowid ? `COMMIT ✓ · SQLite asignó el id ${cursor.lastrowid}` : "COMMIT ✓ cambios guardados en taller.db" });
    salir();
    return cursor;
  }
  function bd_consultar(sql, parametros, consulta) {
    entrar(RUTAS.bd, "consultar", { sql, parametros: tupla(parametros) });
    P("inicio = time.perf_counter()"); v("inicio", 13851.9021);
    P("filas = self.conexion.execute(sql, parametros).fetchall()");
    const filas = consulta();
    v("filas", filas.map((f) => ({ ...f })));
    P("self._avisar(sql=sql, parametros=parametros, filas=len(filas),"); bd_ms_desde(); bd_avisar();
    anotarSQL(sql, parametros, filas.length);
    P("return filas");
    salir();
    return filas;
  }
  /** Lo que la app ejecuta para repintar (refrescar): se anota en la consola como «refresco». */
  function refrescoSilencioso(busqueda = "") {
    const antes = BD.motivo;
    BD.motivo = busqueda ? null : "refresco";
    anotarSQL("SELECT carrera, COUNT(*) AS total FROM estudiantes GROUP BY carrera ORDER BY total DESC", [], porCarrera().length);
    anotarSQL("SELECT * FROM estudiantes ORDER BY id DESC", [], BD.filas.length);
    BD.motivo = antes;
  }

  // ───────────────────────── modelo.py ──────────────────────────────────────────
  function modelo_desde_fila(fila) {
    entrar(RUTAS.modelo, "desde_fila", { fila: { ...fila } });
    P("return cls(", { nota: "la fila de SQLite se convierte en un objeto Estudiante" });
    salir();
    return comoEstudiante(fila);
  }

  // ───────────────────────── validaciones.py ────────────────────────────────────
  const PATRON_CORREO = /^[\p{L}\p{N}_.+-]+@[\p{L}\p{N}_-]+(\.[\p{L}\p{N}_-]+)+$/u;

  function validar_estudiante(datos) {
    entrar(RUTAS.val, "validar_estudiante", { datos });
    const errores = {};
    P("errores = {}"); v("errores", errores);
    P('nombre = datos.get("nombre", "").strip()'); const nombre = (datos.nombre || "").trim(); v("nombre", nombre);
    P('correo = datos.get("correo", "").strip().lower()'); const correo = (datos.correo || "").trim().toLowerCase(); v("correo", correo);
    P('telefono = datos.get("telefono", "")'); let telefono = (datos.telefono || "").trim().replace(/-/g, "").replace(/ /g, ""); v("telefono", telefono);
    P('edad_texto = datos.get("edad", "").strip()'); const edadTexto = (datos.edad || "").trim(); v("edad_texto", edadTexto);
    P('carrera = datos.get("carrera", "").strip()'); const carrera = (datos.carrera || "").trim(); v("carrera", carrera);

    P("if len(nombre) < 3:");
    if (nombre.length < 3) { P('errores["nombre"] = '); errores.nombre = "Escribe al menos 3 letras."; }
    P("if not PATRON_CORREO.match(correo):");
    if (!PATRON_CORREO.test(correo)) { P('errores["correo"] = '); errores.correo = "Ejemplo válido: ana@correo.com"; }
    P("if telefono and not (telefono.isdigit()");
    if (telefono && !(/^\d+$/.test(telefono) && telefono.length === 8)) { P('errores["telefono"] = '); errores.telefono = "Deben ser 8 dígitos, ej. 5555 1234."; }
    P("edad = 0"); let edad = 0;
    P("try:"); v("edad", 0);
    P("edad = int(edad_texto)");
    if (/^\s*[+-]?\d+\s*$/.test(edadTexto)) {
      edad = parseInt(edadTexto, 10); v("edad", edad);
      P("if not 10 <= edad <= 120:");
      if (!(edad >= 10 && edad <= 120)) { P('errores["edad"] = "La edad debe'); errores.edad = "La edad debe estar entre 10 y 120."; }
    } else {
      E(`⚠ ValueError: invalid literal for int(): ${pyrepr(edadTexto)}`);
      P("except ValueError:", { nota: "try/except atrapó el error: el programa NO se cae" });
      P('errores["edad"] = "Escribe la edad'); errores.edad = "Escribe la edad con números.";
    }
    P("if carrera not in CARRERAS:");
    if (!CARRERAS.includes(carrera)) { P('errores["carrera"] = '); errores.carrera = "Elige una carrera de la lista."; }
    v("errores", { ...errores });

    P("if errores:");
    if (Object.keys(errores).length) {
      P("return None, errores", { nota: `${Object.keys(errores).length} campo(s) con error → no se toca la base de datos` });
      salir();
      return [null, errores];
    }
    P("if telefono:");
    if (telefono) { P('telefono = f"{telefono[:4]}-{telefono[4:]}"'); telefono = `${telefono.slice(0, 4)}-${telefono.slice(4)}`; v("telefono", telefono); }
    P("return Estudiante(nombre=nombre", { nota: "todo bien → se arma el objeto Estudiante" });
    salir();
    return [comoEstudiante({ nombre, correo, telefono, edad, carrera, id: null, creado_en: null }), {}];
  }

  // ───────────────────────── repositorio.py ─────────────────────────────────────
  const unico = (correo, excepto) => {
    if (BD.filas.some((f) => f.correo === correo && f.id !== excepto)) {
      throw new Error("UNIQUE constraint failed: estudiantes.correo");
    }
  };

  function repo_crear(e) {
    entrar(RUTAS.repo, "crear", { estudiante: e });
    P("cursor = self.bd.ejecutar(");
    let cursor;
    try {
      cursor = bd_ejecutar("INSERT INTO estudiantes (nombre, correo, telefono, edad, carrera) VALUES (?, ?, ?, ?, ?)",
        [e.nombre, e.correo, e.telefono, e.edad, e.carrera], () => {
          unico(e.correo);
          const id = BD.siguienteId++;
          BD.filas.push({ id, nombre: e.nombre, correo: e.correo, telefono: e.telefono, edad: e.edad, carrera: e.carrera, creado_en: ahora() });
          return { rowcount: 1, lastrowid: id };
        });
    } catch (falla) { E(`⚠ IntegrityError sube por repositorio.crear()`); salir(); throw falla; }
    v("cursor", { __tipo: "sqlite3.Cursor" });
    P("return cursor.lastrowid", { nota: `devuelve el id nuevo: ${cursor.lastrowid}` });
    salir();
    return cursor.lastrowid;
  }

  function repo_obtener(id) {
    entrar(RUTAS.repo, "obtener", { id_estudiante: id });
    P('filas = self.bd.consultar("SELECT * FROM estudiantes WHERE id = ?"');
    const filas = bd_consultar("SELECT * FROM estudiantes WHERE id = ?", [id], () => BD.filas.filter((f) => f.id === id));
    v("filas", filas.map((f) => ({ ...f })));
    P("return Estudiante.desde_fila(filas[0]) if filas else None");
    const r = filas.length ? modelo_desde_fila(filas[0]) : null;
    salir();
    return r;
  }

  function repo_listar(busqueda) {
    entrar(RUTAS.repo, "listar", { busqueda });
    P("if busqueda:");
    let filas;
    if (busqueda) {
      const patron = `%${busqueda}%`;
      P('patron = f"%{busqueda}%"'); v("patron", patron);
      P("filas = self.bd.consultar(");
      const t = busqueda.toLowerCase();
      filas = bd_consultar("SELECT * FROM estudiantes WHERE nombre LIKE ? OR correo LIKE ? OR carrera LIKE ? ORDER BY id DESC",
        [patron, patron, patron], () => BD.filas.filter((f) =>
          [f.nombre, f.correo, f.carrera].some((x) => x.toLowerCase().includes(t))).slice().reverse());
    } else {
      P('filas = self.bd.consultar("SELECT * FROM estudiantes ORDER BY id DESC")');
      filas = bd_consultar("SELECT * FROM estudiantes ORDER BY id DESC", [], () => BD.filas.slice().reverse());
    }
    v("filas", filas.map((f) => ({ ...f })));
    P("return [Estudiante.desde_fila(fila) for fila in filas]",
      { nota: `«list comprehension»: ${filas.length} filas → ${filas.length} objetos Estudiante` });
    const lista = filas.map((f) => modelo_desde_fila(f));
    salir();
    return lista;
  }

  function repo_actualizar(e) {
    entrar(RUTAS.repo, "actualizar", { estudiante: e });
    P("cursor = self.bd.ejecutar(");
    let cursor;
    try {
      cursor = bd_ejecutar("UPDATE estudiantes SET nombre = ?, correo = ?, telefono = ?, edad = ?, carrera = ? WHERE id = ?",
        [e.nombre, e.correo, e.telefono, e.edad, e.carrera, e.id], () => {
          unico(e.correo, e.id);
          const f = BD.filas.find((x) => x.id === e.id);
          if (!f) return { rowcount: 0 };
          Object.assign(f, { nombre: e.nombre, correo: e.correo, telefono: e.telefono, edad: e.edad, carrera: e.carrera });
          return { rowcount: 1 };
        });
    } catch (falla) { E("⚠ IntegrityError sube por repositorio.actualizar()"); salir(); throw falla; }
    v("cursor", { __tipo: "sqlite3.Cursor" });
    P("return cursor.rowcount == 1");
    salir();
    return cursor.rowcount === 1;
  }

  function repo_eliminar(id) {
    entrar(RUTAS.repo, "eliminar", { id_estudiante: id });
    P("cursor = self.bd.ejecutar(");
    const cursor = bd_ejecutar("DELETE FROM estudiantes WHERE id = ?", [id], () => {
      const antes = BD.filas.length;
      BD.filas = BD.filas.filter((f) => f.id !== id);
      return { rowcount: antes - BD.filas.length };
    });
    v("cursor", { __tipo: "sqlite3.Cursor" });
    P("return cursor.rowcount == 1");
    salir();
    return cursor.rowcount === 1;
  }

  function porCarrera() {
    const cuenta = {};
    BD.filas.forEach((f) => { cuenta[f.carrera] = (cuenta[f.carrera] || 0) + 1; });
    return Object.entries(cuenta).sort((a, b) => b[1] - a[1]);
  }

  // ───────────────────────── interfaz/ventana_principal.py ──────────────────────
  // Las líneas de la ventana (toast, ruta, pizarra...) se recorren; lo que hacen en
  // pantalla lo ejecuta la página DESPUÉS, según el resultado que devolvemos.
  function v_celebrar(operacion, mensaje) {
    entrar(RUTAS.ventana, "_celebrar", { operacion, mensaje });
    P("self.encabezado.encender(operacion)");
    P('self.toast.mostrar(mensaje, OPERACIONES[operacion]["color"])');
    salir();
  }
  function v_avisar_error(titulo, explicacion) {
    entrar(RUTAS.ventana, "_avisar_error", { titulo, explicacion });
    P('self.toast.mostrar(f"⚠ {titulo}", COLORES["error"])');
    P("self.pizarra.explicar_error(titulo, explicacion)");
    salir();
  }
  function v_limpiar(explicar) {
    entrar(RUTAS.ventana, "limpiar", { explicar });
    P("self.id_seleccionado = None");
    P("self.tabla.quitar_seleccion()");
    P("self.formulario.vaciar()");
    P("if explicar:");
    salir();
  }
  function v_refrescar_resumido() {
    resumir(RUTAS.ventana, "refrescar", "↻ refrescar() vuelve a leer la tabla y el gráfico (se resume en un paso)");
    refrescoSilencioso();
  }

  function crear(datos, busquedaActiva) {
    entrar(RUTAS.ventana, "crear");
    P("estudiante, errores = validar_estudiante(self.formulario.leer())");
    const [estudiante, errores] = validar_estudiante(datos);
    v("estudiante", estudiante); v("errores", errores);
    P("if errores:");
    if (Object.keys(errores).length) {
      P("self.formulario.mostrar_errores(errores)");
      P('self.ruta.recorrer(COLORES["error"], hasta=1, fallo=True)');
      P('self._avisar_error("Revisa los campos en rojo",');
      v_avisar_error("Revisa los campos en rojo", "La validación detuvo el guardado...");
      P("return"); salir();
      return { tipo: "errores", errores };
    }
    P("try:");
    P("nuevo_id = self.repo.crear(estudiante)");
    let nuevoId;
    try {
      nuevoId = repo_crear(estudiante);
    } catch (falla) {
      E("⚠ IntegrityError llega a la ventana");
      P("except sqlite3.IntegrityError:", { nota: "la ventana atrapa el error y avisa con calma" });
      P('self.formulario.mostrar_errores({"correo": "Ese correo ya está registrado."})');
      P('self.ruta.recorrer(COLORES["error"], hasta=3, fallo=True)');
      P('self._avisar_error("SQLite dijo que no",');
      v_avisar_error("SQLite dijo que no", "La columna «correo» es UNIQUE...");
      P("return"); salir();
      return { tipo: "unico" };
    }
    v("nuevo_id", nuevoId);
    P('self._celebrar("INSERT"'); v_celebrar("INSERT", `✓ ${estudiante.nombre} creado (#${nuevoId})`);
    P('self.ruta.recorrer(COLORES["crear"])');
    P("if self.tabla.busqueda.get():");
    if (busquedaActiva) { P('self.tabla.busqueda.set("")'); } else { P("self.refrescar()"); }
    v_refrescar_resumido();
    P("self.tabla.destellar(nuevo_id");
    P("self.formulario.vaciar()");
    P("self.pizarra.explicar_crear(estudiante, nuevo_id)");
    salir();
    estudiante.id = nuevoId;
    return { tipo: "ok", estudiante, id: nuevoId };
  }

  function seleccionar(id) {
    entrar(RUTAS.ventana, "seleccionar", { id_estudiante: id });
    P("estudiante = self.repo.obtener(id_estudiante)");
    const e = repo_obtener(id);
    v("estudiante", e);
    P("if estudiante is None:");
    if (!e) { P("return"); salir(); return { tipo: "nada" }; }
    P("self.id_seleccionado = id_estudiante");
    P("self.formulario.cargar(estudiante)");
    P('self.encabezado.encender("SELECT")');
    P('self.ruta.recorrer(COLORES["leer"], saltar={1})');
    P("self.pizarra.explicar_leer(estudiante)");
    salir();
    return { tipo: "ok", estudiante: e };
  }

  function buscar(texto) {
    entrar(RUTAS.ventana, "buscar", { texto });
    P("total = self.refrescar(texto, con_grafico=False)");
    // Aquí sí mostramos refrescar por dentro: el SELECT con LIKE es la acción principal.
    entrar(RUTAS.ventana, "refrescar", { busqueda: texto, con_grafico: false });
    P("with self.bd.motivo(");
    P("if con_grafico:");
    P("estudiantes = self.repo.listar(busqueda)");
    const antes = BD.motivo; BD.motivo = texto ? null : "refresco";
    const estudiantes = repo_listar(texto);
    BD.motivo = antes;
    v("estudiantes", estudiantes);
    P("self.tabla.mostrar(estudiantes)", { nota: "la tabla de la ventana se vuelve a pintar" });
    P("total = len(estudiantes)"); v("total", estudiantes.length);
    P("plantilla = ");
    P("contar_hasta(self.contador");
    P("self._total_mostrado = total");
    P("return total");
    salir();
    v("total", estudiantes.length);
    P("if texto:");
    if (texto) {
      P('self.encabezado.encender("SELECT")');
      P('self.ruta.recorrer(COLORES["leer"], saltar={1})');
      P("self.pizarra.explicar_busqueda(texto, total)");
    }
    salir();
    return { tipo: "ok", estudiantes, total: estudiantes.length };
  }

  function actualizar(id, datos) {
    entrar(RUTAS.ventana, "actualizar");
    P("if not self.id_seleccionado:");
    P("estudiante, errores = validar_estudiante(self.formulario.leer())");
    const [estudiante, errores] = validar_estudiante(datos);
    v("estudiante", estudiante); v("errores", errores);
    P("if errores:");
    if (Object.keys(errores).length) {
      P("self.formulario.mostrar_errores(errores)");
      P('self.ruta.recorrer(COLORES["error"], hasta=1, fallo=True)');
      P('self._avisar_error("Revisa los campos en rojo", "No se envió ningún UPDATE.")');
      v_avisar_error("Revisa los campos en rojo", "No se envió ningún UPDATE.");
      P("return"); salir();
      return { tipo: "errores", errores };
    }
    P("anterior = self.repo.obtener(self.id_seleccionado)");
    const anterior = repo_obtener(id);
    v("anterior", anterior);
    P("estudiante.id = self.id_seleccionado"); estudiante.id = id; v("estudiante", estudiante);
    P("try:");
    P("self.repo.actualizar(estudiante)");
    try {
      repo_actualizar(estudiante);
    } catch (falla) {
      E("⚠ IntegrityError llega a la ventana");
      P("except sqlite3.IntegrityError:");
      P('self.formulario.mostrar_errores({"correo": "Ese correo ya lo usa otro estudiante."})');
      P('self.ruta.recorrer(COLORES["error"], hasta=3, fallo=True)');
      P('self._avisar_error("SQLite dijo que no", "El correo debe ser único (UNIQUE).")');
      v_avisar_error("SQLite dijo que no", "El correo debe ser único (UNIQUE).");
      P("return"); salir();
      return { tipo: "unico" };
    }
    const cambios = ["nombre", "correo", "telefono", "edad", "carrera"].filter((c) => anterior[c] !== estudiante[c]);
    P("cambios = [campo for campo in"); v("cambios", cambios);
    P('self._celebrar("UPDATE"'); v_celebrar("UPDATE", `✎ ${estudiante.nombre} actualizado`);
    P('self.ruta.recorrer(COLORES["actualizar"])');
    P("self.refrescar(self.tabla.busqueda.get().strip())"); v_refrescar_resumido();
    P("self.tabla.destellar(estudiante.id");
    P("self.pizarra.explicar_actualizar(estudiante, cambios)");
    P("self.limpiar(explicar=False)"); v_limpiar(false);
    salir();
    return { tipo: "ok", estudiante, cambios };
  }

  function eliminar(id) {
    entrar(RUTAS.ventana, "eliminar");
    P("if not self.id_seleccionado:");
    P("estudiante = self.repo.obtener(self.id_seleccionado)");
    const e = repo_obtener(id);
    v("estudiante", e);
    P("if estudiante is None:");
    if (!e) { P("return"); salir(); return { tipo: "nada" }; }
    P("if not messagebox.askyesno(", { nota: "se pidió confirmación y el usuario dijo «Sí»" });
    P("self.repo.eliminar(estudiante.id)"); repo_eliminar(e.id);
    P('self._celebrar("DELETE"'); v_celebrar("DELETE", `✕ ${e.nombre} eliminado`);
    P('self.ruta.recorrer(COLORES["eliminar"], saltar={1})');
    P("self.limpiar(explicar=False)"); v_limpiar(false);
    P("self.refrescar(self.tabla.busqueda.get().strip())"); v_refrescar_resumido();
    P("self.pizarra.explicar_eliminar(estudiante.nombre, estudiante.id)");
    salir();
    return { tipo: "ok", estudiante: e };
  }

  // ───────────────────────── API pública ────────────────────────────────────────
  return {
    cargarFuentes, grabar, faltantes, BD, CARRERAS, porCarrera, refrescoSilencioso,
    filasVisibles: (texto) => {
      const t = (texto || "").toLowerCase();
      return BD.filas.filter((f) => !t || [f.nombre, f.correo, f.carrera].some((x) => x.toLowerCase().includes(t))).slice().reverse();
    },
    obtenerFila: (id) => BD.filas.find((f) => f.id === id),
    operaciones: { crear, seleccionar, buscar, actualizar, eliminar },
    reiniciar: () => { sembrar(); BD.registro = []; },
  };
})();
if (typeof module !== "undefined") module.exports = Motor;
