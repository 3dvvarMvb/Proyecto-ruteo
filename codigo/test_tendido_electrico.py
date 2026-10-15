"""Metadata #2 (reemplazo de altura de edificacion) - Tendido electrico aereo.

Justificacion: los cables de alta/media tension son un riesgo de colision
fisico y directo para un dron de bajo vuelo, especialmente relevante en los
cerros de Valparaiso donde el tendido sobre las calles es denso y bajo.
Penaliza el costo de una arista del grafo vial (a diferencia de las
comisarias, que definen nodos especiales de origen/carga).

Fuente: Overpass API (tags power=line / power=minor_line de OpenStreetMap).
Nota: Overpass volvio a mostrarse inestable (504 Gateway Timeout en los
primeros intentos con "out geom"), igual que en las pruebas anteriores del
grupo; funciono al reintentar con [maxsize] mas alto. Para la Tarea 2 se
recomienda descargar esto con anticipacion y guardarlo, igual que se hizo
con el grafo vial (plan B: Geofabrik + osmium tags-filter w/power).
"""
import json
import os
import time
import requests
from shapely.geometry import LineString, box

URL = "https://overpass-api.de/api/interpreter"
BBOX = "-33.25,-71.75,-32.7,-71.15"  # Gran Valparaíso
QUERY = f"""
[out:json][timeout:120][maxsize:536870912];
(
  way["power"="line"]({BBOX});
  way["power"="minor_line"]({BBOX});
);
out geom;
"""
CACHE = "evidencia/datos/osm_tendido_electrico.json"

# Overpass se mostro inestable en pruebas anteriores de este grupo (504
# Gateway Timeout bajo carga); se reutiliza el resultado cacheado si existe,
# y si no, se reintenta varias veces antes de fallar.
if os.path.exists(CACHE):
    print(f"Usando resultado cacheado en {CACHE} (borrarlo para forzar una nueva consulta)")
    with open(CACHE, encoding="utf-8") as f:
        data = json.load(f)
else:
    data = None
    for intento in range(1, 4):
        try:
            resp = requests.post(
                URL,
                data={"data": QUERY},
                timeout=150,
                headers={"User-Agent": "ruteo-resiliente-drones/1.0 (tarea1-uni)"},
            )
            resp.raise_for_status()
            data = resp.json()
            print("HTTP", resp.status_code, f"(intento {intento})")
            break
        except requests.exceptions.HTTPError as e:
            print(f"Intento {intento} falló: {e}")
            time.sleep(5)
    if data is None:
        raise SystemExit("Overpass no respondió tras 3 intentos. Reintentar más tarde.")

ways = data.get("elements", [])

print("Líneas eléctricas (ways) encontradas:", len(ways))

por_tipo = {}
largo_total_km = 0.0
largo_sin_recortar_km = 0.0
from math import radians, sin, cos, sqrt, atan2

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

def largo_linea_km(coords):
    return sum(haversine_km(coords[i][1], coords[i][0], coords[i+1][1], coords[i+1][0]) for i in range(len(coords) - 1))

# Overpass devuelve la geometria COMPLETA de cada way aunque solo un tramo
# cruce el bbox (mismo problema que se detecto antes con FIRMS) - hay que
# recortar cada linea al area real del Gran Valparaiso antes de medir.
area = box(-71.75, -33.25, -71.15, -32.7)  # west, south, east, north

for w in ways:
    tipo = w.get("tags", {}).get("power", "desconocido")
    por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
    geom = w.get("geometry", [])
    coords = [(p["lon"], p["lat"]) for p in geom]
    if len(coords) < 2:
        continue
    largo_sin_recortar_km += largo_linea_km(coords)
    recortada = LineString(coords).intersection(area)
    if recortada.is_empty:
        continue
    if recortada.geom_type == "LineString":
        largo_total_km += largo_linea_km(list(recortada.coords))
    elif recortada.geom_type == "MultiLineString":
        for parte in recortada.geoms:
            largo_total_km += largo_linea_km(list(parte.coords))

print("Por tipo:", por_tipo)
print(f"Largo SIN recortar (bug tipo-FIRMS, incluye tramos fuera del área): {largo_sin_recortar_km:.1f} km")
print(f"Largo REAL dentro del Gran Valparaíso (recortado al bbox): {largo_total_km:.1f} km")

with open(CACHE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
print(f"\nGuardado en {CACHE}")
