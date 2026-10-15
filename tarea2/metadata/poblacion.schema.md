# Estructura de `poblacion.json`

Polígonos de manzanas censales urbanas con población y viviendas en las 5 comunas del Gran Valparaíso (Valparaíso, Viña del Mar, Concón, Quilpué, Villa Alemana).

**Rol operacional:** Cuantifica la densidad y exposición de personas en tierra bajo el corredor aéreo. Un vuelo sobre manzanas densamente habitadas concentra alto riesgo ante fallas mecánicas, por lo que el algoritmo de ruteo resiliente encarece estas aristas mediante un buffer espacial de 50 metros, empujando la trayectoria hacia corredores viales más despejados.

**Fuente:** Censo 2017 (INE), publicado como Feature Service ArcGIS público por el Observatorio de Ciudades UC (`services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Manzanas_censo_2017/FeatureServer/0`).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial de la manzana |
| `comuna` | texto | Nombre de la comuna oficial |
| `manzent` | texto | Código único censal de la manzana (`MANZENT_I`) |
| `total_pers` | entero | Total de personas residentes en la manzana censal |
| `total_vivi` | entero | Total de viviendas registradas en la manzana censal |
| `geom_wkt` | texto | Geometría del polígono en formato WKT (Polygon / MultiPolygon, EPSG:4326) |

Ejemplo:
```json
{
  "id": 1,
  "comuna": "Valparaíso",
  "manzent": "05101011001001",
  "total_pers": 84,
  "total_vivi": 26,
  "geom_wkt": "POLYGON ((-71.621 -33.048, -71.620 -33.049, -71.619 -33.048, -71.621 -33.048))"
}
```
