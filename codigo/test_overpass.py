"""Fuente 2 - Overpass API (altura de edificacion, para f_obstaculo)."""
import json
import requests

URL = "https://overpass-api.de/api/interpreter"
QUERY = """
[out:json][timeout:25];
area["name"="Valparaíso"]["admin_level"="6"]->.a;
(
  way(area.a)["building:levels"];
);
out geom 20;
"""

resp = requests.post(
    URL,
    data={"data": QUERY},
    timeout=40,
    headers={"User-Agent": "ruteo-resiliente-drones/1.0 (tarea1-uni)"},
)
resp.raise_for_status()
data = resp.json()

print("HTTP", resp.status_code)
print("Elementos devueltos:", len(data.get("elements", [])))
for el in data.get("elements", [])[:5]:
    tags = el.get("tags", {})
    print(f"  way {el['id']}: building:levels={tags.get('building:levels')}, height={tags.get('height')}")

with open("evidencia/overpass_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Guardado en evidencia/overpass_response.json")
