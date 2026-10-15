"""Carga sismos.json a la tabla amenaza_sismos."""
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

with open(f"{AQUI}/sismos.json", encoding="utf-8") as f:
    sismos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE amenaza_sismos RESTART IDENTITY;")

for s in sismos:
    cur.execute(
        """
        INSERT INTO amenaza_sismos (usgs_id, magnitud, profundidad_km, fecha, lugar, geom)
        VALUES (%s, %s, %s, to_timestamp(%s / 1000.0), %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        ON CONFLICT (usgs_id) DO NOTHING
        """,
        (s["usgs_id"], s["magnitud"], s["profundidad_km"], s["fecha"], s["lugar"], s["lon"], s["lat"]),
    )

conn.commit()
cur.execute("SELECT count(*) FROM amenaza_sismos;")
print(f"OK: {cur.fetchone()[0]} sismos cargados en amenaza_sismos")
cur.close()
conn.close()
