"""7.2 - Prueba del pipeline PostGIS + pgRouting con datos sinteticos
que replican la operacion descrita en el informe (recorte por poligono
de exclusion, penalizacion por foco de incendio, pgr_KSP)."""
import psycopg2

conn = psycopg2.connect(host="localhost", dbname="ruteo_drones", user="kali", password="kali")
conn.autocommit = True
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS aristas, zonas_excluidas, focos_firms CASCADE;")

# Una mini red vial sintetica: 5 nodos en linea con un bypass, en coordenadas
# reales del area de Valparaiso, para poder graficar sobre el mapa real despues.
cur.execute("""
CREATE TABLE aristas (
    id serial PRIMARY KEY,
    source integer,
    target integer,
    costo double precision,
    operable boolean DEFAULT true,
    geom geometry(LineString, 4326)
);
""")

# 1->2->3->4 (ruta directa) y 1->5->4 (ruta alternativa/bypass)
edges = [
    (1, 2, "LINESTRING(-71.62 -33.04, -71.615 -33.04)"),
    (2, 3, "LINESTRING(-71.615 -33.04, -71.61 -33.04)"),
    (3, 4, "LINESTRING(-71.61 -33.04, -71.605 -33.04)"),
    (1, 5, "LINESTRING(-71.62 -33.04, -71.615 -33.045)"),
    (5, 4, "LINESTRING(-71.615 -33.045, -71.605 -33.04)"),
]
for s, t, wkt in edges:
    cur.execute(
        "INSERT INTO aristas (source, target, costo, geom) "
        "VALUES (%s, %s, ST_Length(ST_GeomFromText(%s, 4326)::geography), ST_GeomFromText(%s, 4326))",
        (s, t, wkt, wkt),
    )

cur.execute("""
CREATE TABLE zonas_excluidas (
    id serial PRIMARY KEY,
    nombre text,
    geom geometry(Polygon, 4326)
);
""")
# Poligono de exclusion DGAC que corta la arista 2->3 de la ruta directa
cur.execute("""
INSERT INTO zonas_excluidas (nombre, geom) VALUES (
    'Zona restringida DGAC (demo)',
    ST_GeomFromText('POLYGON((-71.617 -33.041, -71.608 -33.041, -71.608 -33.039, -71.617 -33.039, -71.617 -33.041))', 4326)
);
""")

cur.execute("""
CREATE TABLE focos_firms (
    id serial PRIMARY KEY,
    geom geometry(Point, 4326)
);
""")
cur.execute("INSERT INTO focos_firms (geom) VALUES (ST_GeomFromText('POINT(-71.6175 -33.0445)', 4326));")

print("--- Estado inicial de aristas ---")
cur.execute("SELECT id, source, target, round(costo::numeric,1), operable FROM aristas ORDER BY id;")
for row in cur.fetchall():
    print(row)

# Operacion clave 1: exclusion permanente por poligono DGAC (§7.2 del informe)
cur.execute("""
UPDATE aristas a
SET operable = FALSE, costo = 1e9
FROM zonas_excluidas z
WHERE ST_Intersects(a.geom, z.geom);
""")
print(f"\nAristas cortadas por poligono de exclusion: {cur.rowcount}")

# Operacion clave 2: penalizacion dinamica por foco de incendio (buffer 500 m)
cur.execute("""
UPDATE aristas a
SET costo = costo * 1000
FROM focos_firms f
WHERE ST_DWithin(a.geom::geography, f.geom::geography, 500)
  AND a.operable;
""")
print(f"Aristas penalizadas por cercania a foco de incendio: {cur.rowcount}")

print("\n--- Estado final de aristas ---")
cur.execute("SELECT id, source, target, round(costo::numeric,1), operable FROM aristas ORDER BY id;")
for row in cur.fetchall():
    print(row)

# Operacion de ruteo resiliente: k rutas alternativas con pgr_KSP (algoritmo de Yen)
print("\n--- pgr_KSP: k=2 rutas alternativas de nodo 1 a nodo 4 ---")
cur.execute("""
SELECT seq, path_id, node, edge, round(cost::numeric,1), round(agg_cost::numeric,1)
FROM pgr_KSP(
    'SELECT id, source, target, costo AS cost FROM aristas WHERE operable',
    1, 4, 2, directed := false
);
""")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
print("\nOK: pipeline PostGIS + pgRouting funcional de extremo a extremo.")
