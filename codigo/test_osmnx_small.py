"""Version reducida de la prueba OSMnx: un bbox pequeno en el centro de
Valparaiso, para verificar factibilidad sin saturar Overpass."""
import time
import osmnx as ox

ox.settings.timeout = 180
ox.settings.log_console = True

# bbox pequeno en el centro de Valparaiso (plaza Sotomayor / puerto)
north, south, east, west = -33.030, -33.050, -71.610, -71.635

t0 = time.time()
G = ox.graph_from_bbox((west, south, east, north), network_type="drive")
t1 = time.time()

nodos, aristas = ox.graph_to_gdfs(G)
print(f"Tiempo de descarga: {t1 - t0:.1f} s")
print(f"Nodos: {len(nodos)} | Aristas: {len(aristas)}")

nodos.to_file("evidencia/nodos_centro_valpo.gpkg", driver="GPKG")
aristas.to_file("evidencia/aristas_centro_valpo.gpkg", driver="GPKG")
print("Guardado en evidencia/")

fig, ax = ox.plot_graph(G, show=False, close=False, node_size=3, edge_linewidth=0.6)
fig.savefig("evidencia/mapa_centro_valpo.png", dpi=150)
print("Mapa guardado en evidencia/mapa_centro_valpo.png")
