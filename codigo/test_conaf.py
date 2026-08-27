"""Amenaza 2 (reemplazo de SENAPRED) - CONAF, pronostico de riesgo de incendios.

Hallazgo: la pagina https://www.conaf.cl/incendios/situacion-actual-y-pronostico-de-incendios/
enlaza un dashboard ArcGIS Online publico (item "Pronostico de Riesgo",
id 06a31e138f5c40efbd577c1993154ce5, owner deigeprif, access=public).
Ese dashboard consume, entre otros, dos Feature Services REST publicos y
sin API key:

  - PI/FeatureServer/4   -> poligonos de probabilidad de ignicion a 5 dias
                            (capa "d4_20260830_PI": pronostico dia+4)
  - ASP/FeatureServer/0  -> poligonos de Areas Silvestres Protegidas (SNASPE)

Esto es MEJOR que lo que asumia el informe original (SENAPRED como
"portal institucional" sin API real): es un servicio REST de ArcGIS,
publico, con geometrias de poligono listas para ST_Intersects en PostGIS.
"""
import json
import requests

BBOX_VALPARAISO = "-72.0,-33.5,-71.2,-32.7"  # west,south,east,north (WGS84)

def query_layer(nombre, url, where="1=1", out_fields="*"):
    params = {
        "where": where,
        "outFields": out_fields,
        "geometry": BBOX_VALPARAISO,
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnGeometry": "true",
        "f": "geojson",
    }
    resp = requests.get(url + "/query", params=params, timeout=25)
    resp.raise_for_status()
    data = resp.json()
    feats = data.get("features", [])
    print(f"\n=== {nombre} ===")
    print("HTTP", resp.status_code, "| features:", len(feats))
    for f in feats[:5]:
        print(" ", f["properties"])
    with open(f"evidencia/conaf_{nombre}.geojson", "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    print(f"Guardado en evidencia/conaf_{nombre}.geojson")
    return data


# 1) Pronostico de riesgo de ignicion (poligonos, actualizado diariamente)
query_layer(
    "probabilidad_ignicion",
    "https://services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/PI/FeatureServer/4",
    out_fields="FID,count_,label",
)

# 2) Areas Silvestres Protegidas (poligonos de exclusion/restriccion para RPAS)
query_layer(
    "areas_protegidas",
    "https://services5.arcgis.com/A1ELWse9bRAi2JiV/arcgis/rest/services/ASP/FeatureServer/0",
    where="region = 'Valparaíso'",
    out_fields="nom_min,region,categoria,sup_ha",
)

print("\nOK: ambos Feature Services de CONAF responden con geometrias de poligono reales.")
