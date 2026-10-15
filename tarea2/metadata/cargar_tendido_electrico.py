"""Carga tendido_electrico.json a la tabla metadata_tendido_electrico."""
import json
import os
import psycopg2
from psycopg2.extras import execute_values

AQUI = os.path.dirname(os.path.abspath(__file__))
CONN = dict(
    host=os.environ.get("DB_HOST", "localhost"),
    port=os.environ.get("DB_PORT", "5432"),
    dbname=os.environ.get("DB_NAME", "ruteo_drones"),
    user=os.environ.get("DB_USER", "ruteo"),
    password=os.environ.get("DB_PASSWORD", "ruteo"),
)

archivo_json = os.path.join(AQUI, "tendido_electrico.json")
with open(archivo_json, encoding="utf-8") as f:
    datos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE metadata_tendido_electrico RESTART IDENTITY;")

valores = [
    (d["id"], d["tipo"], f"SRID=4326;{d['geom_wkt']}")
    for d in datos
]

execute_values(
    cur,
    "INSERT INTO metadata_tendido_electrico (id, tipo, geom) VALUES %s",
    valores,
    template="(%s, %s, ST_GeomFromEWKT(%s))",
    page_size=2000,
)

conn.commit()
cur.execute("SELECT count(*) FROM metadata_tendido_electrico;")
print(f"OK: {cur.fetchone()[0]} líneas cargadas en metadata_tendido_electrico")
cur.close()
conn.close()
