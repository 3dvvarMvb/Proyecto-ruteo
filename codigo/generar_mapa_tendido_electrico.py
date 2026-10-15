"""Mapa de tendido electrico aereo (Metadata #2) sobre el mismo fondo
geografico usado en los otros mapas del Gran Valparaiso."""
import json
import geopandas as gpd
from shapely.geometry import LineString, box
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia/datos"
EVID_IMG = "evidencia/imagenes"

with open(f"{EVID}/osm_tendido_electrico.json", encoding="utf-8") as f:
    data = json.load(f)

area = box(-71.75, -33.25, -71.15, -32.7)
registros = []
for w in data["elements"]:
    geom = w.get("geometry", [])
    coords = [(p["lon"], p["lat"]) for p in geom]
    if len(coords) < 2:
        continue
    recortada = LineString(coords).intersection(area)
    if recortada.is_empty:
        continue
    tipo = w.get("tags", {}).get("power", "desconocido")
    if recortada.geom_type == "LineString":
        registros.append({"tipo": tipo, "geometry": recortada})
    elif recortada.geom_type == "MultiLineString":
        for parte in recortada.geoms:
            registros.append({"tipo": tipo, "geometry": parte})

tendido = gpd.GeoDataFrame(registros, crs="EPSG:4326")

region = gpd.read_file(f"{EVID}/region_valparaiso.geojson")
comunas = gpd.read_file(f"{EVID}/comunas_gran_valparaiso.geojson")

fig, ax = plt.subplots(figsize=(9, 8))
ax.set_facecolor("#cfe3f5")
region.plot(ax=ax, facecolor="#f2ead9", edgecolor="none", zorder=0)
comunas.plot(ax=ax, facecolor="none", edgecolor="#333333", linewidth=1.0, zorder=1)

lineas = tendido[tendido["tipo"] == "line"]
menores = tendido[tendido["tipo"] == "minor_line"]
menores.plot(ax=ax, color="#f39c12", linewidth=0.8, zorder=2, label=f"Línea menor / distribución ({len(menores)})")
lineas.plot(ax=ax, color="#c0392b", linewidth=1.2, zorder=3, label=f"Línea de alta/media tensión ({len(lineas)})")

for _, row in comunas.iterrows():
    c = row.geometry.centroid
    ax.annotate(row["name"], (c.x, c.y), fontsize=8, ha="center", color="white",
                zorder=4, path_effects=[__import__("matplotlib.patheffects", fromlist=["withStroke"]).withStroke(linewidth=2, foreground="black")])

ax.set_xlim(-71.75, -71.15); ax.set_ylim(-33.25, -32.7)
ax.set_aspect("equal", adjustable="box")
largo_km = tendido.to_crs(32719).length.sum() / 1000
ax.set_title(f"Tendido eléctrico aéreo (OSM) — riesgo de colisión para el dron\nGran Valparaíso: {len(tendido)} tramos, ~{largo_km:.0f} km dentro del área")
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
ax.legend(loc="lower right", fontsize=9)
fig.tight_layout()
fig.savefig(f"{EVID_IMG}/mapa_tendido_electrico.png", dpi=150)
print("OK evidencia/imagenes/mapa_tendido_electrico.png")
