"""Regenera el mapa de sismicidad USGS con contexto geografico real:
contorno de comunas del Gran Valparaiso (CONAF/ArcGIS REST, mismo
Feature Service ya usado para el reemplazo de SENAPRED)."""
import json
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

EVID = "evidencia/datos"
EVID_IMG = "evidencia/imagenes"
COMUNAS = ["Valparaíso", "Viña del Mar", "Quilpué", "Villa Alemana", "Concón"]

# --- Contorno real de comunas (contexto geografico) ---
where = " OR ".join([f"name = '{c}'" for c in COMUNAS])
url = "https://services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/Comunas/FeatureServer/0/query"
params = {"where": where, "outFields": "name", "returnGeometry": "true", "outSR": 4326, "f": "geojson"}
r = requests.get(url, params=params, timeout=25)
r.raise_for_status()
comunas = gpd.GeoDataFrame.from_features(r.json()["features"], crs="EPSG:4326")
print("Comunas obtenidas:", comunas["name"].tolist())
comunas.to_file(f"{EVID}/comunas_gran_valparaiso.geojson", driver="GeoJSON")

# --- Region de Valparaiso completa (para distinguir tierra firme del mar;
# la mayoria de los sismos de esta zona de subduccion ocurren mar adentro,
# por eso sin la costa como referencia los puntos parecen "flotar" fuera del mapa) ---
url_reg = "https://services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/Regiones/FeatureServer/0/query"
params_reg = {"where": "reg_saff = 'DE VALPARAISO'", "outFields": "reg_saff", "returnGeometry": "true", "outSR": 4326, "f": "geojson"}
r_reg = requests.get(url_reg, params=params_reg, timeout=25)
r_reg.raise_for_status()
region = gpd.GeoDataFrame.from_features(r_reg.json()["features"], crs="EPSG:4326")
print("Region obtenida:", region["reg_saff"].tolist() if len(region) else "VACIA - revisar nombre")
region.to_file(f"{EVID}/region_valparaiso.geojson", driver="GeoJSON")

# --- Sismos USGS ya descargados ---
with open(f"{EVID}/usgs_response.json", encoding="utf-8") as f:
    usgs = json.load(f)
lons = [feat["geometry"]["coordinates"][0] for feat in usgs["features"]]
lats = [feat["geometry"]["coordinates"][1] for feat in usgs["features"]]
mags = [feat["properties"]["mag"] for feat in usgs["features"]]

fig, ax = plt.subplots(figsize=(9, 7.5))
ax.set_facecolor("#cfe3f5")  # mar (Oceano Pacifico)
region.plot(ax=ax, facecolor="#f2ead9", edgecolor="#8a8a8a", linewidth=0.6, zorder=1)  # tierra firme
comunas.plot(ax=ax, facecolor="#dfe7f5", edgecolor="#4a4a4a", linewidth=0.8, zorder=2)
for _, row in comunas.iterrows():
    c = row.geometry.centroid
    ax.annotate(row["name"], (c.x, c.y), fontsize=8, ha="center", color="#333333", zorder=4)

sc = ax.scatter(lons, lats, s=[max(m, 1) ** 2.2 for m in mags], c=mags, cmap="inferno_r",
                alpha=0.8, edgecolor="black", linewidth=0.3, zorder=3)
cbar = plt.colorbar(sc, ax=ax, label="Magnitud", shrink=0.8, pad=0.02)

ax.set_xlim(-72.1, -70.9)
ax.set_ylim(-33.6, -32.6)
ax.set_aspect("equal", adjustable="box")
ax.set_title(f"USGS - Sismicidad Región de Valparaíso (2015-2026)\n{len(mags)} eventos M≥2 reales · comunas del Gran Valparaíso como referencia", fontsize=11)
ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
fig.subplots_adjust(left=0.09, right=0.93, top=0.90, bottom=0.08)
fig.savefig(f"{EVID_IMG}/mapa_usgs_sismicidad.png", dpi=150)
print("OK mapa_usgs_sismicidad.png (con contexto geografico)")
