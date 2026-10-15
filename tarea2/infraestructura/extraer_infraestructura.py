"""Punto 1 de la rubrica - Infraestructura: extrae y transforma el grafo vial
(nodos y aristas) a JSON.

Fuente: extracto local de OpenStreetMap via Geofabrik (ver codigo/RESULTADOS.md
de la Tarea 1 - Overpass en vivo se descarto por inestable). Este script NO
vuelve a descargar el .pbf (pesado); parte de los .gpkg ya generados por
codigo/construir_grafo_local.py en la Tarea 1 o de los .json ya extraidos.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TAREA1_DATOS = os.environ.get("TAREA1_DATOS", os.path.join(AQUI, "../../codigo/evidencia/datos"))
SALIDA = AQUI

# Si los JSON ya existen y tienen contenido, los reutiliza directamente
nodos_path = os.path.join(SALIDA, "nodos.json")
aristas_path = os.path.join(SALIDA, "aristas.json")

if os.path.exists(nodos_path) and os.path.exists(aristas_path) and os.path.getsize(aristas_path) > 1000:
    print(f"OK: {nodos_path} y {aristas_path} ya existen y están listos.")
    sys.exit(0)

try:
    import geopandas as gpd
except ImportError:
    sys.exit("Error: geopandas es requerido si no existen nodos.json ni aristas.json.")

print("Cargando grafo vial (Tarea 1)...")
nodos = gpd.read_file(f"{TAREA1_DATOS}/nodos_valparaiso.gpkg")
aristas = gpd.read_file(f"{TAREA1_DATOS}/aristas_valparaiso.gpkg")
print(f"  {len(nodos):,} nodos, {len(aristas):,} aristas")

# --- nodos.json ---
nodos_json = []
for _, row in nodos.iterrows():
    osmid = int(row["osmid"])
    nodos_json.append({
        "id": osmid,
        "osmid": osmid,
        "lon": round(row.geometry.x, 7),
        "lat": round(row.geometry.y, 7),
    })

with open(nodos_path, "w", encoding="utf-8") as f:
    json.dump(nodos_json, f, ensure_ascii=False)
print(f"Guardado {nodos_path} ({len(nodos_json):,} nodos)")

# --- aristas.json ---
aristas_json = []
next_id = 1
for _, row in aristas.iterrows():
    length_m = row.get("length")
    if length_m is None:
        length_m = row.geometry.length * 111_000  # fallback aproximado
    osmid_raw = row["osmid"]
    if isinstance(osmid_raw, list):
        osmid_val = int(osmid_raw[0])
    elif isinstance(osmid_raw, str) and osmid_raw.startswith("["):
        osmid_val = int(osmid_raw.strip("[]").split(",")[0])
    else:
        osmid_val = int(osmid_raw)

    aristas_json.append({
        "id": next_id,
        "osmid": osmid_val,
        "source": int(row["u"]),
        "target": int(row["v"]),
        "highway": str(row.get("highway")) if row.get("highway") is not None else None,
        "surface": str(row.get("surface")) if "surface" in aristas.columns and row.get("surface") is not None else None,
        "oneway": bool(row.get("oneway")) if row.get("oneway") is not None else False,
        "length_m": round(float(length_m), 2),
        "geom_wkt": row.geometry.wkt,
    })
    next_id += 1

with open(aristas_path, "w", encoding="utf-8") as f:
    json.dump(aristas_json, f, ensure_ascii=False)
print(f"Guardado {aristas_path} ({len(aristas_json):,} aristas)")
