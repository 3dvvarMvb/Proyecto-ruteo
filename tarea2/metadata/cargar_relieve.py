"""Carga relieve.json a la tabla metadata_relieve."""
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

archivo_json = os.path.join(AQUI, "relieve.json")
with open(archivo_json, encoding="utf-8") as f:
    datos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE metadata_relieve RESTART IDENTITY;")

# Obtener mapeo rápido de (source, target) -> arista_id
cur.execute("SELECT id, source, target FROM infraestructura_aristas;")
filas = cur.fetchall()
mapa_aristas = {(r[1], r[2]): r[0] for r in filas}

cargados = 0
for d in datos:
    arista_id = mapa_aristas.get((d["source"], d["target"]))
    cur.execute(
        """
        INSERT INTO metadata_relieve (arista_id, elev_u_m, elev_v_m, desnivel_m, pendiente_pct)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (arista_id, d["elev_u_m"], d["elev_v_m"], d["desnivel_m"], d["pendiente_pct"]),
    )
    cargados += 1

conn.commit()
cur.execute("SELECT count(*), count(arista_id) FROM metadata_relieve;")
total, con_arista = cur.fetchone()
print(f"OK: {total} registros cargados en metadata_relieve ({con_arista} vinculados a aristas de red)")
cur.close()
conn.close()
