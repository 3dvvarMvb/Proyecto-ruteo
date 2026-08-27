"""Construye el grafo vial del Gran Valparaiso desde el extracto local de
Geofabrik (recortado con osmium), sin depender de Overpass en vivo."""
import time
import osmnx as ox

ox.settings.log_console = True

t0 = time.time()
G = ox.graph_from_xml("data/valparaiso_drive.osm.xml")
t1 = time.time()

nodos, aristas = ox.graph_to_gdfs(G)
print(f"Tiempo de construccion del grafo: {t1 - t0:.1f} s")
print(f"Nodos: {len(nodos)} | Aristas: {len(aristas)}")
print(f"CRS: {nodos.crs}")

nodos.to_file("evidencia/datos/nodos_valparaiso.gpkg", driver="GPKG")
aristas.to_file("evidencia/datos/aristas_valparaiso.gpkg", driver="GPKG")
print("Guardado en evidencia/datos/nodos_valparaiso.gpkg y aristas_valparaiso.gpkg")

fig, ax = ox.plot_graph(
    G, show=False, close=False,
    node_size=1.5, node_color="#8B0000",
    edge_linewidth=0.5, edge_color="#333333",
    bgcolor="#cfe3f5",
)
ax.set_title(f"Grafo vial real - Gran Valparaíso (OSM vía Geofabrik)\n{len(nodos):,} nodos, {len(aristas):,} aristas", fontsize=11, color="black")
fig.savefig("evidencia/imagenes/mapa_grafo_valparaiso.png", dpi=150)
print("Mapa guardado en evidencia/imagenes/mapa_grafo_valparaiso.png")
