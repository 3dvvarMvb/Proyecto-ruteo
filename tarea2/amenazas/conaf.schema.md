# Estructura de Amenazas CONAF: `conaf_ignicion.json` y `conaf_areas_protegidas.json`

Amenazas y restricciones biológicas gestionadas por la Corporación Nacional Forestal (CONAF).

---

## 1. `conaf_ignicion.json` (Pronóstico de Riesgo de Ignición)

**Rol operacional:** Modela el riesgo predictivo a 5 días de ocurrencia y propagación de incendios forestales. A diferencia de un foco activo (corte puntual), una zona con alta probabilidad de ignición (deciles 70-100) encarece las rutas de manera regional, empujando la navegación hacia corredores estadísticamente más seguros.

**Fuente:** CONAF GEPRIF, Feature Service ArcGIS REST público (`services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/PI/FeatureServer/4`).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial del polígono |
| `label` | entero | Límite superior del decil de probabilidad (10, 20, 30, ..., 100) |
| `rango_pi` | texto | Rango explicativo del índice (ej. `"1-10"`, `"21-30"`) |
| `dia_pronostico` | entero | Día del pronóstico proyectado (0 a 4) |
| `geom_wkt` | texto | Geometría del polígono en formato WKT (Polygon / MultiPolygon, EPSG:4326) |

---

## 2. `conaf_areas_protegidas.json` (Áreas Silvestres Protegidas - SNASPE)

**Rol operacional:** Polígonos de exclusión aérea permanente y ambiental. La normativa de Parques Nacionales, Reservas Nacionales y Santuarios de la Naturaleza prohíbe el sobrevuelo de RPAS para proteger avifauna y ecosistemas frágiles. Corta de forma absoluta las aristas que intersecan (`ST_Intersects`).

**Fuente:** CONAF SNASPE, Feature Service ArcGIS REST público (`services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/ASP/FeatureServer/0`).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial del área protegida |
| `nombre` | texto | Nombre oficial de la unidad (ej. `Reserva Nacional Lago Peñuelas`, `La Campana`) |
| `categoria` | texto | Categoría de manejo: `Reserva Nacional`, `Parque Nacional`, `Monumento Natural` |
| `sup_ha` | float | Superficie oficial en hectáreas |
| `geom_wkt` | texto | Geometría del polígono en formato WKT (Polygon / MultiPolygon, EPSG:4326) |
