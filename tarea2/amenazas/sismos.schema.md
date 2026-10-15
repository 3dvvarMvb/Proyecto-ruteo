# Estructura de `sismos.json`

Lista de eventos sísmicos reales (M≥2, desde 2015) en la Región de Valparaíso.
Fuente: USGS FDSN Event API (`earthquake.usgs.gov`), sin API key.

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
