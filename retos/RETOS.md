# Retos del taller

Elige tu nivel. Trabaja en pareja: uno escribe, el otro revisa. Las pistas están escondidas: ábrelas solo si te atoras.

---

## Nivel 1 · Calentamiento

### 1.1 Una carrera nueva
Agrega «Ingeniería Agroindustrial» a la lista de carreras de la app final.

<details><summary>Pista</summary>

Todo lo configurable está en `app_crud/configuracion.py`. Busca la lista `CARRERAS`.
</details>

### 1.2 Cambia los colores
Haz que el color de «Crear» sea morado (`#7B3FE4`). ¿Dónde más cambia, además del botón?

<details><summary>Pista</summary>

Diccionario `COLORES` en `configuracion.py`. Observa el semáforo, la ruta del dato y la consola: todos leen el mismo color.
</details>

### 1.3 Más rápido o más lento
Haz que la pizarra escriba el doble de lento.

<details><summary>Pista</summary>

`VELOCIDAD_ESCRITURA` en `configuracion.py`.
</details>

---

## Nivel 2 · Ya le agarraste la onda

### 2.1 Validar el nombre
Que el nombre no acepte números («Ana2» debe dar error).

<details><summary>Pista</summary>

En `validaciones.py`: `any(letra.isdigit() for letra in nombre)` es `True` si hay algún dígito.
</details>

### 2.2 Contar por edad
Agrega al repositorio una función `promedio_edad()` que devuelva el promedio de edades usando SQL y muéstralo en la barra de abajo.

<details><summary>Pista</summary>

```python
def promedio_edad(self) -> float:
    fila = self.bd.consultar("SELECT AVG(edad) AS promedio FROM estudiantes")[0]
    return fila["promedio"] or 0
```
</details>

### 2.3 Buscar también por teléfono
Haz que el buscador encuentre estudiantes por su número de teléfono.

<details><summary>Pista</summary>

En `repositorio.py`, método `listar()`: agrega `OR telefono LIKE ?` y un `patron` más en la tupla. Cuenta los `?` y los valores: deben ser iguales.
</details>

---

## Nivel 3 · Reto de verdad

### 3.1 Un campo nuevo de punta a punta: «Carné»
Agrega el campo **carné** (texto, único) a la app final. Tienes que tocar **todas las capas**:

1. `base_datos.py` → la columna en `CREATE TABLE` (borra `taller.db` para que se cree de nuevo).
2. `modelo.py` → el atributo en `Estudiante`.
3. `repositorio.py` → el `INSERT` y el `UPDATE`.
4. `validaciones.py` → que no venga vacío.
5. `interfaz/formulario.py` → el campo en la lista `CAMPOS`.
6. `interfaz/tabla.py` → la columna en `COLUMNAS`.

Este reto demuestra por qué el código está separado en capas: cada archivo cambia un poquito y nada se rompe.

### 3.2 Exportar a CSV
Agrega un botón «Exportar» que guarde todos los estudiantes en `estudiantes.csv` (se abre en Excel).

<details><summary>Pista</summary>

```python
import csv
from tkinter import filedialog

ruta = filedialog.asksaveasfilename(defaultextension=".csv")
with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["id", "nombre", "correo", "telefono", "edad", "carrera"])
    for e in repo.listar():
        escritor.writerow(e.como_tupla_tabla())
```
</details>

### 3.3 Ordenar al hacer clic en el encabezado
En la tabla, al hacer clic en «Nombre» o «Edad» se ordena por esa columna.

<details><summary>Pista</summary>

`self.arbol.heading(clave, text=titulo, command=lambda c=clave: ordenar(c))`. Para ordenar, puedes usar `ORDER BY` en SQL, pero ¡cuidado! El nombre de una columna **no** se puede pasar con `?`. Usa una lista blanca: `if columna in ("nombre", "edad"): ...`
</details>
