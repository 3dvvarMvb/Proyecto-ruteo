# Estructura de `tendido_electrico.json`

Líneas de tendido eléctrico aéreo (alta tensión, media tensión y distribución menor) en el Gran Valparaíso.

**Rol operacional:** Representa un riesgo físico y directo de colisión para drones BVLOS que vuelan a baja altura sobre corredores viales, especialmente en los cerros de Valparaíso donde el cableado es denso y bajo. Encarece el costo de las aristas que cruzan o van paralelas a los cables.

**Fuente:** OpenStreetMap vía Overpass API / extracto local de Geofabrik, tags `power=line` y `power=minor_line`.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial de la línea |
| `tipo` | texto | Clasificación de tensión: `line` (alta/media tensión) o `minor_line` (distribución menor) |
| `longitud_m` | float | Longitud del tramo dentro del área del Gran Valparaíso (metros) |
| `geom_wkt` | texto | Geometría del trazado en formato WKT (LineString, EPSG:4326) |

Ejemplo:
```json
{
  "id": 1,
  "tipo": "line",
  "longitud_m": 1420.5,
  "geom_wkt": "LINESTRING (-71.615 -33.042, -71.611 -33.040, -71.608 -33.038)"
}
```
