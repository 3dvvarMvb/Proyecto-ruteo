"""Exporta las capas ya cargadas en la BD a GeoJSON para que Leaflet las
consuma directo como archivos estaticos (sitio_web/data/*.geojson)."""
import json
import os
import psycopg2

AQUI = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = f"{AQUI}/data"
os.makedirs(DATA_DIR, exist_ok=True)

CONN = dict(
    host=os.environ.get("DB_HOST", "localhost"),
    port=os.environ.get("DB_PORT", "5432"),
    dbname=os.environ.get("DB_NAME", "ruteo_drones"),
    user=os.environ.get("DB_USER", "ruteo"),
    password=os.environ.get("DB_PASSWORD", "ruteo"),
)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()


def exportar(nombre, sql):
    cur.execute(sql)
    row = cur.fetchone()
    geojson = row[0]
    with open(f"{DATA_DIR}/{nombre}.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)
    n = len(geojson.get("features", []))
    print(f"  {nombre}.geojson: {n} features")


print("Exportando capas a sitio_web/data/ ...")

exportar("carabineros", """
    SELECT json_build_object(
        'type', 'FeatureCollection',
        'features', COALESCE(json_agg(json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(geom)::json,
            'properties', json_build_object(
                'nombre', nombre, 'comuna', comuna,
                'es_comisaria', es_comisaria, 'es_punto_carga', es_punto_carga
            )
        )), '[]'::json)
    ) FROM nodo_carabineros;
""")

exportar("sismos", """
    SELECT json_build_object(
        'type', 'FeatureCollection',
        'features', COALESCE(json_agg(json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(geom)::json,
            'properties', json_build_object(
                'magnitud', magnitud, 'profundidad_km', profundidad_km,
                'fecha', fecha, 'lugar', lugar
            )
        )), '[]'::json)
    ) FROM amenaza_sismos;
""")

conn.commit()
cur.close()
conn.close()
print("OK")
