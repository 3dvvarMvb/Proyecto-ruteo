# Estructura de `permisos_edificacion.json`

Puntos georreferenciados de permisos de edificación otorgados entre 2010-2018 en las 5 comunas del Gran Valparaíso.

**Rol operacional:** Proxy parcial de antigüedad relativa de la edificación por zona (NO probabilidad de colapso ni cumplimiento de norma antisísmica — ese dato no existe público en Chile). Zonas con poca densidad de permisos recientes tienden a tener edificación más antigua, lo que en un escenario post-sismo aumenta el riesgo de escombros/obstrucción de calles. Amplía la Amenaza #3 (sismicidad): ver `codigo/RESULTADOS.md`, sección "Ampliación: antigüedad de la edificación como segundo factor de la prioridad sísmica".

**Cómo se usa en Tarea 2:** se vincula espacialmente a las manzanas censales de `metadata_poblacion` (ver `cargar_permisos_edificacion.py`), que calcula ahí un `indice_antiguedad` por manzana. Ese índice penaliza levemente (y solo de forma condicional, cuando el destino de la ruta es un sismo) las aristas que cruzan zonas de edificación antigua, en `sitio_web/generar_rutas_comparativas.py`.

**Limitación declarada:** "sin permiso en la ventana 2010-2018" no es lo mismo que "edificación antigua e incumple la norma" — podría tener un permiso anterior a 2010 o posterior a 2018. Por eso nunca se usa como probabilidad de colapso por edificio individual, solo como indicador agregado y relativo por zona.

**Fuente:** "Permisos de Edificación Georreferenciados en Chile 2010-2018", Feature Service público del Observatorio de Ciudades UC (`services9.arcgis.com/kKJR3Qt68ohAWuet/arcgis/rest/services/Permisos_edificacion_2010_2018/FeatureServer/0`), sin API key. Mismo publicador que la Metadata de población (Censo 2017). Verificado ya en Tarea 1 (`codigo/test_permisos_edificacion.py`), ahí solo como conteo agregado por comuna; en Tarea 2 se extraen los puntos individuales para poder vincularlos a manzanas.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial del permiso |
| `comuna` | texto | Comuna donde se otorgó el permiso |
| `anio` | entero | Año de otorgamiento (2010-2018) |
| `num_pisos` | entero | Número de pisos de la edificación permisada |
| `superficie_m2` | float | Superficie construida en m² |
| `lon` | float | Longitud del punto (EPSG:4326) |
| `lat` | float | Latitud del punto (EPSG:4326) |

Ejemplo:
```json
{
  "id": 1,
  "comuna": "Valparaíso",
  "anio": 2015,
  "num_pisos": 3,
  "superficie_m2": 140,
  "lon": -71.6297714,
  "lat": -33.0396450991372
}
```

Total extraído: 6.788 permisos (Valparaíso: 2.361, Viña del Mar: 1.193, Concón: 691, Quilpué: 1.397, Villa Alemana: 1.146) — coincide con el conteo agregado verificado en Tarea 1.
