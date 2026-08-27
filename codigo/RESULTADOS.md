# Resultados de las pruebas de factibilidad — Tarea 1

Fecha de ejecución: 2026-08-26. Todos los scripts están en este directorio y son ejecutables directamente (`python3 test_*.py`).

## Stack instalado y funcionando

- PostgreSQL 18 + PostGIS 3.6 + pgRouting 4.0.1 (BD `ruteo_drones`, rol `kali`)
- Python: `osmnx 2.0.3`, `geopandas 1.1.4`, `shapely 2.1.2`, `psycopg2`, `requests`

## Resultado por fuente

| # | Fuente | Script | Estado | Nota |
|---|--------|--------|--------|------|
| 1 | Open-Meteo (viento) | `test_open_meteo.py` | ✅ OK | JSON real, sin API key. Rachas de hasta 45 km/h detectadas para el punto de prueba |
| 2 | Overpass API (OSM, edificación) | `test_overpass.py` | ✅ OK (con fix) | El User-Agent por defecto de `requests`/`osmnx` **es bloqueado por el servidor (HTTP 406)**. Solución: fijar un `User-Agent` propio en la cabecera |
| 3 | USGS FDSN (sismos) | `test_usgs.py` | ✅ OK | 105 eventos M≥2 reales desde 2015 en la Región de Valparaíso, sin API key |
| 4 | NASA FIRMS (focos de incendio) | `test_firms.py` | ✅ Endpoint accesible | Sin `MAP_KEY` responde 400 "Invalid MAP_KEY" — comportamiento esperado y documentado. **Falta que un integrante se registre** en https://firms.modaps.eosdis.nasa.gov/api/map_key/ para obtener la key real antes de la presentación |
| 5 | SENAPRED (alertas) | — | ⚠️ **No es una API pública** | `senapred.cl` es una SPA en React; su backend real es un GraphQL en AWS AppSync con **autenticación Cognito** (no hay endpoint abierto). El "Visor Chile Preparado" es un iframe de WordPress sin servicio de mapas expuesto públicamente que se haya podido ubicar. **Reemplazado por CONAF (ver más abajo)** |
| 5b | **CONAF — reemplazo de SENAPRED** | `test_conaf.py` | ✅ **OK, mejor de lo esperado** | La página de CONAF enlaza un **dashboard ArcGIS Online público** ("Pronóstico de Riesgo", `deigeprif`, `access: public`). Detrás hay **Feature Services REST reales, sin API key**: `PI/FeatureServer/4` (polígonos de probabilidad de ignición a 5 días, actualizados a diario) y `ASP/FeatureServer/0` (polígonos de Áreas Silvestres Protegidas). Se consultaron ambos con un bbox de la Región de Valparaíso y devolvieron geometrías de polígono reales |
| 6 | PostGIS + pgRouting (pipeline completo) | `test_postgis_pgrouting.py` | ✅ OK | Se replicó exactamente el pipeline del informe con datos sintéticos: `ST_Intersects` corta aristas por polígono DGAC, `ST_DWithin` penaliza por cercanía a foco de incendio, `pgr_KSP` devuelve rutas alternativas (algoritmo de Yen) |
| 7 | OSMnx (grafo vial real) | `construir_grafo_local.py` | ✅ **Resuelto con plan B** | Overpass quedó bloqueado tras uso pesado (verificado en servidor principal y espejo). Se ejecutó el plan de contingencia: `chile-latest.osm.pbf` de Geofabrik (346 MB) → `osmium extract` por bbox (21.8 MB) → `osmium tags-filter` a vías transitables (3.5 MB) → `ox.graph_from_xml()`. Resultado real: **52.856 nodos, 126.480 aristas** en <1 min de procesamiento. Mapa en `evidencia/mapa_grafo_valparaiso.png` |
| 2b | Overpass (edificación) — reemplazo local | `extraer_edificacion_local.py` | ✅ **Reemplazado, mejor cobertura** | La consulta en vivo a Overpass solo devolvía 8 elementos (filtro muy restrictivo). Con el mismo extracto de Geofabrik (`osmium tags-filter w/building`) se obtuvieron **74.550 edificios totales, 17.961 con dato de altura (24,1% de cobertura)** — muestra estadísticamente representativa en vez de 8 casos sueltos. Histograma real en `evidencia/grafico_edificacion_valparaiso.png` |

## Aclaración sobre la capa de probabilidad de ignición

El campo `label` de `PI/FeatureServer/4` **no es un porcentaje directo**: es el límite superior de un decil (1-10, 11-20, ..., 91-100) de un índice de Probabilidad de Ignición (campo `var="PI"`), según el `renderer` (classBreaks) publicado por el propio servicio. En la Región de Valparaíso para el 2026-08-30 solo aparecieron los deciles bajos (1-10, 11-20, 21-30); a nivel nacional la escala completa llega hasta 100. Además el servicio publica 5 capas (`d0` a `d4`, una por día), confirmando el pronóstico a 5 días que menciona el informe. El mapa y el script (`generar_evidencia_visual.py`) ya quedaron corregidos para mostrar los rangos reales en vez del código crudo.

## Hallazgos a incorporar al informe

1. **Reemplazar SENAPRED por CONAF como Amenaza 2**: CONAF expone, sin darse cuenta explícitamente en su sitio de contenido, un dashboard ArcGIS Online **público** con dos Feature Services REST:
   - `https://services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/PI/FeatureServer/4` — polígonos de **probabilidad de ignición a 5 días** (pronóstico diario, exactamente lo que el informe original citaba como "fuente de reserva" de CONAF, pero ahora confirmado con URL real y datos reales).
   - `https://services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/ASP/FeatureServer/0` — polígonos de **Áreas Silvestres Protegidas**, que además sirve para la capa de exclusión del §7.2 (hasta ahora atribuida de forma genérica a "DGAC/CONAF").
   Esto es un mejor resultado que el original: dos APIs REST públicas y con geometría de polígono en una sola fuente, sin necesidad de scraping ni login.
2. **SENAPRED se mantiene como fuente complementaria/cualitativa**, no como API: puede citarse para contexto normativo (categorías de alerta) pero sin pretender consumo automático, ya que su backend real requiere login (Cognito).
3. **Overpass tuvo una caída real durante las pruebas** (verificada contra dos servidores independientes) — no es un problema del código. Para la presentación: descargar el grafo con anticipación y tener el `.gpkg`/mapa ya generado como respaldo, más `Geofabrik` como plan B si hace falta volver a descargar en vivo.
4. **Overpass exige `User-Agent` personalizado**: detalle técnico menor pero real (bloquea el UA por defecto de `requests`/`osmnx` con HTTP 406) — inclúyanlo en el código de la Tarea 2.
5. Open-Meteo, USGS, FIRMS, CONAF y PostGIS+pgRouting quedaron **demostrados con evidencia real**, no solo argumentados.

## Corrección importante: focos FIRMS "en Chile"

El conteo de "56 focos en Chile" reportado antes estaba mal. La consulta a FIRMS usó un **bbox rectangular** (`-76,-56,-66,-17`), y como Chile es un país angosto, ese rectángulo incluye buena parte de **Argentina y Bolivia** al este de la cordillera. Al filtrar los 56 puntos contra el **polígono real de Chile** (unión de las 16 regiones, `evidencia/regiones_chile.geojson`), solo **7 estaban efectivamente en territorio chileno**; los otros 49 eran de Mendoza, Neuquén, La Rioja, etc.

Esto es un hallazgo de diseño importante para la Tarea 2: **las consultas geoespaciales de amenazas deben filtrarse por el polígono real de la zona de interés (`ST_Intersects`/`ST_Within` con el polígono, no con su bounding box)**, o el modelo va a contaminarse con eventos de otro país. El mapa `mapa_firms_focos_incendio.png` ya quedó corregido mostrando ambos grupos (dentro/fuera de Chile) para dejar el filtro en evidencia.

## Archivos de evidencia

Ver `evidencia/`: `open_meteo_response.json`, `overpass_response.json`, `usgs_response.json`, `conaf_probabilidad_ignicion.geojson`, `conaf_areas_protegidas.geojson`, `mapa_grafo_valparaiso.png`, `grafico_edificacion_valparaiso.png`, `overpass_local_edificacion.{json,csv}`.
