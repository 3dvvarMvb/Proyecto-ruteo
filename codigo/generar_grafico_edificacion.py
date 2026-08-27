"""Reemplaza la tabla de 8 filas (Overpass en vivo) por un histograma real
de la distribucion de alturas de edificacion en el Gran Valparaiso, usando
el extracto local de Geofabrik (74.550 edificios, 17.961 con dato de altura)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia"

with open(f"{EVID}/overpass_local_edificacion.json", encoding="utf-8") as f:
    data = json.load(f)

niveles = []
for el in data["elementos"]:
    v = el["building:levels"]
    if v != "-":
        try:
            niveles.append(float(v))
        except ValueError:
            pass

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(niveles, bins=range(0, 22), color="#c0392b", edgecolor="black", alpha=0.85)
ax.set_title(
    f"Distribución de altura de edificación — Gran Valparaíso (OSM vía Geofabrik)\n"
    f"{data['total_edificios']:,} edificios totales · {data['con_altura']:,} con dato de altura "
    f"({data['con_altura']/data['total_edificios']*100:.1f}% de cobertura)"
)
ax.set_xlabel("building:levels (pisos)")
ax.set_ylabel("Cantidad de edificios")
fig.tight_layout()
fig.savefig(f"{EVID}/grafico_edificacion_valparaiso.png", dpi=150)
print("OK evidencia/grafico_edificacion_valparaiso.png")
print(f"Mediana de pisos: {sorted(niveles)[len(niveles)//2]}")
print(f"Máximo: {max(niveles)}")
