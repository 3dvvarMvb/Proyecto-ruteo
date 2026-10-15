"""Mapa de cuarteles de Carabineros (posibles nodos de origen/carga del dron)
sobre el mismo fondo geográfico usado en los otros mapas del Gran Valparaíso."""
import json
import geopandas as gpd
from shapely.geometry import shape
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia/datos"
EVID_IMG = "evidencia/imagenes"

with open(f"{EVID}/carabineros_cuarteles_gran_valparaiso.geojson", encoding="utf-8") as f:
    data = json.load(f)

cuarteles = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
cuarteles["es_comisaria"] = cuarteles["nombre"].str.contains("COM.", regex=False) & ~cuarteles["nombre"].str.contains("SUBCOM", regex=False)

region = gpd.read_file(f"{EVID}/region_valparaiso.geojson")
comunas = gpd.read_file(f"{EVID}/comunas_gran_valparaiso.geojson")

fig, ax = plt.subplots(figsize=(9, 8))
ax.set_facecolor("#cfe3f5")
region.plot(ax=ax, facecolor="#f2ead9", edgecolor="none", zorder=0)
comunas.plot(ax=ax, facecolor="none", edgecolor="#333333", linewidth=1.0, zorder=1)

otros = cuarteles[~cuarteles["es_comisaria"]]
comisarias = cuarteles[cuarteles["es_comisaria"]]

ax.scatter(otros.geometry.x, otros.geometry.y, c="#7f8c8d", s=35, marker="o",
           edgecolor="black", linewidth=0.4, zorder=2, label=f"Tenencias / retenes / subcomisarías ({len(otros)})")
ax.scatter(comisarias.geometry.x, comisarias.geometry.y, c="#c0392b", s=90, marker="^",
           edgecolor="black", linewidth=0.6, zorder=3, label=f"Comisarías ({len(comisarias)})")

for _, row in comunas.iterrows():
    c = row.geometry.centroid
    ax.annotate(row["name"], (c.x, c.y), fontsize=8, ha="center", color="white",
                zorder=4, path_effects=[__import__("matplotlib.patheffects", fromlist=["withStroke"]).withStroke(linewidth=2, foreground="black")])

ax.set_xlim(-71.75, -71.15); ax.set_ylim(-33.25, -32.7)
ax.set_aspect("equal", adjustable="box")
ax.set_title(f"Cuarteles de Carabineros — posibles nodos de origen/carga del dron\nGran Valparaíso: {len(cuarteles)} cuarteles ({len(comisarias)} comisarías)")
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
ax.legend(loc="lower right", fontsize=9)
fig.tight_layout()
fig.savefig(f"{EVID_IMG}/mapa_carabineros_cuarteles.png", dpi=150)
print("OK evidencia/imagenes/mapa_carabineros_cuarteles.png")
