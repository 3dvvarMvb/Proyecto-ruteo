"""Carga viento.json a la tabla metadata_viento."""
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

archivo_json = os.path.join(AQUI, "viento.json")
with open(archivo_json, encoding="utf-8") as f:
    datos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE metadata_viento RESTART IDENTITY;")

for p in datos:
    cur.execute(
        """
        INSERT INTO metadata_viento (comuna, sector, elevacion_m, viento_medio_kmh, racha_media_kmh, racha_max_kmh, direccion_deg, geom)
        VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """,
        (
            p["comuna"], p["sector"], p["elevacion_m"],
            p["viento_medio_kmh"], p["racha_media_kmh"], p["racha_max_kmh"], p["direccion_deg"],
            p["lon"], p["lat"]
        ),
    )

conn.commit()
cur.execute("SELECT count(*) FROM metadata_viento;")
print(f"OK: {cur.fetchone()[0]} registros cargados en metadata_viento")
cur.close()
conn.close()
