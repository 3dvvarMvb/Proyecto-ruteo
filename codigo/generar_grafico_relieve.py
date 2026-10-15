"""Histograma de pendiente de aristas (muestra real del grafo vial)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia/datos"
EVID_IMG = "evidencia/imagenes"

with open(f"{EVID}/relieve_muestra_aristas.json", encoding="utf-8") as f:
    datos = json.load(f)

pendientes = [d["pendiente_pct"] for d in datos]

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.hist(pendientes, bins=20, color="#8e44ad", edgecolor="black", alpha=0.85)
ax.axvline(15, color="#c0392b", linestyle="--", linewidth=2, label="15% — umbral de pendiente empinada")
ax.set_title(f"Pendiente del terreno por arista — muestra de {len(pendientes)} tramos del grafo vial\nGran Valparaíso (elevación vía Open Topo Data / SRTM 90m)")
ax.set_xlabel("Pendiente (%)")
ax.set_ylabel("Cantidad de aristas")
ax.legend()
ax.grid(axis="y", linestyle=":", alpha=0.6)
fig.tight_layout()
fig.savefig(f"{EVID_IMG}/grafico_relieve_pendiente.png", dpi=150)
print("OK evidencia/imagenes/grafico_relieve_pendiente.png")
