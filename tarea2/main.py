#!/usr/bin/env python3
"""Punto 9 de la rubrica - orquesta todo el pipeline de la Tarea 2:

  1. Levanta la base de datos (Docker: PostGIS + pgRouting) y el sitio web.
  2. Corre cada extractor de infraestructura/metadata/amenazas -> *.json.
  3. Carga cada *.json a su tabla correspondiente en la BD.
  4. Calcula la ruta de ejemplo con pgr_dijkstra y exporta las capas para
     el sitio web (Leaflet).

Uso:  python3 main.py            (requiere Docker y docker compose)
      python3 main.py --sin-docker   (asume que ya tenes Postgres accesible
                                       por las variables de entorno DB_*)
"""
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))

# (script, directorio) - orden importa: infraestructura y carabineros antes
# que la ruta de ejemplo; cada extractor antes de su loader.
PASOS_EXTRACCION = [
    ("infraestructura/extraer_infraestructura.py", "infraestructura"),
    ("infraestructura/extraer_carabineros.py", "infraestructura"),
    ("metadata/extraer_viento.py", "metadata"),
    ("metadata/extraer_tendido_electrico.py", "metadata"),
    ("metadata/extraer_relieve.py", "metadata"),
    ("metadata/extraer_poblacion.py", "metadata"),
    ("amenazas/extraer_firms.py", "amenazas"),
    ("amenazas/extraer_conaf.py", "amenazas"),
    ("amenazas/extraer_sismos.py", "amenazas"),
]

PASOS_CARGA = [
    ("infraestructura/cargar_infraestructura.py", "infraestructura"),
    ("infraestructura/cargar_carabineros.py", "infraestructura"),
    ("metadata/cargar_viento.py", "metadata"),
    ("metadata/cargar_tendido_electrico.py", "metadata"),
    ("metadata/cargar_relieve.py", "metadata"),
    ("metadata/cargar_poblacion.py", "metadata"),
    ("amenazas/cargar_firms.py", "amenazas"),
    ("amenazas/cargar_conaf.py", "amenazas"),
    ("amenazas/cargar_sismos.py", "amenazas"),
]

PASOS_SITIO = [
    ("sitio_web/generar_ruta_ejemplo.py", "sitio_web"),
    ("sitio_web/exportar_capas_web.py", "sitio_web"),
]


def correr(script_rel, cwd_rel, env):
    ruta_script = os.path.join(RAIZ, script_rel)
    if not os.path.exists(ruta_script):
        print(f"  [saltado] {script_rel} (no existe todavía)")
        return
    print(f"  -> {script_rel}")
    resultado = subprocess.run(
        [sys.executable, os.path.basename(script_rel)],
        cwd=os.path.join(RAIZ, cwd_rel),
        env=env,
    )
    if resultado.returncode != 0:
        raise SystemExit(f"Falló: {script_rel} (código {resultado.returncode})")


def main():
    sys.stdout.reconfigure(line_buffering=True)
    sin_docker = "--sin-docker" in sys.argv

    if not sin_docker:
        print("1. Levantando Docker (BD + sitio web)...")
        subprocess.run(["docker", "compose", "up", "-d", "--build"], cwd=RAIZ, check=True)
        print("   Esperando que la BD esté healthy...")
        for _ in range(30):
            chequeo = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Health.Status}}", "ruteo_db"],
                capture_output=True, text=True,
            )
            if chequeo.stdout.strip() == "healthy":
                break
            time.sleep(2)
        else:
            raise SystemExit("La BD no quedó healthy a tiempo.")

    env = os.environ.copy()
    env.setdefault("DB_HOST", "localhost")
    env.setdefault("DB_PORT", "5432")
    env.setdefault("DB_NAME", "ruteo_drones")
    env.setdefault("DB_USER", "ruteo")
    env.setdefault("DB_PASSWORD", "ruteo")

    print("\n2. Extracción (API -> JSON)...")
    for script, carpeta in PASOS_EXTRACCION:
        correr(script, carpeta, env)

    print("\n3. Carga (JSON -> BD)...")
    for script, carpeta in PASOS_CARGA:
        correr(script, carpeta, env)

    print("\n4. Ruta de ejemplo + capas del sitio web...")
    for script, carpeta in PASOS_SITIO:
        correr(script, carpeta, env)

    print("\nListo. Sitio disponible en http://localhost:8080")


if __name__ == "__main__":
    main()
