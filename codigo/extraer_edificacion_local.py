"""Reemplaza la consulta en vivo a Overpass (Fuente 2, altura de edificacion)
por el extracto local de Geofabrik, ya que Overpass demostro ser poco
confiable durante las pruebas del grupo. Parsea el XML de OSM directamente
(no hace falta osmnx para esto, solo tags de las ways)."""
import xml.etree.ElementTree as ET
import json
import csv

XML_PATH = "data/valparaiso_buildings.osm.xml"
EVID = "evidencia/datos"

tree = ET.parse(XML_PATH)
root = tree.getroot()

total_ways = 0
con_levels = []
con_height = []

for way in root.iter("way"):
    total_ways += 1
    tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
    if "building:levels" in tags or "height" in tags:
        con_levels.append({
            "way_id": way.get("id"),
            "building": tags.get("building", "-"),
            "building:levels": tags.get("building:levels", "-"),
            "height": tags.get("height", "-"),
        })

print(f"Total de ways con tag building=*: {total_ways}")
print(f"Con building:levels o height: {len(con_levels)}")

with open(f"{EVID}/overpass_local_edificacion.json", "w", encoding="utf-8") as f:
    json.dump({"total_edificios": total_ways, "con_altura": len(con_levels), "elementos": con_levels}, f, ensure_ascii=False, indent=2)

with open(f"{EVID}/overpass_local_edificacion.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["way_id", "building", "building:levels", "height"])
    w.writeheader()
    w.writerows(con_levels)

print("Guardado en evidencia/overpass_local_edificacion.{json,csv}")
