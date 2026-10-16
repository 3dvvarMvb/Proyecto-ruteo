#!/usr/bin/env python3
"""Genera el diagrama visual de la base de datos (Punto 0 de la rubrica)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "diagrama_bd.png")

fig, ax = plt.subplots(figsize=(16, 13), dpi=200)
ax.set_xlim(0, 16)
ax.set_ylim(-3.2, 11)
ax.axis("off")

# Colores temáticos
COLOR_HEADER_INFRA = "#1f4e79"
COLOR_HEADER_NODO = "#2e75b6"
COLOR_HEADER_META = "#385723"
COLOR_HEADER_AMEN = "#c00000"
COLOR_BG = "#f9fbfd"
COLOR_BOX_BG = "#ffffff"

def draw_table(ax, x, y, width, title, columns, header_color):
    row_height = 0.28
    header_height = 0.38
    total_height = header_height + len(columns) * row_height
    
    # Sombra ligera
    shadow = patches.FancyBboxPatch(
        (x + 0.05, y - total_height - 0.05), width, total_height,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        facecolor="#d9d9d9", edgecolor="none", zorder=1
    )
    ax.add_patch(shadow)
    
    # Caja principal
    box = patches.FancyBboxPatch(
        (x, y - total_height), width, total_height,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        facecolor=COLOR_BOX_BG, edgecolor="#b0b0b0", linewidth=1, zorder=2
    )
    ax.add_patch(box)
    
    # Encabezado
    header_box = patches.Rectangle(
        (x, y - header_height), width, header_height,
        facecolor=header_color, edgecolor="none", zorder=3
    )
    ax.add_patch(header_box)
    ax.text(x + width/2, y - header_height/2, title,
            color="white", weight="bold", fontsize=9, ha="center", va="center", zorder=4)
    
    # Filas
    curr_y = y - header_height - row_height/2
    for name, dtype, note in columns:
        prefix = "PK " if "PK" in note else ("FK " if "FK" in note else "   ")
        color_pfx = "#b22222" if "PK" in note else ("#1b4f72" if "FK" in note else "#333333")
        ax.text(x + 0.12, curr_y, prefix, color=color_pfx, weight="bold", fontsize=7.5, va="center", zorder=4)
        ax.text(x + 0.45, curr_y, name, color="#222222", fontsize=7.5, weight="semibold" if "PK" in note else "normal", va="center", zorder=4)
        ax.text(x + width - 0.12, curr_y, dtype, color="#666666", fontsize=7, ha="right", va="center", zorder=4)
        curr_y -= row_height

# 1. Infraestructura
draw_table(ax, 0.5, 10.2, 3.4, "infraestructura_nodos", [
    ("id", "BIGINT", "PK"),
    ("osmid", "BIGINT", ""),
    ("lon", "DOUBLE", ""),
    ("lat", "DOUBLE", ""),
    ("geom", "Point(4326)", "GIST")
], COLOR_HEADER_INFRA)

draw_table(ax, 0.5, 7.8, 3.4, "infraestructura_aristas", [
    ("id", "BIGINT", "PK"),
    ("osmid", "BIGINT", ""),
    ("source", "BIGINT", "FK -> nodos"),
    ("target", "BIGINT", "FK -> nodos"),
    ("highway", "TEXT", ""),
    ("surface", "TEXT", ""),
    ("oneway", "BOOLEAN", ""),
    ("length_m", "DOUBLE", "Costo base"),
    ("geom", "LineString", "GIST")
], COLOR_HEADER_INFRA)

draw_table(ax, 0.5, 4.0, 3.4, "nodo_carabineros", [
    ("id", "SERIAL", "PK"),
    ("nombre", "TEXT", ""),
    ("tipo", "TEXT", "Comisaría/Tenencia"),
    ("comuna", "TEXT", ""),
    ("es_comisaria", "BOOLEAN", ""),
    ("es_punto_carga", "BOOLEAN", "Default TRUE"),
    ("nodo_vial_id", "BIGINT", "FK -> nodos"),
    ("geom", "Point(4326)", "GIST")
], COLOR_HEADER_NODO)

# 2. Metadata
draw_table(ax, 4.6, 10.2, 3.8, "metadata_viento (Open-Meteo)", [
    ("id", "SERIAL", "PK"),
    ("comuna", "TEXT", ""),
    ("sector", "TEXT", ""),
    ("elevacion_m", "DOUBLE", ""),
    ("viento_medio_kmh", "DOUBLE", ""),
    ("racha_media_kmh", "DOUBLE", ""),
    ("racha_max_kmh", "DOUBLE", "Umbral 40km/h"),
    ("direccion_deg", "DOUBLE", "Dirección"),
    ("geom", "Point(4326)", "GIST")
], COLOR_HEADER_META)

draw_table(ax, 4.6, 6.7, 3.8, "metadata_tendido_electrico", [
    ("id", "SERIAL", "PK"),
    ("tipo", "TEXT", "line / minor_line"),
    ("geom", "LineString", "GIST (OSM)")
], COLOR_HEADER_META)

draw_table(ax, 4.6, 5.0, 3.8, "metadata_relieve (Open Topo Data)", [
    ("id", "SERIAL", "PK"),
    ("arista_id", "BIGINT", "FK -> aristas"),
    ("elev_u_m", "DOUBLE", ""),
    ("elev_v_m", "DOUBLE", ""),
    ("desnivel_m", "DOUBLE", ""),
    ("pendiente_pct", "DOUBLE", "Penalización")
], COLOR_HEADER_META)

draw_table(ax, 4.6, 2.3, 3.8, "metadata_poblacion (INE Censo)", [
    ("id", "SERIAL", "PK"),
    ("comuna", "TEXT", ""),
    ("manzent", "TEXT", "ID Manzana"),
    ("total_pers", "INTEGER", "Población"),
    ("total_vivi", "INTEGER", "Viviendas"),
    ("permisos_count", "INTEGER", "Permisos 2010-18"),
    ("indice_antiguedad", "DOUBLE", "0-1, proxy sismo"),
    ("geom", "MultiPolygon", "GIST (Buffer 50m)")
], COLOR_HEADER_META)

draw_table(ax, 4.6, -0.75, 3.8, "metadata_permisos_edificacion", [
    ("id", "SERIAL", "PK"),
    ("comuna", "TEXT", ""),
    ("anio", "INTEGER", "2010-2018"),
    ("num_pisos", "INTEGER", ""),
    ("superficie_m2", "DOUBLE", ""),
    ("geom", "Point(4326)", "GIST")
], COLOR_HEADER_META)

# 3. Amenazas
draw_table(ax, 9.2, 10.2, 3.6, "amenaza_firms (NASA FIRMS)", [
    ("id", "SERIAL", "PK"),
    ("fecha", "DATE", ""),
    ("confianza", "TEXT", "n/h/l"),
    ("dentro_chile", "BOOLEAN", "Filtro ST_Intersects"),
    ("geom", "Point(4326)", "GIST (Buffer 500m)")
], COLOR_HEADER_AMEN)

draw_table(ax, 9.2, 7.7, 3.6, "amenaza_conaf_ignicion", [
    ("id", "SERIAL", "PK"),
    ("label", "INTEGER", "Decil 10..100"),
    ("rango_pi", "TEXT", "ej. '21-30'"),
    ("dia_pronostico", "INTEGER", "0..4 (5 días)"),
    ("geom", "MultiPolygon", "GIST")
], COLOR_HEADER_AMEN)

draw_table(ax, 9.2, 5.3, 3.6, "amenaza_conaf_areas_protegidas", [
    ("id", "SERIAL", "PK"),
    ("nombre", "TEXT", "SNASPE"),
    ("categoria", "TEXT", "Parque/Reserva"),
    ("sup_ha", "DOUBLE", "Superficie"),
    ("geom", "MultiPolygon", "GIST (Exclusión)")
], COLOR_HEADER_AMEN)

draw_table(ax, 9.2, 2.9, 3.6, "amenaza_sismos (USGS FDSN)", [
    ("id", "SERIAL", "PK"),
    ("usgs_id", "TEXT", "UNIQUE"),
    ("magnitud", "DOUBLE", "M >= 2"),
    ("profundidad_km", "DOUBLE", ""),
    ("fecha", "TIMESTAMP", "Epoch ms -> UTC"),
    ("lugar", "TEXT", "Valparaíso"),
    ("geom", "Point(4326)", "GIST (Destino misión)")
], COLOR_HEADER_AMEN)

# 4. Panel de Relaciones y Notas
ax.text(13.2, 10.2, "ARQUITECTURA RELACIONAL", fontsize=11, weight="bold", color="#1f4e79")
ax.text(13.2, 9.7, "• Motor: PostgreSQL 18 + PostGIS 3.6\n• Algoritmo base: pgr_dijkstra\n• k=2 rutas: penalización iterativa\n  de aristas (insp. en Suurballe 1974)\n• CRS Geométrico: EPSG:4326 (WGS84)\n• Índices: GIST espaciales en cada geom",
        fontsize=8, color="#333333", va="top")

ax.text(13.2, 8.2, "INTERACCIONES DE RUTEO", fontsize=10, weight="bold", color="#385723")
ax.text(13.2, 7.8,
        "1. Origen: nodo_carabineros\n   vinculado por KNN (<->) a la red.\n\n"
        "2. Destino: nodo vial más cercano\n   al epicentro de amenaza_sismos.\n\n"
        "3. Costo base: length_m en aristas.\n\n"
        "4. Costo dinámico:\n"
        "   costo = length_m *\n"
        "   (1 + α*viento + β*tendido\n"
        "      + γ*relieve + δ*poblacion)\n\n"
        "5. Cortes / Exclusiones:\n"
        "   - ST_DWithin(foco_firms, 500m)\n"
        "   - ST_Intersects(areas_protegidas)\n"
        "   - ST_Intersects(conaf_ignicion > umbral)\n\n"
        "6. Riesgo condicional (solo si el\n"
        "   destino es un sismo):\n"
        "   costo *= (1 + 0.3 * indice_\n"
        "   antiguedad_zona), por riesgo de\n"
        "   escombros en edificación antigua.\n"
        "   No aplica a incendios ni en\n"
        "   general (ver metadata_permisos_\n"
        "   edificacion).",
        fontsize=7.8, color="#222222", va="top")

# Flechas conectivas clave
def draw_arrow(ax, p1, p2, text=""):
    ax.annotate(text, xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="->", color="#1f4e79", lw=1.2, ls="--"),
                fontsize=7, color="#1f4e79", weight="bold")

# Conexión Carabineros -> Nodos
draw_arrow(ax, (3.9, 2.5), (3.9, 9.2), "KNN (<->)")
# Conexión Aristas -> Nodos
draw_arrow(ax, (2.2, 7.8), (2.2, 8.8), "source/target")
# Conexión Relieve -> Aristas
draw_arrow(ax, (4.6, 3.8), (3.9, 6.0), "arista_id")
# Conexión Permisos Edificación -> Población (join espacial, no FK)
draw_arrow(ax, (6.5, -0.75), (6.5, 0.3), "ST_Contains")

# Título general superior
fig.suptitle("Modelo de Base de Datos Geoespacial — Ruteo Resiliente de Drones BVLOS (Gran Valparaíso)\nPostgreSQL + PostGIS + pgRouting",
             fontsize=14, weight="bold", y=0.98, color="#0f2537")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(SALIDA, bbox_inches="tight")
print(f"OK: Diagrama guardado en {SALIDA}")
