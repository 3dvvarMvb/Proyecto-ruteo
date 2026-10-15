"""Punto 2 de la rubrica - Metadata: Tendido Electrico Aereo (OSM/Overpass).
Extrae lineas de media/alta tension y distribucion en el Gran Valparaiso
y las transforma a tendido_electrico.json.
"""
import json
import os
import requests

try:
    from shapely.geometry import LineString, box
    HAVE_SHAPELY = True
except ImportError:
    HAVE_SHAPELY = False

AQUI = os.path.dirname(os.path.abspath(__file__))
TAREA1_DATOS = os.environ.get("TAREA1_DATOS", os.path.join(AQUI, "../../codigo/evidencia/datos"))

URL = "https://overpass-api.de/api/interpreter"
BBOX_STR = "-33.25,-71.75,-32.7,-71.15"  # s,w,n,e
CACHE_TAREA1 = os.path.join(TAREA1_DATOS, "osm_tendido_electrico.json")

salida_path = os.path.join(AQUI, "tendido_electrico.json")

data = None
try:
    print("Consultando Overpass API (tendido eléctrico)...")
    QUERY = f"""
    [out:json][timeout:10][maxsize:536870912];
    (
      way["power"="line"]({BBOX_STR});
      way["power"="minor_line"]({BBOX_STR});
    );
    out geom;
    """
    resp = requests.post(
        URL,
        data={"data": QUERY},
        timeout=6,
        headers={"User-Agent": "ruteo-drones-bvlos/2.0 (udp-proyecto)"},
    )
    if resp.status_code == 200:
        data = resp.json()
except Exception as e:
    print(f"Aviso: Overpass en vivo no respondió o tardó ({e}). Buscando respaldo...")

if not data and os.path.exists(CACHE_TAREA1):
    print("Cargando desde cache local de Tarea 1...")
    with open(CACHE_TAREA1, encoding="utf-8") as f:
        data = json.load(f)

if not data:
    if os.path.exists(salida_path) and os.path.getsize(salida_path) > 1000:
        print(f"OK: Reutilizando {salida_path} validado ({os.path.getsize(salida_path)} bytes).")
        raise SystemExit(0)
    raise SystemExit("Error: No se pudo obtener datos de tendido eléctrico.")

elements = data.get("elements", [])
salida = []
id_seq = 1

if HAVE_SHAPELY:
    BBOX_BOX = box(-71.75, -33.25, -71.15, -32.7)
    for el in elements:
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [(pt["lon"], pt["lat"]) for pt in el["geometry"]]
        if len(coords) < 2:
            continue
        linea = LineString(coords)
        inter = linea.intersection(BBOX_BOX)
        if inter.is_empty:
            continue
        tipo = el.get("tags", {}).get("power", "line")
        geoms = inter.geoms if hasattr(inter, "geoms") else [inter]
        for g in geoms:
            if g.is_empty or len(g.coords) < 2:
                continue
            longitud_m = g.length * 111_000
            salida.append({
                "id": id_seq,
                "tipo": tipo,
                "longitud_m": round(float(longitud_m), 1),
                "geom_wkt": g.wkt,
            })
            id_seq += 1
else:
    # Parser alternativo sin dependencia de shapely
    for el in elements:
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [(pt["lon"], pt["lat"]) for pt in el["geometry"]]
        # Filtrar puntos dentro del bbox aproximado
        coords_in = [c for c in coords if -71.75 <= c[0] <= -71.15 and -33.25 <= c[1] <= -32.7]
        if len(coords_in) < 2:
            continue
        tipo = el.get("tags", {}).get("power", "line")
        wkt = f"LINESTRING ({', '.join(f'{c[0]} {c[1]}' for c in coords_in)})"
        # Calcular largo aproximado
        largo_deg = sum(((coords_in[i][0]-coords_in[i-1][0])**2 + (coords_in[i][1]-coords_in[i-1][1])**2)**0.5 for i in range(1, len(coords_in)))
        salida.append({
            "id": id_seq,
            "tipo": tipo,
            "longitud_m": round(float(largo_deg * 111_000), 1),
            "geom_wkt": wkt,
        })
        id_seq += 1

salida_path = os.path.join(AQUI, "tendido_electrico.json")
with open(salida_path, "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False)

print(f"OK: {len(salida)} tramos de tendido eléctrico guardados en {salida_path}")
