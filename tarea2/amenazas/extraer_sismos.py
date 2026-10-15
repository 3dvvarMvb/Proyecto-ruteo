"""Punto 3 de la rubrica - Amenaza: sismos (USGS FDSN), extrae y transforma a JSON."""
import json
import os
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
params = {
    "format": "geojson",
    "minlatitude": -33.5, "maxlatitude": -32.7,
    "minlongitude": -72.0, "maxlongitude": -71.2,
    "minmagnitude": 2,
    "starttime": "2015-01-01",
}

resp = requests.get(URL, params=params, timeout=20)
resp.raise_for_status()
data = resp.json()

salida = []
for feat in data["features"]:
    p = feat["properties"]
    lon, lat, prof = feat["geometry"]["coordinates"]
    salida.append({
        "usgs_id": feat["id"],
        "magnitud": p["mag"],
        "profundidad_km": prof,
        "fecha": p["time"],  # epoch ms UTC
        "lugar": p["place"],
        "lon": lon,
        "lat": lat,
    })

with open(f"{AQUI}/sismos.json", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
print(f"OK: {len(salida)} sismos guardados en sismos.json")
