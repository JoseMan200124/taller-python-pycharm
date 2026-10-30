"""
test_crud.py — Pruebas automáticas del CRUD (sin abrir ventanas).
==================================================================

En PyCharm: clic derecho sobre la carpeta `tests` → Run 'Python tests in tests'.
Verás una barra verde si todo funciona. 🟢

Cada prueba usa una base de datos en memoria (":memory:"), así que
nunca toca el archivo real taller.db.
"""

import sqlite3
import sys
import unittest
from pathlib import Path

# Para poder importar los módulos de app_crud desde esta carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app_crud"))

from base_datos import BaseDatos  # noqa: E402
from modelo import Estudiante  # noqa: E402
from repositorio import RepositorioEstudiantes  # noqa: E402
from validaciones import validar_estudiante  # noqa: E402
from interfaz.rastreador import Rastreador  # noqa: E402


def estudiante_de_prueba(**cambios) -> Estudiante:
    datos = dict(nombre="Ana Pérez", correo="ana@correo.com", telefono="5555-1234",
                 edad=21, carrera="Agronomía")
    datos.update(cambios)
    return Estudiante(**datos)


class PruebasCRUD(unittest.TestCase):
    def setUp(self):
        """Se ejecuta ANTES de cada prueba: BD nueva y vacía."""
        self.bd = BaseDatos(":memory:")
        self.repo = RepositorioEstudiantes(self.bd)

    def tearDown(self):
        self.bd.cerrar()

    def test_crear_y_leer(self):
        nuevo_id = self.repo.crear(estudiante_de_prueba())
        guardado = self.repo.obtener(nuevo_id)
        self.assertEqual(guardado.nombre, "Ana Pérez")
        self.assertIsNotNone(guardado.creado_en)  # lo puso SQLite (DEFAULT)

    def test_correo_repetido_falla(self):
        self.repo.crear(estudiante_de_prueba())
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.crear(estudiante_de_prueba(nombre="Otra Ana"))

    def test_actualizar(self):
        nuevo_id = self.repo.crear(estudiante_de_prueba())
        cambiado = estudiante_de_prueba(id=nuevo_id, edad=22)
        self.assertTrue(self.repo.actualizar(cambiado))
        self.assertEqual(self.repo.obtener(nuevo_id).edad, 22)

    def test_eliminar(self):
        nuevo_id = self.repo.crear(estudiante_de_prueba())
        self.assertTrue(self.repo.eliminar(nuevo_id))
        self.assertIsNone(self.repo.obtener(nuevo_id))
        self.assertFalse(self.repo.eliminar(nuevo_id))  # ya no existe

    def test_buscar_con_like(self):
        self.repo.crear(estudiante_de_prueba())
        self.repo.crear(estudiante_de_prueba(nombre="Carlos", correo="c@correo.com", carrera="Medicina"))
        self.assertEqual(len(self.repo.listar("medi")), 1)
        self.assertEqual(len(self.repo.listar()), 2)

    def test_inyeccion_sql_no_funciona(self):
        """El clásico ' OR '1'='1 se busca como texto literal y no encuentra nada."""
        self.repo.crear(estudiante_de_prueba())
        self.assertEqual(self.repo.listar("' OR '1'='1"), [])

    def test_oyente_recibe_cada_sql(self):
        registro = []
        self.bd.agregar_oyente(registro.append)
        self.repo.crear(estudiante_de_prueba())
        self.assertTrue(registro[-1]["sql"].startswith("INSERT"))
        self.assertEqual(registro[-1]["filas"], 1)


class PruebasValidacion(unittest.TestCase):
    def test_datos_correctos(self):
        estudiante, errores = validar_estudiante({
            "nombre": "  Ana  ", "correo": "ANA@Correo.com", "telefono": "55551234",
            "edad": "21", "carrera": "Agronomía"})
        self.assertEqual(errores, {})
        self.assertEqual(estudiante.nombre, "Ana")
        self.assertEqual(estudiante.correo, "ana@correo.com")
        self.assertEqual(estudiante.telefono, "5555-1234")

    def test_datos_incorrectos(self):
        _, errores = validar_estudiante({
            "nombre": "A", "correo": "sin-arroba", "telefono": "123",
            "edad": "veinte", "carrera": ""})
        self.assertEqual(set(errores), {"nombre", "correo", "telefono", "edad", "carrera"})


class PruebasRastreador(unittest.TestCase):
    """El espía de sys.settrace debe anotar las líneas reales del CRUD."""

    def test_graba_lineas_de_repositorio_y_base_datos(self):
        if sys.gettrace() is not None:
            self.skipTest("Con el depurador o coverage activo no se puede grabar.")
        bd = BaseDatos(":memory:")
        repo = RepositorioEstudiantes(bd)
        nuevo_id, pasos = Rastreador().grabar(lambda: repo.crear(estudiante_de_prueba()))
        bd.cerrar()

        self.assertEqual(nuevo_id, 1)
        archivos = {paso.archivo for paso in pasos}
        self.assertIn("repositorio.py", archivos)
        self.assertIn("base_datos.py", archivos)
        # La pila debe mostrar que base_datos.ejecutar fue llamado por repositorio.crear.
        pila = next(p.pila for p in pasos if p.funcion == "ejecutar")
        self.assertEqual(pila[:2], ["repositorio.crear", "base_datos.ejecutar"])


if __name__ == "__main__":
    unittest.main()
