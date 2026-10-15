"""Carga conaf_ignicion.json y conaf_areas_protegidas.json a PostgreSQL."""
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

conn = psycopg2.connect(**CONN)
cur = conn.cursor()

# 1. Ignición
path_pi = os.path.join(AQUI, "conaf_ignicion.json")
if os.path.exists(path_pi):
    with open(path_pi, encoding="utf-8") as f:
        datos_pi = json.load(f)
    cur.execute("TRUNCATE amenaza_conaf_ignicion RESTART IDENTITY;")
    val_pi = [
        (d["label"], d["rango_pi"], d["dia_pronostico"], f"SRID=4326;{d['geom_wkt']}")
        for d in datos_pi
    ]
    execute_values(
        cur,
        "INSERT INTO amenaza_conaf_ignicion (label, rango_pi, dia_pronostico, geom) VALUES %s",
        val_pi,
        template="(%s, %s, %s, ST_Multi(ST_MakeValid(ST_GeomFromEWKT(%s))))",
        page_size=1000,
    )
    cur.execute("SELECT count(*) FROM amenaza_conaf_ignicion;")
    print(f"OK: {cur.fetchone()[0]} registros cargados en amenaza_conaf_ignicion")

# 2. Áreas Protegidas
path_asp = os.path.join(AQUI, "conaf_areas_protegidas.json")
if os.path.exists(path_asp):
    with open(path_asp, encoding="utf-8") as f:
        datos_asp = json.load(f)
    cur.execute("TRUNCATE amenaza_conaf_areas_protegidas RESTART IDENTITY;")
    val_asp = [
        (d["nombre"], d["categoria"], d["sup_ha"], f"SRID=4326;{d['geom_wkt']}")
        for d in datos_asp
    ]
    execute_values(
        cur,
        "INSERT INTO amenaza_conaf_areas_protegidas (nombre, categoria, sup_ha, geom) VALUES %s",
        val_asp,
        template="(%s, %s, %s, ST_Multi(ST_MakeValid(ST_GeomFromEWKT(%s))))",
        page_size=1000,
    )
    cur.execute("SELECT count(*) FROM amenaza_conaf_areas_protegidas;")
    print(f"OK: {cur.fetchone()[0]} registros cargados en amenaza_conaf_areas_protegidas")

conn.commit()
cur.close()
conn.close()
