"""
datos_ejemplo.py — Para que la tabla no arranque vacía.
========================================================

Solo se insertan si la tabla está vacía. Así la primera vez que se abre
la aplicación ya hay algo que leer, editar y borrar.
Para empezar de cero: borra el archivo taller.db y vuelve a ejecutar.
"""

from repositorio import RepositorioEstudiantes
from modelo import Estudiante

EJEMPLOS = [
    Estudiante("Ana Lucía Pérez", "ana.perez@ejemplo.com", "5521-3344", 21, "Ingeniería en Sistemas"),
    Estudiante("Carlos Méndez", "carlos.mendez@ejemplo.com", "4410-2299", 24, "Agronomía"),
    Estudiante("María José Ruiz", "mariajose.ruiz@ejemplo.com", "", 19, "Medicina"),
    Estudiante("Diego Hernández", "diego.hdz@ejemplo.com", "3098-7766", 27, "Agronomía"),
    Estudiante("Sofía Castillo", "sofia.castillo@ejemplo.com", "5012-4455", 22, "Administración de Empresas"),
    Estudiante("Luis Fernando Ajú", "luis.aju@ejemplo.com", "4777-1200", 30, "Ingeniería en Sistemas"),
]


def sembrar_si_vacia(repo: RepositorioEstudiantes) -> int:
    """Inserta los ejemplos si no hay registros. Devuelve cuántos insertó."""
    if repo.listar():
        return 0
    # reversed() para que, al ordenar por id DESC, Ana quede arriba.
    for estudiante in reversed(EJEMPLOS):
        repo.crear(estudiante)
    return len(EJEMPLOS)
