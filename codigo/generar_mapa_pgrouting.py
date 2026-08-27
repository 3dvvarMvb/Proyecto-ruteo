"""Visualiza el resultado de test_postgis_pgrouting.py: aristas excluidas
por poligono DGAC (rojo), ruta alternativa que sobrevive via pgr_KSP (verde),
poligono de exclusion y foco de incendio."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import psycopg2
from shapely import wkb
from shapely.geometry import Polygon

conn = psycopg2.connect(host="localhost", dbname="ruteo_drones", user="kali", password="kali")
cur = conn.cursor()

fig, ax = plt.subplots(figsize=(8, 7))

cur.execute("SELECT id, operable, ST_AsBinary(geom) FROM aristas ORDER BY id;")
for id_, operable, geom_bin in cur.fetchall():
    line = wkb.loads(bytes(geom_bin))
    xs, ys = line.xy
    color = "green" if operable else "red"
    label = None
    ax.plot(xs, ys, color=color, linewidth=3, solid_capstyle="round", zorder=2)
    ax.annotate(f"#{id_}", (sum(xs)/2, sum(ys)/2), fontsize=8, color=color)

cur.execute("SELECT ST_AsBinary(geom) FROM zonas_excluidas;")
for (geom_bin,) in cur.fetchall():
    poly = wkb.loads(bytes(geom_bin))
    xs, ys = poly.exterior.xy
    ax.fill(xs, ys, color="red", alpha=0.15, zorder=1, label="Polígono de exclusión DGAC")

cur.execute("SELECT ST_AsBinary(geom) FROM focos_firms;")
for (geom_bin,) in cur.fetchall():
    pt = wkb.loads(bytes(geom_bin))
    ax.scatter([pt.x], [pt.y], color="orange", marker="^", s=150, zorder=3, label="Foco de incendio (FIRMS)")

ax.plot([], [], color="green", linewidth=3, label="Arista operable (ruta pgr_KSP)")
ax.plot([], [], color="red", linewidth=3, label="Arista cortada (ST_Intersects con polígono)")
ax.legend(loc="lower right", fontsize=8)
ax.set_title("PostGIS + pgRouting - prueba de extremo a extremo\nRuta directa (1→2→3→4) cortada; bypass (1→5→4) sobrevive vía pgr_KSP")
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
fig.tight_layout()
fig.savefig("evidencia/imagenes/mapa_postgis_pgrouting.png", dpi=150)
print("OK evidencia/imagenes/mapa_postgis_pgrouting.png")

cur.close(); conn.close()
