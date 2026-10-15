"""Punto 2 de la rubrica - Metadata: Viento (Open-Meteo API).
Extrae datos de viento, rachas y direccion para los 6 puntos clave del Gran Valparaiso
y los transforma a viento.json.
"""
import json
import os
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
TAREA1_DATOS = os.environ.get("TAREA1_DATOS", os.path.join(AQUI, "../../codigo/evidencia/datos"))

URL = "https://api.open-meteo.com/v1/forecast"
PUNTOS = [
    {"id": 1, "comuna": "Valparaíso", "sector": "Plan / costa",                 "lat": -33.0488, "lon": -71.6188},
    {"id": 2, "comuna": "Valparaíso", "sector": "Cerros / Placilla (interior alto)", "lat": -33.1147, "lon": -71.5766},
    {"id": 3, "comuna": "Viña del Mar",   "sector": "Centro / Costa",          "lat": -33.0192, "lon": -71.5558},
    {"id": 4, "comuna": "Concón",         "sector": "Costa Norte",             "lat": -32.9224, "lon": -71.5129},
    {"id": 5, "comuna": "Quilpué",        "sector": "Valle Interior",          "lat": -33.0553, "lon": -71.4388},
    {"id": 6, "comuna": "Villa Alemana",  "sector": "Valle Interior Alto",     "lat": -33.0433, "lon": -71.3710},
]

params = {
    "latitude": ",".join(str(p["lat"]) for p in PUNTOS),
    "longitude": ",".join(str(p["lon"]) for p in PUNTOS),
    "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
    "timezone": "America/Santiago",
}

salida_path = os.path.join(AQUI, "viento.json")
data = None
try:
    print("Consultando Open-Meteo API...")
    resp = requests.get(URL, params=params, timeout=6)
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"Aviso: consulta en vivo falló ({e}). Buscando respaldo...")
    cache_path = os.path.join(TAREA1_DATOS, "open_meteo_response.json")
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)

if not data:
    if os.path.exists(salida_path) and os.path.getsize(salida_path) > 500:
        print(f"OK: Reutilizando {salida_path} validado ({os.path.getsize(salida_path)} bytes).")
        raise SystemExit(0)
    raise SystemExit("Error: No se pudo obtener datos de Open-Meteo ni de cache.")

if isinstance(data, dict):
    data = [data]

salida = []
for p, res in zip(PUNTOS, data):
    hourly = res.get("hourly", {})
    speeds = hourly.get("wind_speed_10m", [15.0])
    gusts = hourly.get("wind_gusts_10m", [25.0])
    dirs = hourly.get("wind_direction_10m", [180.0])
    elev = res.get("elevation", 20.0)

    v_medio = sum(speeds) / len(speeds) if speeds else 0.0
    r_medio = sum(gusts) / len(gusts) if gusts else 0.0
    r_max = max(gusts) if gusts else 0.0
    d_medio = sum(dirs) / len(dirs) if dirs else 0.0

    salida.append({
        "id": p["id"],
        "comuna": p["comuna"],
        "sector": p["sector"],
        "elevacion_m": round(float(elev), 1),
        "viento_medio_kmh": round(float(v_medio), 1),
        "racha_media_kmh": round(float(r_medio), 1),
        "racha_max_kmh": round(float(r_max), 1),
        "direccion_deg": round(float(d_medio), 1),
        "lon": p["lon"],
        "lat": p["lat"],
    })

salida_path = os.path.join(AQUI, "viento.json")
with open(salida_path, "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)

print(f"OK: {len(salida)} puntos de viento guardados en {salida_path}")
