const map = L.map("map").setView([-33.03, -71.55], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const info = document.getElementById("info");

function cargarGeoJSON(url, callback) {
  fetch(url)
    .then((r) => r.json())
    .then(callback)
    .catch((err) => console.warn("No se pudo cargar", url, err));
}

// --- Ruta de ejemplo (pgr_dijkstra, costo = length_m, sin metadata/amenazas) ---
let capaRuta;
cargarGeoJSON("ruta_ejemplo.geojson", (geojson) => {
  capaRuta = L.geoJSON(geojson, {
    style: { color: "#2980b9", weight: 5, opacity: 0.85 },
  }).addTo(map);

  const meta = geojson.metadata;
  L.circleMarker([meta.origen.lat, meta.origen.lon], {
    radius: 9, color: "#000", fillColor: "#c0392b", fillOpacity: 1,
  }).addTo(map).bindPopup(`<b>Origen:</b> ${meta.origen.nombre} (${meta.origen.comuna})`);

  L.circleMarker([meta.destino.lat, meta.destino.lon], {
    radius: 9, color: "#000", fillColor: "#e67e22", fillOpacity: 1,
  }).addTo(map).bindPopup(`<b>Destino:</b> ${meta.destino.descripcion}`);

  info.innerHTML = `Ruta de ejemplo: ${meta.num_tramos} tramos, ` +
    `${(meta.distancia_total_m / 1000).toFixed(1)} km. ` +
    `Costo: ${meta.costo_usado}. Algoritmo: ${meta.algoritmo}.`;

  map.fitBounds(capaRuta.getBounds(), { padding: [40, 40] });
});

// --- Cuarteles de Carabineros (nodos de origen/carga) ---
let capaCarabineros;
cargarGeoJSON("data/carabineros.geojson", (geojson) => {
  capaCarabineros = L.geoJSON(geojson, {
    pointToLayer: (feature, latlng) => {
      const esComisaria = feature.properties.es_comisaria;
      return L.circleMarker(latlng, {
        radius: esComisaria ? 7 : 4,
        color: "#000",
        weight: 1,
        fillColor: esComisaria ? "#c0392b" : "#7f8c8d",
        fillOpacity: 0.9,
      });
    },
    onEachFeature: (feature, layer) => {
      const p = feature.properties;
      layer.bindPopup(`<b>${p.nombre}</b><br>${p.comuna}<br>` +
        `${p.es_comisaria ? "Comisaría" : "Otro cuartel"} · ` +
        `${p.es_punto_carga ? "Punto de carga" : ""}`);
    },
  }).addTo(map);
});

// --- Sismos (amenaza) ---
let capaSismos;
cargarGeoJSON("data/sismos.geojson", (geojson) => {
  capaSismos = L.geoJSON(geojson, {
    pointToLayer: (feature, latlng) => {
      const mag = feature.properties.magnitud || 1;
      return L.circleMarker(latlng, {
        radius: Math.max(3, mag * 2),
        color: "#000",
        weight: 0.5,
        fillColor: "#e67e22",
        fillOpacity: 0.6,
      });
    },
    onEachFeature: (feature, layer) => {
      const p = feature.properties;
      layer.bindPopup(`<b>M${p.magnitud}</b><br>${p.lugar}<br>${p.fecha}`);
    },
  }).addTo(map);
});

// --- Toggles del panel ---
document.getElementById("chk-ruta").addEventListener("change", (e) => {
  if (capaRuta) map[e.target.checked ? "addLayer" : "removeLayer"](capaRuta);
});
document.getElementById("chk-carabineros").addEventListener("change", (e) => {
  if (capaCarabineros) map[e.target.checked ? "addLayer" : "removeLayer"](capaCarabineros);
});
document.getElementById("chk-sismos").addEventListener("change", (e) => {
  if (capaSismos) map[e.target.checked ? "addLayer" : "removeLayer"](capaSismos);
});
