"""Genera evidencia visual (PNG) a partir de las respuestas ya guardadas,
para cumplir el criterio de la rubrica que pide capturas, no solo JSON."""
import json
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia"

# Fondo geografico comun (tierra/mar + comunas) para dar contexto real a los
# mapas de poligonos; sin esto, los poligonos aislados "flotan" sin
# referencia y es dificil juzgar si estan bien ubicados.
region = gpd.read_file(f"{EVID}/region_valparaiso.geojson")
comunas = gpd.read_file(f"{EVID}/comunas_gran_valparaiso.geojson")


def dibujar_fondo(ax):
    ax.set_facecolor("#cfe3f5")  # mar
    region.plot(ax=ax, facecolor="#f2ead9", edgecolor="#8a8a8a", linewidth=0.6, zorder=0)
    comunas.plot(ax=ax, facecolor="none", edgecolor="#4a4a4a", linewidth=0.7, zorder=1)
    for _, row in comunas.iterrows():
        c = row.geometry.centroid
        ax.annotate(row["name"], (c.x, c.y), fontsize=7, ha="center", color="#333333", zorder=1)


# ------------------------------------------------------------------
# 1) CONAF - probabilidad de ignicion (poligonos coloreados por riesgo)
# ------------------------------------------------------------------
from shapely.geometry import box

BBOX_VALPO = box(-72.0, -33.5, -71.2, -32.7)

# El campo "label" es el limite superior de un decil (1-10, 11-20, ..., 91-100)
# de un indice de Probabilidad de Ignicion (var="PI" en el servicio), NO un
# porcentaje directo. Mapeo tomado del renderer oficial del FeatureServer.
RANGOS_PI = {v: f"{v-9}-{v}" for v in range(10, 101, 10)}

gdf_pi = gpd.read_file(f"{EVID}/conaf_probabilidad_ignicion.geojson")
gdf_pi["geometry"] = gdf_pi.geometry.buffer(0)  # repara geometrias invalidas
gdf_pi["rango_PI"] = gdf_pi["label"].map(RANGOS_PI)
# Los poligonos son nacionales (categorias de riesgo a nivel pais); se
# recortan al bbox de la Region de Valparaiso para visualizar el detalle real
# (equivalente a ST_Intersection en el pipeline PostGIS de la Tarea 2)
gdf_pi_clip = gpd.clip(gdf_pi, BBOX_VALPO)

# Los poligonos de este servicio se superponen entre si (verificado: el
# poligono de riesgo 30 queda 100% contenido dentro del poligono 20). Sin
# ordenar, matplotlib dibuja por orden de fila y el ultimo pintado tapa a
# los demas, escondiendo silenciosamente la zona de mayor riesgo. Se dibuja
# primero el poligono mas grande (fondo) y al final el mas chico (detalle),
# para que el riesgo mas alto y mas especifico quede siempre visible arriba.
gdf_pi_clip = gdf_pi_clip.assign(_area=gdf_pi_clip.geometry.area).sort_values("_area", ascending=False)

fig, ax = plt.subplots(figsize=(8, 6.5))
dibujar_fondo(ax)
gdf_pi_clip.plot(column="rango_PI", categorical=True, legend=True, ax=ax, cmap="YlOrRd", edgecolor="black", linewidth=0.3, alpha=0.75, zorder=2)
ax.get_legend().set_title("Índice PI (0-100)")
ax.set_xlim(-72.0, -71.2); ax.set_ylim(-33.5, -32.7)
ax.set_aspect("equal", adjustable="box")
ax.set_title("CONAF - Probabilidad de ignición (PI) a 5 días — 2026-08-30\n(Región de Valparaíso, índice 0-100 por decil, dato real vía ArcGIS REST)")
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
fig.tight_layout()
fig.savefig(f"{EVID}/mapa_conaf_probabilidad_ignicion.png", dpi=150)
print("OK mapa_conaf_probabilidad_ignicion.png")

# ------------------------------------------------------------------
# 2) CONAF - areas silvestres protegidas
# ------------------------------------------------------------------
gdf_asp = gpd.read_file(f"{EVID}/conaf_areas_protegidas.geojson")
fig, ax = plt.subplots(figsize=(8, 7))
dibujar_fondo(ax)
gdf_asp.plot(column="categoria", categorical=True, legend=True, ax=ax, cmap="Greens", edgecolor="black", linewidth=0.4, zorder=2)
ax.set_xlim(-71.75, -71.25); ax.set_ylim(-33.5, -32.75)
ax.set_aspect("equal", adjustable="box")
ax.set_title(f"CONAF - Áreas Silvestres Protegidas en Valparaíso\n({len(gdf_asp)} polígonos reales vía ArcGIS REST)")
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
fig.tight_layout()
fig.savefig(f"{EVID}/mapa_conaf_areas_protegidas.png", dpi=150)
print("OK mapa_conaf_areas_protegidas.png")

# ------------------------------------------------------------------
# 3) Open-Meteo - viento y rachas (serie de tiempo)
# ------------------------------------------------------------------
with open(f"{EVID}/open_meteo_response.json", encoding="utf-8") as f:
    om = json.load(f)
horas = om["hourly"]["time"][:48]
viento = om["hourly"]["wind_speed_10m"][:48]
rachas = om["hourly"]["wind_gusts_10m"][:48]
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(range(len(horas)), viento, label="Viento 10m (km/h)")
ax.plot(range(len(horas)), rachas, label="Rachas 10m (km/h)")
ax.axhline(40, color="red", linestyle="--", linewidth=1, label="Ej. límite operacional dron (40 km/h)")
ax.set_title(f"Open-Meteo - Pronóstico de viento, Valparaíso\n(lat={om['latitude']}, lon={om['longitude']}, primeras 48 h)")
ax.set_xlabel("Hora (índice)"); ax.set_ylabel("km/h"); ax.legend()
fig.tight_layout()
fig.savefig(f"{EVID}/grafico_open_meteo_viento.png", dpi=150)
print("OK grafico_open_meteo_viento.png")

# ------------------------------------------------------------------
# 4) USGS - sismicidad: generado por generar_mapa_sismicidad.py (con fondo
#    de tierra/mar + comunas); no se repite aqui para no sobrescribirlo.
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# 5) Overpass - resumen tabular de edificacion (como tabla renderizada)
# ------------------------------------------------------------------
with open(f"{EVID}/overpass_response.json", encoding="utf-8") as f:
    ov = json.load(f)
rows = []
for el in ov.get("elements", []):
    tags = el.get("tags", {})
    rows.append([el["id"], tags.get("building:levels", "-"), tags.get("height", "-"), tags.get("building", "-")])
fig, ax = plt.subplots(figsize=(8, 0.4 * len(rows) + 1))
ax.axis("off")
tbl = ax.table(cellText=rows, colLabels=["way id", "building:levels", "height", "building"], loc="center")
tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1, 1.5)
ax.set_title(f"Overpass API - edificación en Valparaíso ({len(rows)} elementos reales)")
fig.tight_layout()
fig.savefig(f"{EVID}/tabla_overpass_edificacion.png", dpi=150)
print("OK tabla_overpass_edificacion.png")

print("\nListo. Todas las imagenes quedaron en", EVID)
