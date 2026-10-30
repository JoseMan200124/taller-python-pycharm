"""
main.py — ▶ Ejecuta ESTE archivo (clic derecho → Run 'main').
==============================================================

Aquí solo se «enchufan» las piezas y se arranca la ventana:

    BaseDatos  →  RepositorioEstudiantes  →  Aplicacion (ventana)

`if __name__ == "__main__":` significa «solo si este archivo es el que
se ejecutó directamente» (y no si alguien lo importó desde otro archivo).
"""

from base_datos import BaseDatos
from datos_ejemplo import sembrar_si_vacia
from repositorio import RepositorioEstudiantes
from interfaz.ventana_principal import Aplicacion


def main() -> None:
    bd = BaseDatos()                      # 1. abre (o crea) taller.db
    repo = RepositorioEstudiantes(bd)     # 2. prepara el CRUD
    sembrar_si_vacia(repo)                # 3. datos de ejemplo la primera vez
    app = Aplicacion(bd, repo)            # 4. construye la ventana
    app.mainloop()                        # 5. «ciclo de eventos»: espera clics hasta cerrar


if __name__ == "__main__":
    main()
