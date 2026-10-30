# Cómo contribuir

¡Gracias por querer mejorar el taller! Este proyecto es material didáctico, así que la claridad pesa tanto como el código.

## Principios

- **Solo biblioteca estándar.** Nada de paquetes externos: cualquier estudiante debe poder abrir el proyecto y ejecutarlo sin instalar nada.
- **Python 3.10 o más nuevo.**
- **Código que se lee en voz alta.** Nombres en español, comentarios que explican el *porqué* y docstrings al inicio de cada archivo, como en el resto del proyecto.
- **Un concepto nuevo por lección.** Si una lección necesita dos ideas nuevas, probablemente son dos lecciones.

## Flujo de trabajo

1. Haz un *fork* y crea una rama descriptiva (`reto-exportar-csv`, `corrige-validacion-edad`).
2. Haz tus cambios y corre las pruebas:

   ```bash
   python -m unittest discover -s tests -v
   ```

3. Si tocaste algo en `app_crud/`, regenera el simulador web y revisa que siga funcionando en el navegador:

   ```bash
   python presentacion/construir.py
   ```

   Abre `presentacion/index.html`, pulsa cada botón y confirma que `Motor.faltantes` esté vacío en la consola del navegador. Si una línea cambió de texto, actualiza la llamada `P('…')` correspondiente en `presentacion/motor.js`.

4. Abre un *pull request* que explique qué cambia y qué aprende el estudiante con ese cambio.

## Ideas bienvenidas

- Nuevos retos en `retos/RETOS.md`, con su pista.
- Mejores explicaciones en la pizarra o en los comentarios.
- Correcciones de accesibilidad en el simulador web.
- Reportes de errores al dictar el taller: abre un *issue* con el sistema operativo, la versión de Python y los pasos para reproducirlo.
