# Instalación para alumnos

Hazlo **antes del día del taller**. Toma unos 15 minutos y evita que perdamos tiempo de clase.

## 1. Instalar Python 3.12

1. Entra a <https://www.python.org/downloads/> y descarga **Python 3.12** (o más nuevo).
2. **Windows:** en la primera pantalla del instalador marca la casilla **«Add python.exe to PATH»** y luego pulsa **Install Now**.
3. **macOS:** abre el `.pkg` descargado y sigue los pasos.
4. **Linux (Ubuntu/Debian):** Python ya viene instalado. Solo agrega tkinter:

   ```bash
   sudo apt install python3-tk
   ```

Para comprobarlo, abre una terminal (en Windows: «Símbolo del sistema») y escribe:

```bash
python --version
```

Debe responder algo como `Python 3.12.x`. En macOS y Linux usa `python3 --version`.

## 2. Instalar PyCharm

1. Entra a <https://www.jetbrains.com/pycharm/download/>.
2. Descarga **PyCharm**. La versión gratuita alcanza para todo el taller.
3. Instálalo con las opciones por defecto. En Windows conviene marcar **«Add "Open Folder as Project"»**.

## 3. Abrir el proyecto del taller

1. Descarga el proyecto de <https://github.com/JoseMan200124/taller-python-pycharm>: botón verde **Code → Download ZIP** y descomprímelo. Si usas Git: `git clone https://github.com/JoseMan200124/taller-python-pycharm.git`.
   (También sirve la carpeta comprimida que te envíe el instructor.)
2. En PyCharm: **File → Open…** y elige la carpeta del taller.
3. Si PyCharm pregunta por el intérprete («No Python interpreter configured»):
   **Configure Python Interpreter → Add Interpreter → Add Local Interpreter → Virtualenv** y acepta.
   No hace falta instalar paquetes: el taller usa solo lo que trae Python.

## 4. Verificar que todo funcione

En el panel izquierdo de PyCharm, haz clic derecho sobre **`verificar_entorno.py` → Run 'verificar_entorno'**.

Debes ver tres marcas verdes y una ventanita azul que dice **«Tu computadora está lista»**.

| Si ves esto | Haz esto |
|---|---|
| `✘ Python … 3.8` | Instala Python 3.12 y en PyCharm elige ese intérprete (Settings → Project → Python Interpreter). |
| `✘ tkinter no encontrado` | Linux: `sudo apt install python3-tk`. Windows/macOS: reinstala Python desde python.org (no desde la Microsoft Store). |
| No aparece la ventanita | Revisa si quedó detrás de PyCharm (Alt+Tab). |

## Atajos de PyCharm que usaremos

| Acción | Windows / Linux | macOS |
|---|---|---|
| Ejecutar el archivo actual | `Ctrl + Shift + F10` | `Ctrl + Shift + R` |
| Volver a ejecutar | `Shift + F10` | `Ctrl + R` |
| Depurar (Debug) | `Shift + F9` | `Ctrl + D` |
| Avanzar una línea en Debug | `F8` | `F8` |
| Comentar / descomentar línea | `Ctrl + /` | `Cmd + /` |
| Formatear el código | `Ctrl + Alt + L` | `Cmd + Opt + L` |
| Ir a la definición de una función | `Ctrl + clic` | `Cmd + clic` |
| Buscar en todo el proyecto | `Shift Shift` | `Shift Shift` |
| Renombrar una variable en todos lados | `Shift + F6` | `Shift + F6` |
