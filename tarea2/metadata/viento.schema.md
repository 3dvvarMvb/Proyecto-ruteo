# Estructura de `viento.json`

Metadata operacional de meteorología para los puntos clave del Gran Valparaíso (viento, rachas y dirección).

**Rol operacional:** Encarece el costo de las aristas del grafo vial según la velocidad y dirección del viento. Ráfagas sobre el umbral de 40 km/h comprometen la estabilidad aerodinámica y la autonomía del dron BVLOS.

**Fuente:** Open-Meteo API (`api.open-meteo.com/v1/forecast`), REST/JSON público sin API key.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador del punto de monitoreo |
| `comuna` | texto | Comuna (Valparaíso, Viña del Mar, Concón, Quilpué, Villa Alemana) |
| `sector` | texto | Detalle del sector geográfico (ej. `Plan / costa`, `Cerros / Placilla`) |
| `elevacion_m` | float | Altitud del punto sobre el nivel del mar (m) |
| `viento_medio_kmh` | float | Velocidad media del viento a 10m de altura (km/h) |
| `racha_media_kmh` | float | Velocidad media de ráfagas a 10m (km/h) |
| `racha_max_kmh` | float | Racha máxima registrada en el pronóstico (km/h) |
| `direccion_deg` | float | Dirección promedio del viento en grados (0° a 360°, de donde sopla) |
| `lon` | float | Longitud del punto (EPSG:4326) |
| `lat` | float | Latitud del punto (EPSG:4326) |

Ejemplo:
```json
{
  "id": 1,
  "comuna": "Valparaíso",
  "sector": "Plan / costa",
  "elevacion_m": 15.0,
  "viento_medio_kmh": 18.4,
  "racha_media_kmh": 28.2,
  "racha_max_kmh": 41.5,
  "direccion_deg": 210.5,
  "lon": -71.6188,
  "lat": -33.0488
}
```
