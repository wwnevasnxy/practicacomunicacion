#!/usr/bin/env python3
"""
resumen_ventas.py
Procesa un archivo JSON con registros de ventas, valida los datos,
calcula métricas de resumen con precisión monetaria (usando Decimal)
y genera un reporte en formato JSON.
"""

import argparse
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP


class ValidationError(Exception):
    """Excepción para errores de validación de datos de ventas."""
    pass


def validar_registro(registro, indice=0):
    """
    Valida un registro individual de ventas.
    Verifica presencia de campos, tipos numéricos y valores no negativos.
    """
    if not isinstance(registro, dict):
        raise ValidationError(f"Registro en posición {indice} debe ser un objeto JSON (dict).")

    campos_requeridos = ("producto", "cantidad", "precio")
    for campo in campos_requeridos:
        if campo not in registro:
            raise ValidationError(
                f"Registro {indice}: falta el campo obligatorio '{campo}'."
            )

    producto = registro["producto"]
    if not isinstance(producto, str) or not producto.strip():
        raise ValidationError(
            f"Registro {indice}: 'producto' debe ser una cadena de texto no vacía."
        )

    cantidad = registro["cantidad"]
    # En Python, bool es subclase de int, se debe verificar explícitamente
    if isinstance(cantidad, bool) or not isinstance(cantidad, (int, float, Decimal)):
        raise ValidationError(
            f"Registro {indice}: 'cantidad' debe ser un valor numérico (obtenido: {type(cantidad).__name__})."
        )
    if cantidad < 0:
        raise ValidationError(
            f"Registro {indice}: 'cantidad' no puede ser negativa ({cantidad})."
        )

    precio = registro["precio"]
    if isinstance(precio, bool) or not isinstance(precio, (int, float, Decimal)):
        raise ValidationError(
            f"Registro {indice}: 'precio' debe ser un valor numérico (obtenido: {type(precio).__name__})."
        )
    if precio < 0:
        raise ValidationError(
            f"Registro {indice}: 'precio' no puede ser negativo ({precio})."
        )


def procesar_ventas(datos):
    """
    Valida los datos de ventas y calcula:
    - total de productos distintos
    - total de unidades
    - importe total (con precisión monetaria usando Decimal)
    - producto con mayor importe vendido
    """
    if not isinstance(datos, list):
        raise ValidationError("Los datos de ventas deben ser una lista de registros.")

    for idx, reg in enumerate(datos):
        validar_registro(reg, idx)

    if not datos:
        return {
            "productos_distintos": 0,
            "unidades_totales": 0,
            "importe_total": 0.0,
            "producto_mayor_importe": None,
        }

    ventas_por_producto = {}
    unidades_totales = Decimal("0")

    for reg in datos:
        producto = reg["producto"].strip()
        cant = Decimal(str(reg["cantidad"]))
        precio = Decimal(str(reg["precio"]))
        subtotal = cant * precio

        ventas_por_producto[producto] = ventas_por_producto.get(producto, Decimal("0.00")) + subtotal
        unidades_totales += cant

    productos_distintos = len(ventas_por_producto)
    importe_total_dec = sum(ventas_por_producto.values(), Decimal("0.00")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    importe_total = float(importe_total_dec)

    producto_mayor_importe = max(ventas_por_producto.items(), key=lambda item: item[1])[0]

    unidades_final = int(unidades_totales) if unidades_totales == unidades_totales.to_integral() else float(unidades_totales)

    return {
        "productos_distintos": productos_distintos,
        "unidades_totales": unidades_final,
        "importe_total": importe_total,
        "producto_mayor_importe": producto_mayor_importe,
    }


def serializar_reporte(reporte):
    """
    Serializa el reporte a JSON garantizando formato con 2 decimales en importe_total.
    """
    json_str = json.dumps(reporte, indent=2, ensure_ascii=False)
    # Formatear el número de importe_total a dos decimales exactos en el JSON
    json_str = re.sub(
        r'("importe_total":\s*)(\d+(\.\d+)?)',
        lambda m: f"{m.group(1)}{Decimal(m.group(2)):.2f}",
        json_str,
    )
    return json_str


def generar_reporte(ruta_input, ruta_output):
    """
    Lee el archivo de entrada, procesa las ventas y escribe el reporte en el archivo de salida.
    """
    try:
        with open(ruta_input, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        raise ValidationError(f"No se encontró el archivo de entrada: '{ruta_input}'")
    except json.JSONDecodeError as e:
        raise ValidationError(f"El archivo '{ruta_input}' no contiene un JSON válido: {e}")
    except OSError as e:
        raise ValidationError(f"Error al leer el archivo '{ruta_input}': {e}")

    reporte = procesar_ventas(datos)
    json_contenido = serializar_reporte(reporte)

    try:
        with open(ruta_output, "w", encoding="utf-8") as f:
            f.write(json_contenido + "\n")
    except OSError as e:
        raise ValidationError(f"Error al escribir en el archivo de salida '{ruta_output}': {e}")

    return reporte


def main():
    parser = argparse.ArgumentParser(
        description="Procesa datos de ventas y genera reporte en JSON."
    )
    parser.add_argument(
        "--input", required=True, help="Ruta al archivo JSON de ventas de entrada"
    )
    parser.add_argument(
        "--output", required=True, help="Ruta al archivo JSON de reporte de salida"
    )

    args = parser.parse_args()

    try:
        generar_reporte(args.input, args.output)
    except ValidationError as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(1)
    except Exception as err:
        sys.stderr.write(f"Error inesperado: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
