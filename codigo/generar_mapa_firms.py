"""Evidencia visual para NASA FIRMS (Amenaza 1): dos paneles.
Izquierda: focos reales detectados en TODO Chile (prueba que el pipeline
SI detecta incendios cuando existen). Derecha: zoom a la Region de
Valparaiso, donde la consulta dio 0 focos (invierno, temporada baja) -
mostrado explicitamente en vez de dejarlo como "no hay imagen"."""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import box

EVID = "evidencia"

region = gpd.read_file(f"{EVID}/region_valparaiso.geojson")
comunas = gpd.read_file(f"{EVID}/comunas_gran_valparaiso.geojson")
chile = gpd.read_file(f"{EVID}/regiones_chile.geojson")

with open(f"{EVID}/firms_chile_1dia.csv", encoding="utf-8") as f:
    rows_raw = list(csv.DictReader(f))

# El bbox de consulta ("-76,-56,-66,-17") es un rectangulo que, por ser Chile
# un pais angosto, incluye buena parte de Argentina y Bolivia al este de la
# cordillera. Se filtra por el poligono REAL de Chile (union de sus 16
# regiones) antes de contar/graficar, para no reportar focos trasandinos
# como si fueran chilenos.
from shapely.geometry import Point
chile_union = chile.geometry.union_all()
rows = []
rows_fuera = []
for r in rows_raw:
    pt = Point(float(r["longitude"]), float(r["latitude"]))
    (rows if chile_union.contains(pt) else rows_fuera).append(r)
print(f"Focos totales en el bbox: {len(rows_raw)} | dentro de Chile: {len(rows)} | fuera (AR/BO): {len(rows_fuera)}")

lons = [float(r["longitude"]) for r in rows]
lats = [float(r["latitude"]) for r in rows]
frp = [float(r["frp"]) for r in rows]  # potencia radiativa del fuego (proxy de intensidad)

lons_fuera = [float(r["longitude"]) for r in rows_fuera]
lats_fuera = [float(r["latitude"]) for r in rows_fuera]

BBOX_VALPO = box(-72.0, -33.5, -71.2, -32.7)
bx, by = BBOX_VALPO.exterior.xy

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 8), gridspec_kw={"width_ratios": [1, 1.1]})

# --- Panel 1: Chile completo ---
chile.plot(ax=ax1, facecolor="#f2ead9", edgecolor="#8a8a8a", linewidth=0.5, zorder=0)
ax1.set_facecolor("#cfe3f5")
# Focos fuera del poligono de Chile (Argentina/Bolivia, dentro del bbox pero
# no del pais) se muestran en gris para dejar en evidencia el filtro aplicado
ax1.scatter(lons_fuera, lats_fuera, s=15, c="#999999", alpha=0.5, zorder=1,
            label=f"Fuera de Chile (bbox incluye AR/BO): {len(rows_fuera)}")
sc1 = ax1.scatter(lons, lats, s=[max(f, 1) * 3 for f in frp], c=frp, cmap="hot_r",
                   alpha=0.9, edgecolor="black", linewidth=0.3, zorder=2,
                   label=f"Dentro de Chile: {len(rows)}")
ax1.plot(list(bx), list(by), color="blue", linewidth=1.5, linestyle="--", zorder=3,
         label="Bbox consultado\n(Región de Valparaíso)")
plt.colorbar(sc1, ax=ax1, label="FRP (MW)", shrink=0.6)
ax1.set_xlim(-77, -66); ax1.set_ylim(-56, -17)
ax1.set_aspect("equal", adjustable="box")
ax1.set_title(f"NASA FIRMS (VIIRS) - Chile completo\nÚltimas 24h: {len(rows)} focos reales dentro de Chile\n(bbox de consulta incluía {len(rows_fuera)} en Argentina/Bolivia, ya filtrados)")
ax1.set_xlabel("Longitud"); ax1.set_ylabel("Latitud")
ax1.legend(loc="lower left", fontsize=8)

# --- Panel 2: zoom Valparaiso (0 focos) ---
ax2.set_facecolor("#cfe3f5")
region.plot(ax=ax2, facecolor="#f2ead9", edgecolor="#8a8a8a", linewidth=0.6, zorder=0)
comunas.plot(ax=ax2, facecolor="none", edgecolor="#4a4a4a", linewidth=0.8, zorder=1)
for _, row in comunas.iterrows():
    c = row.geometry.centroid
    ax2.annotate(row["name"], (c.x, c.y), fontsize=8, ha="center", color="#333333", zorder=2)
ax2.plot(list(bx), list(by), color="blue", linewidth=1.5, linestyle="--", zorder=3)
ax2.set_xlim(-72.0, -71.2); ax2.set_ylim(-33.5, -32.7)
ax2.set_aspect("equal", adjustable="box")
ax2.set_title("Zoom: Región de Valparaíso\nÚltimos 5 días: 0 focos detectados (temporada baja)")
ax2.set_xlabel("Longitud"); ax2.set_ylabel("Latitud")

fig.suptitle("NASA FIRMS - Amenaza 1: focos de incendio activo (dato real, API con MAP_KEY)", fontsize=13, y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(f"{EVID}/mapa_firms_focos_incendio.png", dpi=150)
print("OK evidencia/mapa_firms_focos_incendio.png")
