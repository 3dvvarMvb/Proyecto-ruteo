"""Carga firms.json a la tabla amenaza_firms."""
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

archivo_json = os.path.join(AQUI, "firms.json")
with open(archivo_json, encoding="utf-8") as f:
    datos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE amenaza_firms RESTART IDENTITY;")

valores = [
    (d["fecha"], d["confianza"], d["dentro_chile"], f"SRID=4326;POINT({d['lon']} {d['lat']})")
    for d in datos
]

execute_values(
    cur,
    "INSERT INTO amenaza_firms (fecha, confianza, dentro_chile, geom) VALUES %s",
    valores,
    template="(%s, %s, %s, ST_GeomFromEWKT(%s))",
    page_size=2000,
)

conn.commit()
cur.execute("SELECT count(*), count(*) FILTER (WHERE dentro_chile) FROM amenaza_firms;")
total, en_chile = cur.fetchone()
print(f"OK: {total} focos cargados en amenaza_firms ({en_chile} dentro de Chile)")
cur.close()
conn.close()
