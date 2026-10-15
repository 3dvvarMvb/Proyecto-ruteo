"""Carga carabineros.json a la tabla nodo_carabineros, y calcula el nodo del
grafo vial mas cercano a cada cuartel (necesario para poder usarlo como
origen/destino real de pgr_dijkstra)."""
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

with open(f"{AQUI}/carabineros.json", encoding="utf-8") as f:
    cuarteles = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("DELETE FROM nodo_carabineros;")

for c in cuarteles:
    cur.execute(
        """
        INSERT INTO nodo_carabineros (nombre, comuna, es_comisaria, es_punto_carga, geom)
        VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        RETURNING id
        """,
        (c["nombre"], c["comuna"], c["es_comisaria"], c["es_punto_carga"], c["lon"], c["lat"]),
    )
    nuevo_id = cur.fetchone()[0]
    # nodo vial mas cercano (KNN con el operador <->, usa el indice espacial)
    cur.execute(
        """
        UPDATE nodo_carabineros SET nodo_vial_id = (
            SELECT n.id FROM infraestructura_nodos n
            ORDER BY n.geom <-> (SELECT geom FROM nodo_carabineros WHERE id = %s)
            LIMIT 1
        ) WHERE id = %s
        """,
        (nuevo_id, nuevo_id),
    )

conn.commit()
cur.execute("SELECT count(*), count(*) FILTER (WHERE es_comisaria) FROM nodo_carabineros;")
total, comisarias = cur.fetchone()
print(f"OK: {total} cuarteles cargados ({comisarias} comisarías), cada uno vinculado a su nodo vial más cercano")
cur.close()
conn.close()
