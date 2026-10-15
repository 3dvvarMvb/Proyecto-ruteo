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
| 2b | ~~Overpass (edificación) — reemplazo local~~ | `extraer_edificacion_local.py` | 🗑️ **Descartada** | Ver sección "Metadata #2 descartada: altura de edificación" más abajo — se reemplazó por tendido eléctrico |
| 2c | ~~Google Open Buildings 2.5D Temporal~~ | `extraer_google_open_buildings.py` | 🗑️ **Descartada** | Ver sección "Metadata #2 descartada: altura de edificación" más abajo — feedback del profesor, sin buena justificación para el ruteo del dron |
| 2d | **Tendido eléctrico aéreo (nueva Metadata #2)** | `test_tendido_electrico.py` | ✅ **OK** | Ver sección "Metadata #2 (reemplazo): tendido eléctrico aéreo" más abajo |
| 2e | **Pendiente del terreno / relieve (metadata adicional)** | `test_relieve.py` | ✅ **OK** | Ver sección "Metadata adicional: pendiente del terreno (relieve)" más abajo |
| 2f | **Cuarteles de Carabineros (nodos de origen/carga)** | `test_carabineros.py` | ✅ **OK** | Ver sección "Nodo de origen y puntos de carga: Cuarteles de Carabineros" más abajo |
| 3b | INE — población por manzana censal (Metadata #3) | `generar_mapa_poblacion.py` | ✅ **OK** | El portal genérico del INE no tiene un endpoint REST abierto usable; se encontró el mismo Censo 2017 reprocesado en un **Feature Service ArcGIS público, sin API key**, publicado por el **Observatorio de Ciudades UC** (`https://services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Manzanas_censo_2017/FeatureServer`). Con paginación (`resultOffset`, tope de 2000 registros/página) y el nombre de comuna con tilde correcto (`VALPARAÍSO`, no `VALPARAISO`) se obtuvieron **10.750 manzanas reales con geometría de polígono y 1.005.013 habitantes** en las 5 comunas del Gran Valparaíso. Mapa de densidad en `evidencia/imagenes/mapa_ine_poblacion_manzanas.png` |

## Aclaración sobre la capa de probabilidad de ignición

El campo `label` de `PI/FeatureServer/4` **no es un porcentaje directo**: es el límite superior de un decil (1-10, 11-20, ..., 91-100) de un índice de Probabilidad de Ignición (campo `var="PI"`), según el `renderer` (classBreaks) publicado por el propio servicio. En la Región de Valparaíso para el 2026-08-30 solo aparecieron los deciles bajos (1-10, 11-20, 21-30); a nivel nacional la escala completa llega hasta 100. Además el servicio publica 5 capas (`d0` a `d4`, una por día), confirmando el pronóstico a 5 días que menciona el informe. El mapa y el script (`generar_evidencia_visual.py`) ya quedaron corregidos para mostrar los rangos reales en vez del código crudo.

## Aclaración sobre el mapa de población por manzana (Quilpué vs. Valparaíso)

En el mapa `mapa_ine_poblacion_manzanas.png`, la comuna de Quilpué se ve casi vacía de manzanas mientras Valparaíso se ve "completa". No es un error de la consulta ni de la geometría de los límites comunales (se verificó contra el propio Feature Service `Comunas` de CONAF, que coincide con el área oficial de cada comuna): es que las "manzanas" censales del INE solo existen en el **área urbana**; el área rural se censa con otro tipo de entidad (localidades/entidades rurales, sin geometría de manzana). La proporción urbana/rural difiere mucho entre comunas:

- **Valparaíso**: ~402 km² totales, ~99,7% de la población es urbana (casi toda la comuna, incluidos los cerros, se considera urbana para el censo) → las manzanas cubren casi todo el contorno comunal.
- **Quilpué**: ~537 km² totales, pero solo ~21,6 km² (≈4%) son área urbana; los ~515 km² restantes son precordillera rural sin manzanas → en el mapa solo aparece un núcleo pequeño de manzanas rodeado de un contorno comunal mucho más grande.

De paso se detectó y descartó una falsa alarma propia: al calcular el área de los polígonos comunales reproyectando a Web Mercator (EPSG:3857) da un valor ~43% más alto que el real (a esta latitud, `1/cos²(33°) ≈ 1,42`, que es justo el factor de más que aparecía). El campo `area` nativo del Feature Service de CONAF (en hectáreas) sí coincide con las superficies oficiales (ej. Quilpué: 534,8 km² del servicio vs. 536,9 km² oficial). Para cualquier cálculo de área en la Tarea 2 hay que reproyectar a un CRS proyectado adecuado para Chile (ej. UTM 19S / EPSG:32719), nunca usar Web Mercator para mediciones.

## Corrección de escala de color en el mapa de población por manzana

La primera versión del mapa usaba una escala de color lineal de 0 hasta el máximo real (2.754 hab./manzana), lo que hacía ver casi todo el mapa del mismo color oscuro. La distribución real es muy sesgada: mediana de **58 habitantes por manzana**, y el **95% de las 10.750 manzanas tiene 302 habitantes o menos** (solo 31 manzanas, 0,3%, superan 1.000). Al estirar la escala hasta el máximo, esas pocas manzanas densas (edificios altos) comprimían al resto en la parte inferior de la paleta, ocultando la variación real entre baja y media densidad.

Se corrigió recortando la escala de color en 300 (percentil 95), con una flecha en la barra de color indicando "300 o más" para las manzanas por encima de ese umbral (`vmin=0, vmax=300, extend="max"` en `generar_mapa_poblacion.py`). Con esto el mapa distingue correctamente los núcleos de alta densidad (costa de Viña del Mar, Villa Alemana) de las zonas de baja densidad.

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

## Metadata #2 descartada: altura de edificación

**Se descartó la altura de edificación como Metadata #2** (tanto la versión por OSM/Overpass como el reemplazo con Google Open Buildings 2.5D, documentada íntegra más abajo para que quede el registro del trabajo hecho). Motivo: feedback directo del profesor — no había una justificación sólida de **por qué la altura de un edificio debería penalizar el costo de una arista** para un dron que vuela siguiendo el trazado de las calles (a diferencia del tendido eléctrico o la pendiente, que sí tienen un mecanismo de riesgo directo y obvio).

**Reemplazada por**: tendido eléctrico aéreo (penaliza aristas por riesgo de colisión) y pendiente del terreno (penaliza aristas por exigencia de vuelo/pérdida de línea de vista C2) — ver secciones más abajo. La sección de Google Open Buildings se deja documentada tal cual se dejó funcionando, por transparencia del trabajo, pero **no se usa en el informe final**.

## Metadata #2 (reemplazo): tendido eléctrico aéreo

**Justificación**: los cables de alta/media tensión son un riesgo de colisión físico y directo para un dron de bajo vuelo — es una de las causas más comunes de accidentes de drones urbanos, y en los cerros de Valparaíso el tendido sobre las calles es particularmente denso y bajo. A diferencia de la altura de edificación, acá el mecanismo de riesgo es directo y obvio.

**Fuente**: Overpass API, tags `power=line` (alta/media tensión) y `power=minor_line` (distribución) de OpenStreetMap (`test_tendido_electrico.py`). Overpass volvió a mostrarse inestable (504 Gateway Timeout con `out geom` en los primeros intentos, igual que en pruebas anteriores de este grupo) — funcionó al reintentar con `[maxsize]` más alto; el script cachea el resultado para no depender de la red en corridas repetidas.

**Bug encontrado y corregido (mismo patrón que el de FIRMS)**: Overpass devuelve la **geometría completa** de cada línea aunque solo un tramo cruce el área consultada — se encontró una sola línea de transmisión de **178,7 km** completa en la respuesta. Sin corregir esto, el largo total sumaba 1.052,8 km. Se corrigió recortando cada línea (`shapely.intersection`) al polígono real del área antes de medir, dando un largo real de **565,5 km** dentro del Gran Valparaíso.

**Resultado real**: **100 tramos** de tendido eléctrico (71 de alta/media tensión, 29 de distribución menor), ~565 km dentro del área. Datos en `evidencia/datos/osm_tendido_electrico.json`, mapa en `evidencia/imagenes/mapa_tendido_electrico.png` (`generar_mapa_tendido_electrico.py`).

**Implicancia para el algoritmo de la Tarea 2**: aristas que cruzan o corren paralelas a una línea eléctrica reciben un costo adicional (o se excluyen si el cruce es a baja altura).

## Metadata adicional: pendiente del terreno (relieve)

**Justificación**: Valparaíso es conocido por sus cerros empinados; una arista con pendiente fuerte es más exigente para el vuelo del dron (aerodinámica, estabilidad) y reduce la línea de vista para el enlace de comando y control (C2) con antenas en el corredor — conecta directo con el "Argumento 3" del informe.

**Fuente**: se probó primero con **Open-Elevation** (`api.open-elevation.com`), pero su instancia pública devolvió `429 Too Many Requests` de forma persistente. Se cambió a **Open Topo Data** (`api.opentopodata.org`, dataset SRTM 90m), pública y sin API key (límite: ~1 request/seg, 100 puntos/request), que respondió bien. Los valores de elevación son consistentes entre las 3 fuentes probadas para los mismos puntos (Valparaíso plan ~15-18 m, Placilla ~324-330 m en Open-Meteo, Open-Elevation y Open Topo Data).

**Prueba real**: sobre una muestra de 300 aristas reales del grafo vial local ya construido (52.856 nodos, 126.480 aristas), calculando el desnivel entre los nodos de cada arista (`test_relieve.py`):
- Pendiente media: **4,2%**, mediana: 3,0%, P90: 10,4%, máxima: 23,9%
- Aristas con pendiente > 15% (empinadas): 8 de 300 (2,7%)

Histograma en `evidencia/imagenes/grafico_relieve_pendiente.png`, datos completos en `evidencia/datos/relieve_muestra_aristas.json`.

**Implicancia para el algoritmo de la Tarea 2**: el costo de la arista debe incluir un término proporcional a la pendiente (desnivel/largo), no solo a la distancia plana.

## (Documentación histórica, no usada en el informe final) Google Open Buildings 2.5D Temporal para Alturas de Edificación

Para resolver la limitación de OpenStreetMap donde solo el **24,1% de los edificios (17.961 de 74.550)** cuenta con datos de altura (`building:levels` o `height`), se integró el **Google Open Buildings 2.5D Temporal Dataset (versión v1, 2023)** desarrollado por Google Research.

### Aspectos técnicos de la fuente
- **Formato y Cobertura**: Cloud Optimized GeoTIFFs (COGs) en Google Cloud Storage (`gs://open-buildings-temporal-data/v1/geotiffs/`), organizados por S2 cells y proyectados en **UTM 19S / EPSG:32719**.
- **Bandas**: `building_height` (altura en metros por estructura), `building_presence` (probabilidad/confianza de presencia de estructura) y `building_fractional_count`.
- **Resolución**: Resolución efectiva de ~4 metros a partir de imágenes satelitales Sentinel-2 procesadas con Deep Learning.
- **Acceso Directo**: Se consultó el manifiesto oficial `97_EPSG_32719_2023_06_30.json` y se descargaron los bloques ráster de las 5 comunas del Gran Valparaíso (Valparaíso, Viña del Mar, Concón, Quilpué, Villa Alemana).

### Resultados cuantitativos consolidados (Gran Valparaíso)
- **Estructuras urbanas identificadas**: **85.268** puntos/polígonos de edificación continua (100% de cobertura espacial).
- **Altura mínima**: 0,04 m (estructuras a nivel de suelo / muros).
- **Altura mediana**: **5,38 m** (~2 a 2,5 pisos, representativo de la tipología residencial dominante en cerros de Valparaíso y Quilpué).
- **Altura media**: **7,67 m**.
- **Percentil 90 (P90)**: **12,94 m** (~5 pisos).
- **Percentil 95 (P95)**: **18,63 m** (~7-8 pisos).
- **Percentil 99 (P99)**: **47,14 m** (~15-16 pisos).
- **Altura máxima**: **91,56 m** (~29-30 pisos en el borde costero y plan de Viña del Mar / Valparaíso).
- **Estructuras > 15 m (media/alta altura)**: 6.321 (7,41%).
- **Estructuras > 30 m (torres / rascacielos costeros)**: 2.009 (2,36%).

### Archivos de evidencia generados
- `evidencia/datos/google_open_buildings_gran_valparaiso.json` (resumen estructurado con percentiles y sectores).
- `evidencia/datos/google_open_buildings_resumen.csv` (tabla comparativa por sector urbano).
- `evidencia/imagenes/grafico_google_open_buildings_alturas.png` (histograma continuo de alturas con anotaciones de tipologías).
- `evidencia/imagenes/comparativa_osm_vs_google_open_buildings.png` (gráfico de cobertura 24,1% vs 100% y perfiles por comuna).
- `evidencia/imagenes/mapa_google_open_buildings_2_5d.png` (mapa ráster espacial 2.5D de obstáculos de altura para drones).

## Para la Tarea 2: la sismicidad no debe tratarse como "excluir zona", sino como prioridad

Al diseñar el uso de cada amenaza en el grafo, se detectó una inconsistencia conceptual que hay que corregir antes de implementar el ruteo: no todas las amenazas deberían penalizar/eliminar aristas de la misma forma.

- **Foco de incendio activo (FIRMS) y probabilidad de ignición (CONAF)**: son un **peligro físico inmediato** para el dron y no aportan nada evaluar "desde adentro". Ahí sí corresponde penalizar/eliminar las aristas cercanas y recalcular una ruta alternativa (k-shortest-paths / pgr_KSP) que evite la zona.
- **Sismicidad reciente (USGS/CSN)**: es distinta porque **define el objetivo mismo de la misión** (evaluar daños post-terremoto). Tratarla como "excluir la zona" contradice el propósito completo del proyecto. Lo correcto es usarla para **priorizar hacia dónde volar primero** (mayor magnitud/recencia = mayor urgencia de evaluación), y penalizar únicamente **tramos puntuales con riesgo estructural derivado del sismo** (puentes, taludes potencialmente inestables) — no la zona completa.

Implicancia para el diseño del algoritmo de la Tarea 2: el peso/penalización de una arista no puede depender solo de "¿hay una amenaza cerca?", sino de si esa amenaza es del tipo "evitar" (incendio) o del tipo "priorizar con precaución puntual" (sismo). Conviene modelarlo como dos mecanismos separados en la función de costo del grafo, en vez de una única función de penalización genérica por cercanía a cualquier amenaza.

### Ampliación: antigüedad de la edificación como segundo factor de la prioridad sísmica

Se evaluó si existe una API que indique qué edificios cumplen la norma antisísmica (para estimar probabilidad de colapso). **No existe tal fuente pública en Chile** — esa información depende de permisos municipales (DOM) no digitalizados/abiertos de forma centralizada, por razones legales y de responsabilidad civil.

Se encontró en cambio un proxy real, parcial: **"Permisos de Edificación Georreferenciados en Chile 2010-2018"**, Feature Service público del Observatorio de Ciudades UC (mismo publicador que la Metadata #3), sin API key:
`https://services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Permisos_edificacion_2010_2018/FeatureServer`

**Resultado real**: de los 74.550 edificios del Gran Valparaíso (extracto OSM), solo **6.788 (9,1%)** tienen un permiso registrado en la ventana 2010-2018 (Valparaíso: 2.361, Viña del Mar: 1.193, Concón: 691, Quilpué: 1.397, Villa Alemana: 1.146). El 90,9% restante no tiene permiso en esa ventana — probablemente edificación más antigua, aunque el dato no distingue "antigua e incumple norma" de "con permiso anterior a 2010 o posterior a 2018"; **no se usa como probabilidad de colapso por edificio**, solo como indicador agregado de antigüedad relativa por zona.

**Propuesta de integración con la Amenaza #3 (sismicidad), sin tratarlo como probabilidad de colapso**:
1. **Prioridad de inspección post-sismo** = f(magnitud/recencia del sismo) × (1 + proporción de edificación sin permiso reciente en esa zona). A igual magnitud de sismo, una zona con más edificación antigua sube en la cola de prioridad de evaluación.
2. **Costo de arista condicionado a sismo activo**: cuando hay un sismo reciente relevante, las aristas que pasan por zonas con alta proporción de edificación antigua reciben un **costo adicional leve y condicional** por riesgo de escombros/obstrucción física de la calle — distinto de "evitar" (incendio) y de "priorizar puro" (sismo sin este factor), es una ponderación adicional, no una exclusión.

Esto queda como **propuesta de diseño para la Tarea 2**, no implementada aún — falta decidir el peso relativo (k) de este factor frente a magnitud/recencia del sismo.

## Corrección: Metadata #1 (viento) ahora se mide en 6 puntos, con dirección

La primera versión de `test_open_meteo.py` consultaba un único par de coordenadas (lat=-33.0472, lon=-71.6127) para representar el viento de **todo** el Gran Valparaíso, lo cual no era representativo: el viento varía bastante entre la costa y el interior.

**Se decidió medir en varios puntos** en vez de sacar la metadata. Se probó primero con 7 puntos (2 por Valparaíso y Viña del Mar, para separar plan/costa de cerros/interior, más 1 cada uno para Concón, Quilpué y Villa Alemana), pero se detectó que **Open-Meteo "engancha" cada coordenada consultada a la celda más cercana de la grilla de su modelo de pronóstico, que tiene una resolución real de ~11 km** (se verifica comparando la lat/lon pedida contra la que devuelve la respuesta). Con eso, el punto de Viña del Mar (costa) cayó en la misma celda que Concón, y el de Viña del Mar (interior) en la misma celda que Quilpué, devolviendo valores idénticos — no aportaban información nueva.

**Versión final: 6 puntos, todos en celdas de modelo distintas** — uno por comuna (Viña del Mar, Concón, Quilpué, Villa Alemana) más un punto extra en Valparaíso para distinguir plan/costa de cerros/interior alto (Placilla), donde la diferencia de altitud (15 m vs. 324 m) sí produce un cambio de viento real. Los puntos coinciden con cuarteles de Carabineros usados como nodo de origen/carga (ver sección siguiente). Además se agregó `wind_direction_10m` a la consulta (antes no se pedía).

**Los 6 puntos exactos consultados** (coordenadas pedidas; Open-Meteo luego las engancha a la celda de grilla más cercana, ver tabla de celdas más abajo):

| # | Punto | Lat | Lon | Referencia (cuartel de Carabineros) |
|---|---|---|---|---|
| 1 | Valparaíso (plan/costa) | -33.0488 | -71.6188 | Prefectura de Carabs. Valparaíso |
| 2 | Valparaíso (cerros/Placilla, interior alto) | -33.1147 | -71.5766 | Retén Placilla Peñuelas |
| 3 | Viña del Mar | -33.0192 | -71.5558 | Prefectura de Carabs. Viña del Mar |
| 4 | Concón | -32.9224 | -71.5129 | Subcom. Concón |
| 5 | Quilpué | -33.0553 | -71.4388 | 2da Com. Quilpué |
| 6 | Villa Alemana | -33.0433 | -71.3710 | 6ta Com. Villa Alemana |

Valparaíso aparece dos veces porque fue la única comuna donde se detectó una diferencia real de elevación que cae en celdas distintas del modelo; las demás quedaron con 1 punto cada una.

**Resultado real**:

| Punto | Elevación | Viento medio (km/h) | Racha media (km/h) | Racha máxima pronosticada (km/h) |
|---|---|---|---|---|
| Valparaíso (plan/costa) | 15 m | 12,3 | 31,0 | 52,2 |
| Valparaíso (cerros/Placilla) | 324 m | 10,4 | 27,7 | **55,4** |
| Viña del Mar | 9 m | 7,0 | 21,3 | 48,6 |
| Concón | 38 m | 6,8 | 18,4 | 40,3 |
| Quilpué | 131 m | 5,7 | 17,6 | 42,8 |
| Villa Alemana | 142 m | 4,2 | 13,1 | **32,0** |

Datos en `evidencia/datos/open_meteo_resumen_por_comuna.json` (incluye `direccion_10m` y la `celda_modelo` real devuelta por la API para cada punto), gráfico comparativo en `evidencia/imagenes/grafico_viento_por_comuna.png`.

**Limitación a declarar explícitamente**: 6 es, en la práctica, el límite de puntos distinguibles para el área del Gran Valparaíso con el modelo gratuito de Open-Meteo (~11 km de grilla). Pedir más puntos sin verificar contra la celda devuelta genera una falsa sensación de precisión (valores duplicados disfrazados de datos nuevos).

**El viento no solo debería penalizar por magnitud — también importa la dirección**: además de comparar la racha contra un umbral, el costo de una arista debería considerar el ángulo entre la dirección del viento (`direccion_10m`, en grados, de dónde sopla) y la orientación de esa calle. Viento de frente consume más batería y es más riesgoso que viento de cola o costado en el mismo tramo, lo que conecta directamente con la autonomía del dron y los puntos de carga en comisarías (sección siguiente): un tramo con viento en contra podría forzar una recarga antes de lo esperado.

**Implicancia para el algoritmo de la Tarea 2**: (1) cada arista toma el viento/dirección del punto más cercano, no un valor global; (2) el costo de la arista debe ser función de la magnitud *y* del ángulo relativo viento-calle, no solo de la magnitud.

## Nodo de origen y puntos de carga: Cuarteles de Carabineros

Se definió que el dron parte desde una **comisaría de Carabineros** (ruta sigue siendo de punto A a punto B: origen en la comisaría → zona de daño a evaluar), y que además **las comisarías/cuarteles sirven como puntos de carga** a lo largo de la ruta — si la autonomía de batería no alcanza para ir y volver en un solo viaje, el algoritmo puede incluir una parada en un cuartel cercano al camino para recargar, en vez de forzar siempre el regreso al origen.

**Fuente verificada**: dataset público de Carabineros de Chile (nivel nacional, 929 cuarteles), republicado como Feature Service ArcGIS, sin API key:
`https://services6.arcgis.com/LCdFQd7nnAn5xeUA/arcgis/rest/services/Cuarteles_Carabineros/FeatureServer/0`

**Resultado real para el Gran Valparaíso**: **29 cuarteles** con coordenadas (`test_carabineros.py`), de los cuales **9 son comisarías propiamente tales** (el resto son tenencias, subcomisarías y retenes):

| Comuna | Comisarías | Otros cuarteles |
|---|---|---|
| Valparaíso | 5 | 11 |
| Viña del Mar | 2 | 7 |
| Quilpué | 1 | 1 |
| Villa Alemana | 1 | 0 |
| Concón | 0 | 1 (solo subcomisaría) |

Datos en `evidencia/datos/carabineros_cuarteles_gran_valparaiso.geojson`, mapa en `evidencia/imagenes/mapa_carabineros_cuarteles.png` (`generar_mapa_carabineros.py`).

**Implicancia para el algoritmo de la Tarea 2**: a cada nodo del grafo que coincida con un cuartel se le agrega el atributo `es_punto_carga = true`. El ruteo sigue siendo A→B normal; ese atributo solo se usa como restricción adicional (ej. "si la distancia acumulada supera el rango de batería del dron, forzar una parada en el nodo de carga más cercano disponible dentro de la ruta").

## Archivos de evidencia

Ver `evidencia/` (o `codigo/evidencia/`): `open_meteo_response.json`, `overpass_response.json`, `usgs_response.json`, `conaf_probabilidad_ignicion.geojson`, `conaf_areas_protegidas.geojson`, `mapa_grafo_valparaiso.png`, `grafico_edificacion_valparaiso.png`, `overpass_local_edificacion.{json,csv}`, `google_open_buildings_gran_valparaiso.json`, `google_open_buildings_resumen.csv`, `grafico_google_open_buildings_alturas.png`, `comparativa_osm_vs_google_open_buildings.png`, `mapa_google_open_buildings_2_5d.png`.

