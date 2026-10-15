# Estructura de `aristas.json`

Lista de objetos, uno por tramo de calle del grafo vial del Gran Valparaíso
(fuente: OpenStreetMap vía extracto de Geofabrik, ver Tarea 1).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador interno de la arista (secuencial, PK) |
| `osmid` | entero | Identificador original de la vía (way) en OpenStreetMap |
| `source` | entero | `id` del nodo de origen (FK a `nodos.json`) |
| `target` | entero | `id` del nodo de destino (FK a `nodos.json`) |
| `highway` | texto o null | Tipo de vía OSM (`primary`, `secondary`, `residential`, etc.) |
| `surface` | texto o null | Tipo de superficie OSM (`asphalt`, `paved`, `unpaved`, etc., si está etiquetado) |
| `oneway` | booleano | Si la vía es de sentido único |
| `length_m` | float | Largo real de la arista en metros — **costo usado por `pgr_dijkstra` en la Fase 2** |
| `geom_wkt` | texto | Geometría de la arista en formato WKT (LineString, EPSG:4326) |

Ejemplo:
```json
{"id": 1, "osmid": 27633392, "source": 123456789, "target": 987654321,
 "highway": "residential", "surface": null, "oneway": false,
 "length_m": 85.3, "geom_wkt": "LINESTRING (-71.61 -33.04, -71.609 -33.041)"}
```
