# Estructura de `firms.json`

Detecciones satelitales de focos de calor / incendios forestales activos (sensores MODIS y VIIRS).

**Rol operacional:** Amenaza de corte inmediato. El fuego y las columnas de humo reducen la visibilidad a cero, alteran la densidad del aire e introducen restricciones temporales (NOTAM) por combate aéreo de brigadas terrestres y aviones cisterna. El algoritmo penaliza severamente o excluye mediante un buffer de 500 metros las aristas cercanas (`ST_DWithin`).

**Fuente:** NASA FIRMS API (`firms.modaps.eosdis.nasa.gov`), producto VIIRS NRT. Requiere `FIRMS_MAP_KEY`. Cuenta con respaldo offline si la clave no está configurada en el entorno.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial del foco de calor |
| `fecha` | texto | Fecha de adquisición satelital (`YYYY-MM-DD`) |
| `confianza` | texto | Nivel de confianza de la detección (`n`: normal, `h`: alta, `l`: baja) |
| `frp` | float | Potencia radiativa del fuego (*Fire Radiative Power*, en MW) |
| `dentro_chile` | booleano | Si el foco está dentro del polígono territorial de Chile (filtro `ST_Intersects`) |
| `lon` | float | Longitud del foco (EPSG:4326) |
| `lat` | float | Latitud del foco (EPSG:4326) |

Ejemplo:
```json
{
  "id": 1,
  "fecha": "2026-08-26",
  "confianza": "n",
  "frp": 4.84,
  "dentro_chile": true,
  "lon": -68.88385,
  "lat": -22.31757
}
```
