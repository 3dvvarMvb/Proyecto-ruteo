"""Amenaza 1 - NASA FIRMS API (focos activos). Requiere MAP_KEY gratuito.
Registro: https://firms.modaps.eosdis.nasa.gov/api/map_key/

Uso: FIRMS_MAP_KEY=xxxx python3 test_firms.py
Sin key, se documenta igualmente el comportamiento del endpoint (debe fallar de forma clara).
"""
import os
import requests

MAP_KEY = os.environ.get("FIRMS_MAP_KEY", "DEMO_KEY_INVALIDA")
SOURCE = "VIIRS_SNPP_NRT"
AREA = "-72.0,-33.5,-71.2,-32.7"  # west,south,east,north (Región de Valparaíso)
DAYS = 3

URL = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{AREA}/{DAYS}"

resp = requests.get(URL, timeout=20)
print("HTTP", resp.status_code)
print("URL:", URL.replace(MAP_KEY, "****"))
print("Primeras líneas de respuesta:")
print("\n".join(resp.text.splitlines()[:5]))

if "Invalid" in resp.text or resp.status_code != 200:
    print("\n[NOTA] MAP_KEY inválida o no configurada. Esto es esperado sin registro.")
    print("El endpoint SÍ responde (no está caído): confirma la accesibilidad del servicio.")
else:
    with open("evidencia/firms_response.csv", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Guardado en evidencia/firms_response.csv")

# Endpoint de estado de transacciones de la key (también requiere key, pero confirma el dominio)
status_url = f"https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY={MAP_KEY}"
status_resp = requests.get(status_url, timeout=15)
print("\nEstado de MAP_KEY -> HTTP", status_resp.status_code)
print(status_resp.text[:300])
