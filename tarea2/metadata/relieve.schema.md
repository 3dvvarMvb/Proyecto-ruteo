# Estructura de `relieve.json`

Metadata operacional de pendiente del terreno y relieve (desnivel) sobre aristas del grafo vial del Gran Valparaíso.

**Rol operacional:** Valparaíso se caracteriza por una topografía de cerros empinados. Aristas con pendientes pronunciadas (>10%) demandan mayor consumo energético, provocan turbulencia orográfica y degradan la línea de vista del enlace de comando y control (C2), por lo que encarecen el costo de la trayectoria.

**Fuente:** Open Topo Data API (`api.opentopodata.org/v1/srtm90m`, dataset SRTM 90m), sin API key.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Identificador secuencial del registro |
| `source` | entero | Nodo de origen de la arista (`u`) |
| `target` | entero | Nodo de destino de la arista (`v`) |
| `elev_u_m` | float | Elevación sobre el nivel del mar en el nodo de origen (metros) |
| `elev_v_m` | float | Elevación sobre el nivel del mar en el nodo de destino (metros) |
| `desnivel_m` | float | Diferencia absoluta de altitud entre nodos (metros) |
| `pendiente_pct` | float | Pendiente longitudinal de la vía ($\frac{\text{desnivel}}{\text{longitud}} \times 100$) en porcentaje |

Ejemplo:
```json
{
  "id": 1,
  "source": 292188928,
  "target": 292188908,
  "elev_u_m": 170.0,
  "elev_v_m": 176.0,
  "desnivel_m": 6.0,
  "pendiente_pct": 13.8
}
```
