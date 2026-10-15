#!/usr/bin/env python3
"""Punto 9 de las instrucciones del profesor:
'Deberá crear un archivo main (en la carpeta raíz de su github) que permita
ejecutar los procesos anteriores de forma automatizada, desde la descarga de
toda la información, su importación en la bd y habilitación del sitio web.'

Uso:
    python3 main.py               (Levanta Docker y ejecuta el pipeline completo)
    python3 main.py --sin-docker  (Ejecuta sobre base de datos Postgres existente)
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
TAREA2_MAIN = os.path.join(RAIZ, "tarea2", "main.py")

if not os.path.exists(TAREA2_MAIN):
    sys.exit(f"Error: no se encontró {TAREA2_MAIN}")

print("=== Orquestador Principal — Tarea 2: Ruteo Resiliente de Drones BVLOS ===")
print(f"Delegando ejecución a: {TAREA2_MAIN}")

resultado = subprocess.run([sys.executable, TAREA2_MAIN] + sys.argv[1:])
sys.exit(resultado.returncode)
