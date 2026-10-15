"""Metadata adicional - Pendiente del terreno (relieve).

Justificacion: Valparaiso es conocido por sus cerros empinados; una arista
con pendiente fuerte es mas exigente para el vuelo del dron (aerodinamica,
estabilidad) y reduce la linea de vista para el enlace de comando y control
(C2) con antenas en el corredor, afectando directo el "Argumento 3" del
informe. Penaliza el costo de la arista, igual que viento o tendido electrico.

Fuente: Open Topo Data (https://api.opentopodata.org, dataset SRTM 90m),
publica, sin API key (limite publico: 1 request/seg, 100 puntos/request).
Se probo primero con Open-Elevation (api.open-elevation.com) pero su
instancia publica devolvio 429 Too Many Requests de forma persistente;
Open Topo Data respondio bien y da valores consistentes con Open-Elevation
y con las elevaciones ya obtenidas de Open-Meteo para los mismos puntos
(ej. Valparaiso plan ~15-18m, Placilla ~324-330m en las 3 fuentes).

Se prueba sobre una muestra real de nodos/aristas del grafo vial local ya
construido (52.856 nodos, 126.480 aristas, ver construir_grafo_local.py),
no sobre coordenadas inventadas.
"""
import json
import random
import time
import requests
import geopandas as gpd

EVID = "evidencia/datos"
URL = "https://api.opentopodata.org/v1/srtm90m"
MUESTRA_ARISTAS = 300  # suficiente para probar feasibilidad sin saturar la API publica

print("Cargando grafo vial local...")
nodos = gpd.read_file(f"{EVID}/nodos_valparaiso.gpkg")
aristas = gpd.read_file(f"{EVID}/aristas_valparaiso.gpkg")
print(f"  {len(nodos):,} nodos, {len(aristas):,} aristas")

nodos = nodos.set_index("osmid") if "osmid" in nodos.columns else nodos

random.seed(42)
muestra = aristas.sample(n=min(MUESTRA_ARISTAS, len(aristas)), random_state=42)

# recolectar todos los nodos u/v necesarios para la muestra
ids_necesarios = set(muestra["u"]).union(set(muestra["v"]))
nodos_muestra = nodos.loc[nodos.index.intersection(ids_necesarios)]

print(f"\nConsultando elevación para {len(nodos_muestra)} nodos (Open Topo Data, por lotes de 100)...")
elevaciones = {}
ids = list(nodos_muestra.index)
for i in range(0, len(ids), 100):
    lote = ids[i:i+100]
    locs_str = "|".join(f"{nodos_muestra.loc[nid].geometry.y},{nodos_muestra.loc[nid].geometry.x}" for nid in lote)
    for intento in range(5):
        resp = requests.get(URL, params={"locations": locs_str}, timeout=30)
        if resp.status_code == 429:
            espera = 5 * (intento + 1)
            print(f"  lote {i // 100 + 1}: 429 Too Many Requests, esperando {espera}s...")
            time.sleep(espera)
            continue
        resp.raise_for_status()
        break
    else:
        raise SystemExit("Open Topo Data siguió devolviendo 429 tras varios reintentos.")
    for nid, r in zip(lote, resp.json()["results"]):
        elevaciones[nid] = r["elevation"]
    print(f"  lote {i // 100 + 1}: {len(lote)} puntos OK")
    time.sleep(1.2)  # respetar el limite publico de ~1 request/seg

resultados = []
for _, arista in muestra.iterrows():
    u, v = arista["u"], arista["v"]
    if u not in elevaciones or v not in elevaciones:
        continue
    elev_u, elev_v = elevaciones[u], elevaciones[v]
    largo_m = arista.geometry.length * 111_000  # aprox grados -> metros
    desnivel_m = abs(elev_v - elev_u)
    pendiente_pct = (desnivel_m / largo_m * 100) if largo_m > 0 else 0
    resultados.append({
        "u": int(u), "v": int(v),
        "elev_u_m": elev_u, "elev_v_m": elev_v,
        "desnivel_m": round(desnivel_m, 1),
        "largo_aprox_m": round(largo_m, 1),
        "pendiente_pct": round(pendiente_pct, 1),
    })

pendientes = [r["pendiente_pct"] for r in resultados]
pendientes.sort()
n = len(pendientes)
print(f"\n{n} aristas con pendiente calculada")
print(f"Pendiente media: {sum(pendientes)/n:.1f}%")
print(f"Mediana: {pendientes[n//2]:.1f}%")
print(f"P90: {pendientes[int(n*0.9)]:.1f}%")
print(f"Máxima: {max(pendientes):.1f}%")
print(f"Aristas con pendiente > 15% (empinadas): {sum(1 for p in pendientes if p > 15)} ({sum(1 for p in pendientes if p > 15)/n*100:.1f}%)")

with open(f"{EVID}/relieve_muestra_aristas.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
print(f"\nGuardado en {EVID}/relieve_muestra_aristas.json")
