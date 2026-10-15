"""Nodos especiales (origen/carga del dron) - Cuarteles de Carabineros.
Mismo hallazgo de la Tarea 1 (codigo/test_carabineros.py), reconsultado aca
para que el pipeline de la Tarea 2 sea autocontenido."""
import json
import os
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = "https://services6.arcgis.com/LCdFQd7nnAn5xeUA/arcgis/rest/services/Cuarteles_Carabineros/FeatureServer/0/query"
COMUNAS = ["Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana"]

where = " OR ".join([f"comuna='{c}'" for c in COMUNAS])
params = {"where": where, "outFields": "nombre,categ,tipo,comuna,lat,lon", "f": "geojson"}
resp = requests.get(URL, params=params, timeout=25)
resp.raise_for_status()
feats = resp.json()["features"]

salida = []
for i, feat in enumerate(feats, start=1):
    p = feat["properties"]
    nombre = p["nombre"]
    es_comisaria = "COM." in nombre and "SUBCOM" not in nombre
    salida.append({
        "id": i,
        "nombre": nombre,
        "comuna": p["comuna"],
        "es_comisaria": es_comisaria,
        "es_punto_carga": True,
        "lon": p["lon"],
        "lat": p["lat"],
    })

with open(f"{AQUI}/carabineros.json", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
print(f"OK: {len(salida)} cuarteles guardados en carabineros.json ({sum(1 for c in salida if c['es_comisaria'])} comisarías)")
