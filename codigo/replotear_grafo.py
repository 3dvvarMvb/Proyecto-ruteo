"""Regraba el mapa del grafo vial desde los .gpkg ya generados (rapido,
sin reconstruir el grafo completo desde el XML de nuevo)."""
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

nodos = gpd.read_file("evidencia/nodos_valparaiso.gpkg")
aristas = gpd.read_file("evidencia/aristas_valparaiso.gpkg")
region = gpd.read_file("evidencia/region_valparaiso.geojson")
comunas = gpd.read_file("evidencia/comunas_gran_valparaiso.geojson")

fig, ax = plt.subplots(figsize=(9, 11))
ax.set_facecolor("#cfe3f5")
region.plot(ax=ax, facecolor="#f2ead9", edgecolor="none", zorder=0)
aristas.plot(ax=ax, color="#c0392b", linewidth=0.25, alpha=0.8, zorder=1)
comunas.plot(ax=ax, facecolor="none", edgecolor="#333333", linewidth=1.0, zorder=2)
for _, row in comunas.iterrows():
    c = row.geometry.centroid
    ax.annotate(row["name"], (c.x, c.y), fontsize=8, ha="center", color="black",
                zorder=3, path_effects=[__import__("matplotlib.patheffects", fromlist=["withStroke"]).withStroke(linewidth=2, foreground="white")])
ax.set_xlim(-71.75, -71.15); ax.set_ylim(-33.25, -32.7)
ax.set_aspect("equal", adjustable="box")
ax.set_title(f"Grafo vial real - Gran Valparaíso (OSM vía Geofabrik, sin Overpass)\n{len(nodos):,} nodos, {len(aristas):,} aristas", fontsize=12)
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
fig.tight_layout()
fig.savefig("evidencia/mapa_grafo_valparaiso.png", dpi=150)
print("OK evidencia/mapa_grafo_valparaiso.png")
