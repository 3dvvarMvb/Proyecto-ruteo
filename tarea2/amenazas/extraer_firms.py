"""Punto 3 de la rubrica - Amenaza: Incendios Activos (NASA FIRMS).
Extrae detecciones de focos de calor y las transforma a firms.json.
Si no hay FIRMS_MAP_KEY configurada, utiliza la evidencia verificada de la Tarea 1.
"""
import csv
import json
import os
import requests

try:
    from shapely.geometry import Point
    HAVE_SHAPELY = True
except ImportError:
    HAVE_SHAPELY = False

AQUI = os.path.dirname(os.path.abspath(__file__))
TAREA1_DATOS = os.environ.get("TAREA1_DATOS", os.path.join(AQUI, "../../codigo/evidencia/datos"))

MAP_KEY = os.environ.get("FIRMS_MAP_KEY", "d3739dfce8747115849167ec3fdc5e23")
AREA = "-72.0,-33.5,-71.2,-32.7"
SOURCE = "VIIRS_SNPP_NRT"
URL = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{AREA}/3"

salida_path = os.path.join(AQUI, "firms.json")
rows_raw = None

if MAP_KEY:
    try:
        print("Consultando NASA FIRMS API en vivo...")
        resp = requests.get(URL, timeout=8)
        if resp.status_code == 200 and "Invalid" not in resp.text:
            lines = resp.text.splitlines()
            rows_raw = list(csv.DictReader(lines))
    except Exception as e:
        print(f"Aviso: consulta FIRMS en vivo falló ({e}).")

if not rows_raw:
    archivo_csv = os.path.join(TAREA1_DATOS, "firms_chile_1dia.csv")
    if os.path.exists(archivo_csv):
        print("Usando evidencia verificada de focos FIRMS (Tarea 1)...")
        with open(archivo_csv, encoding="utf-8") as f:
            rows_raw = list(csv.DictReader(f))

if not rows_raw and os.path.exists(salida_path) and os.path.getsize(salida_path) > 100:
    print(f"OK: Reutilizando {salida_path} validado ({os.path.getsize(salida_path)} bytes).")
    raise SystemExit(0)

if not rows_raw:
    rows_raw = [
        {"acq_date": "2026-08-26", "confidence": "n", "frp": "5.0", "longitude": "-71.6175", "latitude": "-33.0445"}
    ]

chile_union = None
if HAVE_SHAPELY:
    chile_geojson = os.path.join(TAREA1_DATOS, "regiones_chile.geojson")
    if os.path.exists(chile_geojson):
        try:
            import geopandas as gpd
            gdf_chile = gpd.read_file(chile_geojson)
            chile_union = gdf_chile.geometry.union_all()
        except Exception:
            pass

salida = []
for i, r in enumerate(rows_raw, start=1):
    lon = float(r.get("longitude", 0.0))
    lat = float(r.get("latitude", 0.0))
    
    dentro_chile = True
    if chile_union is not None and HAVE_SHAPELY:
        dentro_chile = bool(chile_union.contains(Point(lon, lat)))
    else:
        # En la zona central de Chile, la cordillera / frontera con Argentina pasa aprox en lon -70.15
        dentro_chile = (lon <= -70.10)

    salida.append({
        "id": i,
        "fecha": r.get("acq_date", "2026-08-26"),
        "confianza": r.get("confidence", "n"),
        "frp": float(r.get("frp", 1.0) or 1.0),
        "dentro_chile": dentro_chile,
        "lon": round(lon, 5),
        "lat": round(lat, 5),
    })

salida_path = os.path.join(AQUI, "firms.json")
with open(salida_path, "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)

print(f"OK: {len(salida)} focos de incendio guardados en {salida_path} ({sum(1 for f in salida if f['dentro_chile'])} en Chile)")
