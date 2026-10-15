# Estructura de `carabineros.json`

Lista de cuarteles de Carabineros de Chile (comisarías, tenencias, subcomisarías y retenes) en el Gran Valparaíso (Valparaíso, Viña del Mar, Concón, Quilpué, Villa Alemana).

**Rol operacional:** Nodos especiales de la red que actúan como puntos de origen del dron y estaciones de recarga de batería.

**Fuente:** Carabineros de Chile, Feature Service ArcGIS público (`services6.arcgis.com/LCdFQd7nnAn5xeUA/arcgis/rest/services/Cuarteles_Carabineros/FeatureServer/0`).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial del cuartel |
| `nombre` | texto | Nombre oficial de la unidad policial (ej. `8VA. COM. FLORIDA VALPO.`) |
| `comuna` | texto | Comuna a la que pertenece |
| `es_comisaria` | booleano | `true` si es Comisaría principal (centro de mando preferente), `false` para tenencias/retenes |
| `es_punto_carga` | booleano | `true` (todos los cuarteles cuentan con infraestructura eléctrica permanente para recarga) |
| `lon` | float | Longitud del cuartel (EPSG:4326) |
| `lat` | float | Latitud del cuartel (EPSG:4326) |

Ejemplo:
```json
{
  "id": 1,
  "nombre": "8VA. COM. FLORIDA VALPO.",
  "comuna": "Valparaíso",
  "es_comisaria": true,
  "es_punto_carga": true,
  "lon": -71.621817,
  "lat": -33.053137
}
```
