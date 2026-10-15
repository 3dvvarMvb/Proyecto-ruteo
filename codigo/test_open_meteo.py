"""Fuente 1 - Open-Meteo API (viento, rachas, direccion, visibilidad).

Se consultan 6 puntos en el Gran Valparaiso en vez de uno solo: uno por cada
comuna (Vina del Mar, Concon, Quilpue, Villa Alemana), mas un punto extra
en Valparaiso para distinguir plan/costa de cerros/interior alto (Placilla),
que es donde la diferencia de altitud genera un cambio de viento real.

No se agregaron mas puntos "de relleno": se probo con un punto costa/interior
tambien para Vina del Mar, pero el modelo de pronostico de Open-Meteo tiene
una resolucion de grilla de ~11 km, y esos puntos cayeron en la misma celda
que Concon y Quilpue respectivamente (mismos valores exactos devueltos) -
ver RESULTADOS.md. Por eso el limite practico de puntos distinguibles para
esta area es de unos 5-6, no mas, salvo que se pague un modelo de mayor
resolucion.

Ademas de la magnitud (velocidad/rachas) se pide wind_direction_10m, porque
el viento no solo deberia penalizar una arista por ser "fuerte": importa el
angulo entre la direccion del viento y la orientacion de la calle (viento de
frente consume mas bateria y es mas riesgoso que viento de cola o costado),
lo que conecta ademas con la autonomia del dron y los puntos de carga
(test_carabineros.py).
"""
import json
import requests

URL = "https://api.open-meteo.com/v1/forecast"

PUNTOS = [
    {"comuna": "Valparaíso", "sector": "Plan / costa",                 "lat": -33.0488, "lon": -71.6188, "ref": "Prefectura de Carabs. Valparaíso"},
    {"comuna": "Valparaíso", "sector": "Cerros / Placilla (interior alto)", "lat": -33.1147, "lon": -71.5766, "ref": "Retén Placilla Peñuelas"},
    {"comuna": "Viña del Mar",   "sector": "—", "lat": -33.0192, "lon": -71.5558, "ref": "Prefectura de Carabs. Viña del Mar"},
    {"comuna": "Concón",         "sector": "—", "lat": -32.9224, "lon": -71.5129, "ref": "Subcom. Concón"},
    {"comuna": "Quilpué",        "sector": "—", "lat": -33.0553, "lon": -71.4388, "ref": "2da Com. Quilpué"},
    {"comuna": "Villa Alemana",  "sector": "—", "lat": -33.0433, "lon": -71.3710, "ref": "6ta Com. Villa Alemana"},
]

params = {
    "latitude": ",".join(str(p["lat"]) for p in PUNTOS),
    "longitude": ",".join(str(p["lon"]) for p in PUNTOS),
    "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m,visibility",
    "timezone": "America/Santiago",
}

resp = requests.get(URL, params=params, timeout=20)
resp.raise_for_status()
data = resp.json()  # lista de respuestas, una por punto (mismo orden que PUNTOS)

print("HTTP", resp.status_code)
print("URL final:", resp.url)
print(f"\nPuntos consultados: {len(data)}")

celdas_vistas = {}
resumen = []
for punto, resultado in zip(PUNTOS, data):
    viento = resultado["hourly"]["wind_speed_10m"]
    rachas = resultado["hourly"]["wind_gusts_10m"]
    direccion = resultado["hourly"]["wind_direction_10m"]
    unidad = resultado["hourly_units"]["wind_speed_10m"]
    etiqueta = f"{punto['comuna']} ({punto['sector']})" if punto["sector"] != "—" else punto["comuna"]

    celda = (round(resultado["latitude"], 3), round(resultado["longitude"], 3))
    duplicado = celdas_vistas.get(celda)
    celdas_vistas[celda] = etiqueta

    print(f"\n[{etiqueta}] pedido lat={punto['lat']}, lon={punto['lon']} -> celda del modelo {celda} (elev. {resultado['elevation']} m)")
    if duplicado:
        print(f"  ⚠️ MISMA CELDA que '{duplicado}' (resolución del modelo ~11 km) — valores idénticos, no aporta info nueva")
    print(f"  Viento 10m ({unidad}) primeras 3h: {viento[:3]}")
    print(f"  Rachas 10m ({unidad}) primeras 3h: {rachas[:3]}")
    print(f"  Dirección (°, de donde sopla) primeras 3h: {direccion[:3]}")
    print(f"  Racha máxima del pronóstico: {max(rachas):.1f} {unidad}")
    resumen.append({
        "comuna": punto["comuna"],
        "sector": punto["sector"],
        "referencia": punto["ref"],
        "lat": punto["lat"],
        "lon": punto["lon"],
        "celda_modelo": celda,
        "elevacion_m": resultado["elevation"],
        "unidad": unidad,
        "viento_10m": viento,
        "rachas_10m": rachas,
        "direccion_10m": direccion,
        "racha_maxima": max(rachas),
    })

with open("evidencia/datos/open_meteo_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
with open("evidencia/datos/open_meteo_resumen_por_comuna.json", "w", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)

print("\nGuardado en evidencia/datos/open_meteo_response.json")
print("Guardado en evidencia/datos/open_meteo_resumen_por_comuna.json")
