const MARITIME_CENTER = [6.4, 1.35];
let map, markersLayer, nasaOverlays = {};

const basemaps = {
  osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
  }),
  satellite: L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'Esri' },
  ),
  topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'OpenTopoMap',
  }),
};

function phColor(c) {
  return { red: '#c1121f', yellow: '#e9c46a', green: '#40916c' }[c] || '#666';
}

function initMap() {
  map = L.map('map', { center: MARITIME_CENTER, zoom: 9 });
  basemaps.osm.addTo(map);
  L.control.layers(
    { 'OpenStreetMap': basemaps.osm, 'Satellite': basemaps.satellite, 'Topographique': basemaps.topo },
  ).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
  loadSoilPoints();
  loadNasaToggles();
}

async function loadSoilPoints() {
  const params = new URLSearchParams({ light: '1' });
  const phMin = document.getElementById('filter-ph-min')?.value;
  const phMax = document.getElementById('filter-ph-max')?.value;
  const soilType = document.getElementById('filter-soil-type')?.value;
  if (phMin) params.set('ph_min', phMin);
  if (phMax) params.set('ph_max', phMax);
  if (soilType) params.set('soil_type', soilType);
  const data = await SigSolsAPI.api('/points/?' + params);
  markersLayer.clearLayers();
  const list = data.results || (Array.isArray(data) ? data : data.features || []);
  list.forEach((props) => {
    const coords = [props.lon, props.lat];
    const color = phColor(props.ph_color);
    const marker = L.circleMarker([coords[1], coords[0]], {
      radius: 7,
      fillColor: color,
      color: '#333',
      weight: 1,
      fillOpacity: 0.85,
    });
    marker.bindPopup(`
      <strong>Point #${props.id}</strong><br/>
      pH: ${props.ph} · Humidité: ${props.humidity_pct}%<br/>
      Type: ${props.soil_type}<br/>
      NDVI: ${props.ndvi_3m_avg ?? '—'} · SMAP: ${props.smap_moisture_avg ?? '—'}<br/>
      <button onclick="predictAtPoint(${props.ph}, ${props.humidity_pct}, '${props.soil_type}')">Prédire fertilité</button>
    `);
    markersLayer.addLayer(marker);
  });
}

async function loadNasaToggles() {
  const summary = await SigSolsAPI.api('/nasa/catalog/summary/');
  const container = document.getElementById('nasa-layers-toggles');
  container.innerHTML = '';
  (summary.by_product || []).forEach((p) => {
    const label = document.createElement('label');
    label.innerHTML = `<input type="checkbox" data-product="${p.product}" /> ${p.product} (${p.count})`;
    label.querySelector('input').addEventListener('change', (e) => toggleNasaLayer(p.product, e.target.checked));
    container.appendChild(label);
  });
}

function toggleNasaLayer(product, on) {
  if (on && !nasaOverlays[product]) {
    const today = new Date().toISOString().slice(0, 10);
    nasaOverlays[product] = L.tileLayer(
      `${window.location.origin}/api/v1/nasa/tiles/${product}/${today}/{z}/{x}/{y}.png`,
      { opacity: 0.35 },
    ).addTo(map);
  } else if (!on && nasaOverlays[product]) {
    map.removeLayer(nasaOverlays[product]);
    delete nasaOverlays[product];
  }
}

window.predictAtPoint = async (ph, humidity, soilType) => {
  document.getElementById('pred-ph').value = ph;
  document.getElementById('pred-humidity').value = humidity;
  document.getElementById('pred-soil-type').value = soilType;
  await runPrediction();
};

async function runPrediction() {
  const body = {
    ph: parseFloat(document.getElementById('pred-ph').value),
    humidity_pct: parseFloat(document.getElementById('pred-humidity').value),
    soil_type: document.getElementById('pred-soil-type').value,
  };
  const r = await SigSolsAPI.api('/ml/predict/', { method: 'POST', body: JSON.stringify(body) });
  document.getElementById('pred-result').textContent = JSON.stringify(r, null, 2);
}

window.SigSolsMap = { initMap, loadSoilPoints, runPrediction };
