"""
test_lecciones.py — Los ejemplos de lecciones/ejemplos/ se pueden grabar paso a paso.

La sección «Las lecciones, paso a paso» de la página usa lo que graba
presentacion/grabar_lecciones.py. Si un ejemplo se rompe, esta prueba avisa.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "presentacion"))

import grabar_lecciones  # noqa: E402


class TestLecciones(unittest.TestCase):
    def test_cada_ejemplo_se_graba_completo(self):
        for leccion in grabar_lecciones.grabar_todas():
            with self.subTest(leccion["archivo"]):
                pasos = leccion["pasos"]
                self.assertGreater(len(pasos), 5)
                self.assertTrue(pasos[-1]["fin"])
                total = sum(len(texto) for _, texto in leccion["salida"])
                self.assertEqual(pasos[-1]["salida"], total)

    def test_ventana_y_tabla_quedan_grabadas(self):
        lecciones = {l["id"]: l for l in grabar_lecciones.grabar_todas()}
        final = lecciones["07"]["pasos"][-1]
        self.assertEqual([f[1] for f in final["tabla"]["filas"]], ["Ana", "Carlos"])
        lista = next(w for w in final["ventana"]["widgets"] if w["tipo"] == "Listbox")
        self.assertEqual(len(lista["filas"]), 2)


if __name__ == "__main__":
    unittest.main()
