"""Punto 8 de la rubrica - genera una ruta de ejemplo con pgr_dijkstra usando
length_m (distancia) como costo. Es el "peor caso": NO considera metadata ni
amenazas (eso es Fase 3), solo la ruta mas corta en distancia.

Origen: una comisaria de Carabineros (nodo de origen del dron).
Destino: el nodo vial mas cercano al epicentro de un sismo real (amenaza de
ejemplo), para representar "ir a evaluar danos tras el sismo"."""
import json
import os
import psycopg2

AQUI = os.path.dirname(os.path.abspath(__file__))
CONN = dict(
    host=os.environ.get("DB_HOST", "localhost"),
    port=os.environ.get("DB_PORT", "5432"),
    dbname=os.environ.get("DB_NAME", "ruteo_drones"),
    user=os.environ.get("DB_USER", "ruteo"),
    password=os.environ.get("DB_PASSWORD", "ruteo"),
)

ORIGEN_NOMBRE = "8VA. COM. FLORIDA VALPO."  # comisaria de Valparaiso
# M4.6, 5km N de Viña del Mar, a 479m de la red vial mas cercana. Se eligio
# este sismo (y no uno mas lejano) porque esta a menos de 2000m del nodo vial
# mas cercano: un dron BVLOS evalua danos siguiendo calles, no sobrevolando
# el oceano, asi que si el epicentro esta muy lejos de la red, "llegar" ahi
# es solo un punto arbitrario de la costa, no el area real de impacto. Ver
# UMBRAL_DISTANCIA_RED_M en sitio_web/servidor.py y generar_rutas_comparativas.py.
SISMO_ID = "us7000ltwn"

conn = psycopg2.connect(**CONN)
cur = conn.cursor()

cur.execute("SELECT nombre, comuna, nodo_vial_id, ST_X(geom), ST_Y(geom) FROM nodo_carabineros WHERE nombre = %s", (ORIGEN_NOMBRE,))
row_orig = cur.fetchone()
if not row_orig:
    cur.execute("SELECT nombre, comuna, nodo_vial_id, ST_X(geom), ST_Y(geom) FROM nodo_carabineros WHERE es_comisaria = true LIMIT 1")
    row_orig = cur.fetchone()
origen_nombre, origen_comuna, origen_nodo, origen_lon, origen_lat = row_orig

cur.execute("SELECT lugar, magnitud, ST_X(geom), ST_Y(geom) FROM amenaza_sismos WHERE usgs_id = %s", (SISMO_ID,))
row_sismo = cur.fetchone()
if not row_sismo:
    cur.execute("SELECT lugar, magnitud, ST_X(geom), ST_Y(geom) FROM amenaza_sismos ORDER BY magnitud DESC LIMIT 1")
    row_sismo = cur.fetchone()
sismo_lugar, sismo_mag, sismo_lon, sismo_lat = row_sismo

cur.execute(
    """
    SELECT id FROM infraestructura_nodos
    ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
    LIMIT 1
    """,
    (sismo_lon, sismo_lat),
)
destino_nodo = cur.fetchone()[0]

print(f"Origen: {origen_nombre} ({origen_comuna}) -> nodo vial {origen_nodo}")
print(f"Destino: epicentro M{sismo_mag} {sismo_lugar} -> nodo vial más cercano {destino_nodo}")

cur.execute(
    """
    SELECT seq, node, edge, cost, agg_cost
    FROM pgr_dijkstra(
        'SELECT id, source, target, length_m AS cost FROM infraestructura_aristas',
        %s, %s
    )
    """,
    (origen_nodo, destino_nodo),
)
filas = cur.fetchall()
edge_ids = [r[2] for r in filas if r[2] != -1]
distancia_total_m = filas[-1][4]

print(f"Ruta encontrada: {len(edge_ids)} tramos, {distancia_total_m:.0f} m totales")

cur.execute(
    "SELECT id, ST_AsGeoJSON(geom) FROM infraestructura_aristas WHERE id = ANY(%s)",
    (edge_ids,),
)
geoms_por_id = {row[0]: json.loads(row[1]) for row in cur.fetchall()}

features = []
for eid in edge_ids:
    features.append({
        "type": "Feature",
        "geometry": geoms_por_id[eid],
        "properties": {"arista_id": eid},
    })

geojson = {
    "type": "FeatureCollection",
    "metadata": {
        "origen": {"nombre": origen_nombre, "comuna": origen_comuna, "lon": origen_lon, "lat": origen_lat},
        "destino": {"descripcion": f"Epicentro M{sismo_mag} - {sismo_lugar}", "lon": sismo_lon, "lat": sismo_lat},
        "distancia_total_m": round(distancia_total_m, 1),
        "num_tramos": len(edge_ids),
        "costo_usado": "length_m (distancia, sin metadata ni amenazas - Fase 2)",
        "algoritmo": "pgr_dijkstra",
    },
    "features": features,
}

with open(f"{AQUI}/ruta_ejemplo.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False)
print(f"Guardado en {AQUI}/ruta_ejemplo.geojson")

cur.close()
conn.close()
