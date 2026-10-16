"""Metadata adicional - Permisos de Edificacion (proxy de antiguedad de la
edificacion, NO probabilidad de colapso). Amplia la Amenaza #3 (sismicidad):
ver "Ampliacion: antiguedad de la edificacion como segundo factor de la
prioridad sismica" en codigo/RESULTADOS.md para la justificacion completa.

No existe en Chile una API publica que indique que edificios cumplen la
norma antisismica (depende de permisos municipales DOM no digitalizados de
forma abierta/centralizada). Se usa en cambio como proxy parcial el dataset
publico "Permisos de Edificacion Georreferenciados en Chile 2010-2018"
(Observatorio de Ciudades UC, mismo publicador que la Metadata de poblacion),
ya verificado en Tarea 1 (codigo/test_permisos_edificacion.py), ahora
extrayendo los puntos georreferenciados (no solo el conteo agregado) para
poder vincularlos espacialmente a las manzanas censales.

Limitacion a declarar: "sin permiso en la ventana 2010-2018" no es lo mismo
que "antigua e incumple la norma" (podria tener permiso anterior a 2010 o
posterior a 2018). Se usa solo como indicador agregado por zona, nunca como
probabilidad de colapso por edificio individual.
"""
import json
import os
import time
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
URL = "https://services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Permisos_edificacion_2010_2018/FeatureServer/0/query"
COMUNAS = ["Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana"]
PAGE_SIZE = 2000  # maxRecordCount real del servicio (confirmado via metadata del layer)

salida_path = os.path.join(AQUI, "permisos_edificacion.json")
salida = []
seq_id = 1

for comuna in COMUNAS:
    offset = 0
    total_comuna = 0
    while True:
        params = {
            "where": f"GLOSA_COMU='{comuna}'",
            "outFields": "GLOSA_COMU,AÑO,NUM_PISOS,SUPERFICIE",
            "resultRecordCount": PAGE_SIZE,
            "resultOffset": offset,
            "f": "geojson",
        }
        features = None
        for intento in range(3):
            try:
                resp = requests.get(URL, params=params, timeout=25)
                resp.raise_for_status()
                features = resp.json().get("features", [])
                break
            except Exception as e:
                print(f"Aviso: error en consulta de {comuna} (offset={offset}, intento {intento + 1}/3): {e}")
                if intento < 2:
                    time.sleep(5)

        if not features:
            break

        for feat in features:
            props = feat.get("properties", {})
            geom = feat.get("geometry")
            if not geom or geom.get("type") != "Point":
                continue
            lon, lat = geom["coordinates"][0], geom["coordinates"][1]
            salida.append({
                "id": seq_id,
                "comuna": props.get("GLOSA_COMU", comuna),
                "anio": props.get("AÑO"),
                "num_pisos": props.get("NUM_PISOS"),
                "superficie_m2": props.get("SUPERFICIE"),
                "lon": lon,
                "lat": lat,
            })
            seq_id += 1
            total_comuna += 1

        offset += PAGE_SIZE
        if len(features) < PAGE_SIZE:
            break

    print(f"{comuna}: {total_comuna} permisos (2010-2018)")

if not salida:
    if os.path.exists(salida_path) and os.path.getsize(salida_path) > 10000:
        print(f"OK: Reutilizando {salida_path} verificado ({os.path.getsize(salida_path)} bytes).")
        raise SystemExit(0)
    raise SystemExit("Error: No se pudo obtener datos de permisos de edificación.")

with open(salida_path, "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False)

print(f"OK: {len(salida)} permisos de edificación (2010-2018) guardados en {salida_path}")
