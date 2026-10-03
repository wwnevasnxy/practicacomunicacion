#!/usr/bin/env python3
"""
test_resumen_ventas.py
Pruebas unitarias para resumen_ventas.py usando unittest de la librería estándar.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

from resumen_ventas import (
    ValidationError,
    procesar_ventas,
    generar_reporte,
    validar_registro,
)


class TestResumenVentas(unittest.TestCase):
    def setUp(self):
        self.datos_validos = [
            {"producto": "Paracetamol", "cantidad": 3, "precio": 2.50},
            {"producto": "Ibuprofeno", "cantidad": 2, "precio": 4.20},
            {"producto": "Vitamina C", "cantidad": 5, "precio": 1.80},
        ]

    def test_caso_correcto(self):
        """Verifica que el procesamiento de datos válidos coincida con los resultados esperados."""
        res = procesar_ventas(self.datos_validos)
        self.assertEqual(res["productos_distintos"], 3)
        self.assertEqual(res["unidades_totales"], 10)
        self.assertEqual(res["importe_total"], 24.90)
        self.assertEqual(res["producto_mayor_importe"], "Vitamina C")

    def test_registro_campo_faltante_producto(self):
        """Verifica que un registro sin 'producto' lance ValidationError."""
        datos = [{"cantidad": 2, "precio": 5.0}]
        with self.assertRaises(ValidationError) as ctx:
            procesar_ventas(datos)
        self.assertIn("producto", str(ctx.exception))

    def test_registro_campo_faltante_cantidad(self):
        """Verifica que un registro sin 'cantidad' lance ValidationError."""
        datos = [{"producto": "Aspirina", "precio": 5.0}]
        with self.assertRaises(ValidationError) as ctx:
            procesar_ventas(datos)
        self.assertIn("cantidad", str(ctx.exception))

    def test_registro_campo_faltante_precio(self):
        """Verifica que un registro sin 'precio' lance ValidationError."""
        datos = [{"producto": "Aspirina", "cantidad": 2}]
        with self.assertRaises(ValidationError) as ctx:
            procesar_ventas(datos)
        self.assertIn("precio", str(ctx.exception))

    def test_cantidad_negativa(self):
        """Verifica que una cantidad negativa lance ValidationError."""
        datos = [{"producto": "Aspirina", "cantidad": -1, "precio": 3.50}]
        with self.assertRaises(ValidationError) as ctx:
            procesar_ventas(datos)
        self.assertIn("no puede ser negativa", str(ctx.exception))

    def test_precio_negativo(self):
        """Verifica que un precio negativo lance ValidationError."""
        datos = [{"producto": "Aspirina", "cantidad": 2, "precio": -2.50}]
        with self.assertRaises(ValidationError) as ctx:
            procesar_ventas(datos)
        self.assertIn("no puede ser negativo", str(ctx.exception))

    def test_tipos_no_numericos_o_invalidos(self):
        """Verifica que tipos no numéricos o booleanos sean rechazados."""
        # Cantidad texto
        with self.assertRaises(ValidationError):
            procesar_ventas([{"producto": "A", "cantidad": "tres", "precio": 2.0}])

        # Precio texto
        with self.assertRaises(ValidationError):
            procesar_ventas([{"producto": "A", "cantidad": 3, "precio": "dos"}])

        # Booleano en cantidad
        with self.assertRaises(ValidationError):
            procesar_ventas([{"producto": "A", "cantidad": True, "precio": 2.0}])

        # Producto vacío
        with self.assertRaises(ValidationError):
            procesar_ventas([{"producto": "  ", "cantidad": 1, "precio": 2.0}])

    def test_precision_monetaria(self):
        """Verifica la precisión monetaria sin errores de coma flotante."""
        # Casos clásicos donde floats fallan en sumas/multiplicaciones
        datos = [
            {"producto": "Item 1", "cantidad": 3, "precio": 19.99},  # 59.97
            {"producto": "Item 2", "cantidad": 7, "precio": 0.01},   # 0.07 -> total 60.04
        ]
        res = procesar_ventas(datos)
        self.assertEqual(res["importe_total"], 60.04)
        self.assertEqual(res["producto_mayor_importe"], "Item 1")

    def test_generar_reporte_archivo_y_cli(self):
        """Verifica la generación de archivos y la ejecución desde línea de comandos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "input.json")
            output_file = os.path.join(tmpdir, "output.json")

            with open(input_file, "w", encoding="utf-8") as f:
                json.dump(self.datos_validos, f)

            # Ejecución mediante CLI
            cmd = [
                sys.executable,
                "resumen_ventas.py",
                "--input",
                input_file,
                "--output",
                output_file,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(output_file))

            with open(output_file, "r", encoding="utf-8") as f:
                contenido = json.load(f)

            self.assertEqual(contenido["productos_distintos"], 3)
            self.assertEqual(contenido["unidades_totales"], 10)
            self.assertEqual(contenido["importe_total"], 24.90)
            self.assertEqual(contenido["producto_mayor_importe"], "Vitamina C")

    def test_cli_datos_invalidos_exit_code(self):
        """Verifica que la ejecución CLI falle con código != 0 y mensaje en stderr ante datos inválidos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_input = os.path.join(tmpdir, "bad.json")
            output_file = os.path.join(tmpdir, "output.json")

            with open(bad_input, "w", encoding="utf-8") as f:
                json.dump([{"producto": "Test", "cantidad": -5, "precio": 10.0}], f)

            cmd = [
                sys.executable,
                "resumen_ventas.py",
                "--input",
                bad_input,
                "--output",
                output_file,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error", result.stderr)
            self.assertIn("no puede ser negativa", result.stderr)


if __name__ == "__main__":
    unittest.main()
