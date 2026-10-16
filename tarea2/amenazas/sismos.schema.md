# Estructura de `sismos.json`

Lista de eventos sísmicos reales (M≥2, desde 2015) en la Región de Valparaíso.
Fuente: USGS FDSN Event API (`earthquake.usgs.gov`), sin API key.

**Qué sismos son destino válido de ruteo:** no todos — se excluye un sismo si el nodo vial más cercano a su epicentro supera `distancia_max_valida_sismo_km(magnitud, racha_viento_zona)` (función SQL en `db/schema.sql`), que es el **mínimo** entre:
- un radio de relevancia según la magnitud (Wells & Coppersmith, 1994, *"New Empirical Relationships among Magnitude, Rupture Length..."*, BSSA 84(4):974-1002), y
- un radio operacional que se reduce con el viento real de la zona, acotado por las specs del **DJI Matrice 300 RTK** (alcance máximo de transmisión 15km, resistencia al viento 12-15 m/s según fase de vuelo — ver `metadata/viento.schema.md`).

Ver justificación completa en `README.md`, sección "Qué sismos son destinos válidos".

| Campo | Tipo | Descripción |
|---|---|---|
| `usgs_id` | texto | Identificador único del evento en USGS |
| `magnitud` | float | Magnitud del sismo |
| `profundidad_km` | float | Profundidad del hipocentro en km |
| `fecha` | entero | Fecha/hora del evento, epoch en milisegundos (UTC) |
| `lugar` | texto | Descripción textual del lugar (USGS) |
| `lon`, `lat` | float | Epicentro (EPSG:4326) |

Ejemplo:
```json
{"usgs_id": "us7000abcd", "magnitud": 4.5, "profundidad_km": 35.2,
 "fecha": 1700000000000, "lugar": "12km W of Valparaíso, Chile",
 "lon": -71.65, "lat": -33.02}
```
