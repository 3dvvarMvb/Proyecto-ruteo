"""Carga poblacion.json a la tabla metadata_poblacion."""
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

archivo_json = os.path.join(AQUI, "poblacion.json")
with open(archivo_json, encoding="utf-8") as f:
    datos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE metadata_poblacion RESTART IDENTITY;")

valores = [
    (
        d["id"], d["comuna"], d["manzent"], d["total_pers"], d["total_vivi"],
        f"SRID=4326;{d['geom_wkt']}"
    )
    for d in datos
]

execute_values(
    cur,
    """
    INSERT INTO metadata_poblacion (id, comuna, manzent, total_pers, total_vivi, geom)
    VALUES %s
    """,
    valores,
    template="(%s, %s, %s, %s, %s, ST_Multi(ST_GeomFromEWKT(%s)))",
    page_size=2000,
)

conn.commit()
cur.execute("SELECT count(*), sum(total_pers) FROM metadata_poblacion;")
total, personas = cur.fetchone()
print(f"OK: {total:,} manzanas cargadas en metadata_poblacion ({personas:,} personas cubiertas)")
cur.close()
conn.close()
