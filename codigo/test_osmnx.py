"""4.3 Evidencia de factibilidad - descarga del grafo vial con OSMnx."""
import time
import osmnx as ox

ox.settings.log_console = True

lugares = ["Valparaíso, Chile"]

t0 = time.time()
G = ox.graph_from_place(lugares, network_type="drive")
t1 = time.time()

nodos, aristas = ox.graph_to_gdfs(G)

print(f"Tiempo de descarga: {t1 - t0:.1f} s")
print(f"Nodos: {len(nodos)} | Aristas: {len(aristas)}")
print(f"CRS: {nodos.crs}")
print(f"Bounding box: {nodos.total_bounds}")

nodos.to_file("evidencia/datos/nodos_valparaiso.gpkg", driver="GPKG")
aristas.to_file("evidencia/datos/aristas_valparaiso.gpkg", driver="GPKG")
print("Guardado en evidencia/datos/nodos_valparaiso.gpkg y aristas_valparaiso.gpkg")

# Mapa estático como evidencia visual
fig, ax = ox.plot_graph(G, show=False, close=False, node_size=2, edge_linewidth=0.5)
fig.savefig("evidencia/imagenes/mapa_valparaiso.png", dpi=150)
print("Mapa guardado en evidencia/imagenes/mapa_valparaiso.png")
