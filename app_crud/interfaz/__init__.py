"""
Paquete `interfaz` — todo lo que se VE.
========================================

Cada archivo es una pieza de la ventana, como bloques de LEGO:

    ┌──────────────── encabezado.py (título + botón «Ver código» + semáforo C R U D) ──┐
    │ formulario.py         │  tabla.py (búsqueda + lista de estudiantes)              │
    │ (campos + botones)    │──────────────────────────────────────────────────────────│
    │                       │  ruta_dato.py (Ventana → Validar → ... → taller.db)      │
    │                       │──────────────────────────────────────────────────────────│
    │                       │  pizarra.py           │ consola_sql.py | grafico.py       │
    └───────────────────────┴───────────────────────┴───────────────────────────────────┘
                     ventana_principal.py  une todas las piezas

    Ventana aparte → visor_codigo.py: el código con la línea que se ejecuta brillando
                     (las líneas las graba rastreador.py con sys.settrace)
"""
