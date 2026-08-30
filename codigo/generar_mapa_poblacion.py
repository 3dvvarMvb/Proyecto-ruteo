"""Metadata 3 - INE (via Observatorio de Ciudades UC, ArcGIS REST publico):
poblacion por manzana censal, Censo 2017. Mapa de densidad para el Gran
Valparaiso, con el mismo fondo geografico usado en los otros mapas."""
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia/datos"
EVID_IMG = "evidencia/imagenes"

manzanas = gpd.read_file(f"{EVID}/ine_manzanas_gran_valparaiso.geojson")
region = gpd.read_file(f"{EVID}/region_valparaiso.geojson")
comunas = gpd.read_file(f"{EVID}/comunas_gran_valparaiso.geojson")

fig, ax = plt.subplots(figsize=(9, 8))
ax.set_facecolor("#cfe3f5")
region.plot(ax=ax, facecolor="#f2ead9", edgecolor="none", zorder=0)
# Escala 0-300: el 95% de las manzanas tiene <=302 hab. (mediana=58), y solo
# el 0,3% supera 1.000; con una escala lineal hasta el máximo (2.754) casi
# todo el mapa se ve del mismo color oscuro. Se recorta en el percentil 95
# y se usa "extend" en la barra de color para señalar los valores por encima.
VMAX = 300
manzanas.plot(column="TOTAL_PERS", cmap="viridis", legend=True, ax=ax,
              vmin=0, vmax=VMAX,
              legend_kwds={"label": "Población por manzana (recortado en 300; el 95% de las manzanas está bajo ese valor)",
                           "shrink": 0.7, "extend": "max"},
              linewidth=0, zorder=1)
comunas.plot(ax=ax, facecolor="none", edgecolor="#333333", linewidth=1.0, zorder=2)
for _, row in comunas.iterrows():
    c = row.geometry.centroid
    ax.annotate(row["name"], (c.x, c.y), fontsize=8, ha="center", color="white",
                zorder=3, path_effects=[__import__("matplotlib.patheffects", fromlist=["withStroke"]).withStroke(linewidth=2, foreground="black")])

ax.set_xlim(-71.75, -71.15); ax.set_ylim(-33.25, -32.7)
ax.set_aspect("equal", adjustable="box")
total_pob = int(manzanas["TOTAL_PERS"].sum())
ax.set_title(f"INE (Censo 2017, vía Observatorio de Ciudades UC) - Población por manzana\nGran Valparaíso: {len(manzanas):,} manzanas, {total_pob:,} habitantes")
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
fig.tight_layout()
fig.savefig(f"{EVID_IMG}/mapa_ine_poblacion_manzanas.png", dpi=150)
print("OK evidencia/imagenes/mapa_ine_poblacion_manzanas.png")
