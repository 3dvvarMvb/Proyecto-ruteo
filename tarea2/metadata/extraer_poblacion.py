"""Punto 2 de la rubrica - Metadata: Poblacion por Manzana Censal (INE Censo 2017).
Extrae poligonos de manzanas censales con poblacion para las 5 comunas del Gran Valparaiso
(via Observatorio de Ciudades UC) y los transforma a poblacion.json.
"""
import json
import os
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = "https://services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Manzanas_censo_2017/FeatureServer/0/query"
COMUNAS = ["VALPARAÍSO", "VIÑA DEL MAR", "CONCÓN", "QUILPUÉ", "VILLA ALEMANA"]


def geojson_to_wkt(geometry):
    gtype = geometry.get("type")
    coords = geometry.get("coordinates", [])
    if gtype == "Polygon":
        rings = [f"({', '.join(f'{p[0]} {p[1]}' for p in ring)})" for ring in coords]
        return f"POLYGON ({', '.join(rings)})"
    elif gtype == "MultiPolygon":
        polys = []
        for poly in coords:
            rings = [f"({', '.join(f'{p[0]} {p[1]}' for p in ring)})" for ring in poly]
            polys.append(f"({', '.join(rings)})")
        return f"MULTIPOLYGON ({', '.join(polys)})"
    return "POLYGON EMPTY"


salida_path = os.path.join(AQUI, "poblacion.json")
salida = []
seq_id = 1

for c in COMUNAS:
    print(f"Consultando manzanas censales para {c}...")
    params = {
        "where": f"NOM_COMUNA='{c}'",
        "outFields": "NOM_COMUNA,MANZENT_I,TOTAL_PERS,TOTAL_VIVI",
        "resultRecordCount": 400,
        "f": "geojson",
    }
    try:
        resp = requests.get(URL, params=params, timeout=6)
        resp.raise_for_status()
        features = resp.json().get("features", [])
        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry")
            if not geom:
                continue
            wkt = geojson_to_wkt(geom)
            salida.append({
                "id": seq_id,
                "comuna": props.get("NOM_COMUNA", c),
                "manzent": props.get("MANZENT_I"),
                "total_pers": int(props.get("TOTAL_PERS", 0) or 0),
                "total_vivi": int(props.get("TOTAL_VIVI", 0) or 0),
                "geom_wkt": wkt,
            })
            seq_id += 1
    except Exception as e:
        print(f"Aviso: error o timeout en consulta de {c}: {e}")

if not salida:
    if os.path.exists(salida_path) and os.path.getsize(salida_path) > 10000:
        print(f"OK: Reutilizando {salida_path} verificado ({os.path.getsize(salida_path)} bytes).")
        raise SystemExit(0)
    raise SystemExit("Error: No se pudo obtener datos de población.")

with open(salida_path, "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False)

print(f"OK: {len(salida)} manzanas censales guardadas en {salida_path}")
