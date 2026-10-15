"""Punto 1 de la rubrica - Infraestructura: extrae y transforma el grafo vial
(nodos y aristas) a JSON.

Fuente: extracto local de OpenStreetMap via Geofabrik (ver codigo/RESULTADOS.md
de la Tarea 1 - Overpass en vivo se descarto por inestable). Este script NO
vuelve a descargar el .pbf (pesado); parte de los .gpkg ya generados por
codigo/construir_grafo_local.py en la Tarea 1. Si no existen, hay que correr
ese script primero (requiere el extracto de Geofabrik).
"""
import json
import os
import geopandas as gpd

AQUI = os.path.dirname(os.path.abspath(__file__))
TAREA1_DATOS = os.environ.get("TAREA1_DATOS", os.path.join(AQUI, "../../codigo/evidencia/datos"))
SALIDA = AQUI

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

with open(f"{SALIDA}/nodos.json", "w", encoding="utf-8") as f:
    json.dump(nodos_json, f, ensure_ascii=False)
print(f"Guardado {SALIDA}/nodos.json ({len(nodos_json):,} nodos)")

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

with open(f"{SALIDA}/aristas.json", "w", encoding="utf-8") as f:
    json.dump(aristas_json, f, ensure_ascii=False)
print(f"Guardado {SALIDA}/aristas.json ({len(aristas_json):,} aristas)")
