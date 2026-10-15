"""Grafico comparativo de viento/rachas por punto (6 puntos de Open-Meteo,
uno por comuna + Valparaiso dividido en plan/costa y cerros/interior alto),
mostrando por que un solo punto no representaba bien todo el Gran Valparaiso."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVID = "evidencia/datos"
EVID_IMG = "evidencia/imagenes"

with open(f"{EVID}/open_meteo_resumen_por_comuna.json", encoding="utf-8") as f:
    resumen = json.load(f)

etiquetas_cortas = {
    "Plan / costa": "Plan/costa",
    "Cerros / Placilla (interior alto)": "Cerros/Placilla",
}
comunas = [f"{r['comuna']}\n({etiquetas_cortas.get(r['sector'], r['sector'])})" if r["sector"] != "—" else r["comuna"] for r in resumen]
medias_viento = [sum(r["viento_10m"]) / len(r["viento_10m"]) for r in resumen]
medias_rachas = [sum(r["rachas_10m"]) / len(r["rachas_10m"]) for r in resumen]
max_rachas = [r["racha_maxima"] for r in resumen]

x = range(len(comunas))
width = 0.28

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.bar([i - width for i in x], medias_viento, width, label="Viento medio (km/h)", color="#3498db", edgecolor="black")
ax.bar(x, medias_rachas, width, label="Rachas medias (km/h)", color="#f39c12", edgecolor="black")
ax.bar([i + width for i in x], max_rachas, width, label="Racha máxima pronosticada (km/h)", color="#c0392b", edgecolor="black")

ax.set_xticks(list(x))
ax.set_xticklabels(comunas, fontsize=9)
ax.set_ylabel("km/h")
ax.set_title("Viento por punto — Open-Meteo, 6 puntos (Gran Valparaíso)\nJustifica medir en varios puntos: la racha máxima varía de 32 a 55 km/h según el punto")
ax.legend(fontsize=9)
ax.grid(axis="y", linestyle=":", alpha=0.6)
fig.tight_layout()
fig.savefig(f"{EVID_IMG}/grafico_viento_por_comuna.png", dpi=150)
print("OK evidencia/imagenes/grafico_viento_por_comuna.png")
