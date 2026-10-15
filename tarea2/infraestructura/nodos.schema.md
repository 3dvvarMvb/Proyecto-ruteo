# Estructura de `nodos.json`

Lista de objetos, uno por intersección/nodo del grafo vial del Gran Valparaíso
(fuente: OpenStreetMap vía extracto de Geofabrik, ver Tarea 1).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador interno del nodo (= `osmid`, se usa como PK y como `source`/`target` en `aristas.json`) |
| `osmid` | entero | Identificador original del nodo en OpenStreetMap |
| `lon` | float | Longitud (EPSG:4326, grados decimales) |
| `lat` | float | Latitud (EPSG:4326, grados decimales) |

Ejemplo:
```json
{"id": 123456789, "osmid": 123456789, "lon": -71.6127, "lat": -33.0472}
```
