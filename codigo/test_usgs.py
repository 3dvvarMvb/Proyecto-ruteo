"""Amenaza 3 - USGS FDSN Event API (sismos), respaldo del CSN."""
import json
import requests

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
params = {
    "format": "geojson",
    "minlatitude": -33.5,
    "maxlatitude": -32.7,
    "minlongitude": -72.0,
    "maxlongitude": -71.2,
    "minmagnitude": 2,
    "starttime": "2015-01-01",
}

resp = requests.get(URL, params=params, timeout=20)
resp.raise_for_status()
data = resp.json()

print("HTTP", resp.status_code)
print("URL final:", resp.url)
print("Eventos encontrados:", len(data["features"]))
for feat in data["features"][:5]:
    p = feat["properties"]
    lon, lat, depth = feat["geometry"]["coordinates"]
    print(f"  mag={p['mag']} lugar={p['place']} lat={lat:.3f} lon={lon:.3f} prof={depth}km")

with open("evidencia/usgs_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Guardado en evidencia/usgs_response.json")
