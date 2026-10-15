"""Punto 6 de la rubrica - Carga nodos.json y aristas.json a PostGIS/pgRouting."""
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

with open(f"{AQUI}/nodos.json", encoding="utf-8") as f:
    nodos = json.load(f)
with open(f"{AQUI}/aristas.json", encoding="utf-8") as f:
    aristas = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()

cur.execute("TRUNCATE infraestructura_aristas, infraestructura_nodos, nodo_carabineros, metadata_relieve RESTART IDENTITY CASCADE;")

print(f"Cargando {len(nodos):,} nodos...")
execute_values(
    cur,
    "INSERT INTO infraestructura_nodos (id, osmid, lon, lat, geom) VALUES %s",
    [(n["id"], n["osmid"], n["lon"], n["lat"], f"SRID=4326;POINT({n['lon']} {n['lat']})") for n in nodos],
    template="(%s,%s,%s,%s,ST_GeomFromEWKT(%s))",
    page_size=5000,
)

print(f"Cargando {len(aristas):,} aristas...")
execute_values(
    cur,
    "INSERT INTO infraestructura_aristas (id, osmid, source, target, highway, surface, oneway, length_m, geom) VALUES %s",
    [(a["id"], a["osmid"], a["source"], a["target"], a["highway"], a["surface"], a["oneway"], a["length_m"],
      f"SRID=4326;{a['geom_wkt']}") for a in aristas],
    template="(%s,%s,%s,%s,%s,%s,%s,%s,ST_GeomFromEWKT(%s))",
    page_size=5000,
)

conn.commit()
cur.execute("SELECT count(*) FROM infraestructura_nodos")
print("Nodos en BD:", cur.fetchone()[0])
cur.execute("SELECT count(*) FROM infraestructura_aristas")
print("Aristas en BD:", cur.fetchone()[0])

cur.close()
conn.close()
print("OK")
