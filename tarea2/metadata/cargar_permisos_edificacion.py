"""Carga permisos_edificacion.json a metadata_permisos_edificacion y calcula,
por cada manzana censal de metadata_poblacion, el indice_antiguedad: un proxy
de antiguedad relativa de la edificacion por zona (NO probabilidad de colapso).

Calculo: para cada manzana se cuentan los permisos 2010-2018 que caen dentro
de su poligono (ST_Contains). El indice se normaliza contra el percentil 95
de permisos entre las manzanas que SI tienen al menos un permiso (evita que
un par de manzanas con edificios grandes/complejos nuevos distorsionen la
escala). Manzanas sin ningun permiso reciente quedan con indice = 1.0 (maxima
antiguedad relativa); manzanas en o sobre el percentil 95 quedan con indice
~0.0 (edificacion mayormente renovada).

Requiere que metadata_poblacion ya este cargada (cargar_poblacion.py primero).
"""
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

archivo_json = os.path.join(AQUI, "permisos_edificacion.json")
with open(archivo_json, encoding="utf-8") as f:
    datos = json.load(f)

conn = psycopg2.connect(**CONN)
cur = conn.cursor()
cur.execute("TRUNCATE metadata_permisos_edificacion RESTART IDENTITY;")

valores = [
    (
        d["id"], d["comuna"], d["anio"], d["num_pisos"], d["superficie_m2"],
        f"SRID=4326;POINT({d['lon']} {d['lat']})"
    )
    for d in datos
]

execute_values(
    cur,
    """
    INSERT INTO metadata_permisos_edificacion (id, comuna, anio, num_pisos, superficie_m2, geom)
    VALUES %s
    """,
    valores,
    template="(%s, %s, %s, %s, %s, ST_GeomFromEWKT(%s))",
    page_size=2000,
)
conn.commit()
print(f"OK: {len(valores):,} permisos de edificación cargados en metadata_permisos_edificacion")

# Vincular por zona: contar permisos por manzana y calcular indice_antiguedad
cur.execute("""
    WITH conteo AS (
        SELECT m.id AS manzana_id, count(p.id) AS n_permisos
        FROM metadata_poblacion m
        LEFT JOIN metadata_permisos_edificacion p ON ST_Contains(m.geom, p.geom)
        GROUP BY m.id
    ),
    percentil AS (
        SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY n_permisos) AS p95
        FROM conteo WHERE n_permisos > 0
    )
    UPDATE metadata_poblacion m
    SET permisos_count = c.n_permisos,
        indice_antiguedad = ROUND((1.0 - LEAST(1.0, c.n_permisos::numeric / NULLIF(pct.p95, 0)))::numeric, 3)
    FROM conteo c, percentil pct
    WHERE m.id = c.manzana_id;
""")
conn.commit()

cur.execute("""
    SELECT count(*) FILTER (WHERE permisos_count = 0), count(*),
           round(avg(indice_antiguedad)::numeric, 3), round(max(indice_antiguedad)::numeric, 3)
    FROM metadata_poblacion;
""")
sin_permiso, total, prom, maximo = cur.fetchone()
print(f"OK: indice_antiguedad calculado para {total:,} manzanas "
      f"({sin_permiso:,} sin ningún permiso reciente, promedio={prom}, máximo={maximo})")

cur.close()
conn.close()
