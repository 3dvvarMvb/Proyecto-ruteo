"""Nodo de origen/carga - Cuarteles de Carabineros (comisarías, tenencias, retenes).

Hallazgo: dataset publico de Carabineros de Chile (nivel nacional, 929 cuarteles),
republicado como Feature Service ArcGIS por un tercero, sin API key:

  https://services6.arcgis.com/LCdFQd7nnAn5xeUA/arcgis/rest/services/Cuarteles_Carabineros/FeatureServer/0

Incluye lat/lon, nombre de unidad, comuna y region para cada cuartel. Se usa
como fuente de los posibles nodos de origen/carga del dron (comisarias y
otras unidades con presencia permanente de Carabineros).
"""
import json
import requests

URL = "https://services6.arcgis.com/LCdFQd7nnAn5xeUA/arcgis/rest/services/Cuarteles_Carabineros/FeatureServer/0/query"
COMUNAS = ["Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana"]

where = " OR ".join([f"comuna='{c}'" for c in COMUNAS])
params = {
    "where": where,
    "outFields": "nombre,categ,tipo,comuna,region,lat,lon",
    "f": "geojson",
}

resp = requests.get(URL, params=params, timeout=25)
resp.raise_for_status()
data = resp.json()
feats = data.get("features", [])

print("HTTP", resp.status_code)
print("Cuarteles encontrados en el Gran Valparaíso:", len(feats))

es_comisaria = [f for f in feats if "COM." in f["properties"]["nombre"] and "SUBCOM" not in f["properties"]["nombre"]]
print("De los cuales son Comisarías propiamente tales:", len(es_comisaria))

por_comuna = {}
for f in feats:
    c = f["properties"]["comuna"]
    por_comuna[c] = por_comuna.get(c, 0) + 1
print("Por comuna:", por_comuna)

for f in feats:
    p = f["properties"]
    print(f"  [{p['comuna']}] {p['nombre']}  ({p['lat']:.4f}, {p['lon']:.4f})")

with open("evidencia/datos/carabineros_cuarteles_gran_valparaiso.geojson", "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
print("\nGuardado en evidencia/datos/carabineros_cuarteles_gran_valparaiso.geojson")
