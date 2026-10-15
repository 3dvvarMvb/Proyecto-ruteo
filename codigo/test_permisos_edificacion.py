"""Antiguedad de la edificacion (proxy, NO probabilidad de colapso) para
ampliar la Amenaza #3 (sismicidad) - ver RESULTADOS.md.

No existe en Chile una API publica que indique que edificios cumplen la
norma antisismica (depende de permisos municipales DOM no digitalizados de
forma abierta/centralizada). Se usa en cambio como proxy parcial el dataset
publico "Permisos de Edificacion Georreferenciados en Chile 2010-2018"
(Observatorio de Ciudades UC, mismo publicador que la Metadata #3 INE),
Feature Service ArcGIS sin API key.

Limitacion a declarar: "sin permiso en la ventana 2010-2018" no es lo mismo
que "antigua e incumple la norma" (podria tener permiso anterior a 2010 o
posterior a 2018). Se usa solo como indicador agregado por zona, nunca como
probabilidad de colapso por edificio individual.
"""
import json
import requests

URL = "https://services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Permisos_edificacion_2010_2018/FeatureServer/0/query"
COMUNAS = ["Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana"]
TOTAL_EDIFICIOS_OSM = 74550  # ver overpass_local_edificacion.json / extraer_edificacion_local.py

resultados = {}
for comuna in COMUNAS:
    params = {"where": f"GLOSA_COMU='{comuna}'", "returnCountOnly": "true", "f": "json"}
    resp = requests.get(URL, params=params, timeout=20)
    resp.raise_for_status()
    resultados[comuna] = resp.json()["count"]
    print(f"{comuna}: {resultados[comuna]} permisos (2010-2018)")

total_permisos = sum(resultados.values())
print(f"\nTotal permisos 2010-2018 (Gran Valparaíso): {total_permisos}")
print(f"Total edificios OSM (Gran Valparaíso): {TOTAL_EDIFICIOS_OSM}")
print(f"% edificación con permiso reciente: {total_permisos / TOTAL_EDIFICIOS_OSM * 100:.1f}%")
print(f"% edificación sin permiso en esa ventana (proxy de antigüedad, NO probabilidad de colapso): {(1 - total_permisos / TOTAL_EDIFICIOS_OSM) * 100:.1f}%")

salida = {
    "fuente": "Permisos de Edificación Georreferenciados en Chile 2010-2018 (Observatorio de Ciudades UC)",
    "url": URL.replace("/query", ""),
    "permisos_por_comuna": resultados,
    "total_permisos_2010_2018": total_permisos,
    "total_edificios_osm": TOTAL_EDIFICIOS_OSM,
    "pct_con_permiso_reciente": round(total_permisos / TOTAL_EDIFICIOS_OSM * 100, 1),
    "pct_sin_permiso_reciente": round((1 - total_permisos / TOTAL_EDIFICIOS_OSM) * 100, 1),
    "nota": "No es probabilidad de colapso por edificio; es un proxy agregado de antigüedad relativa por zona.",
}
with open("evidencia/datos/permisos_edificacion_2010_2018.json", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
print("\nGuardado en evidencia/datos/permisos_edificacion_2010_2018.json")
