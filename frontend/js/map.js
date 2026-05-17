import { phColorHex } from './core/phColor.js';
import {
  MARITIME_CENTER,
  buildSoilFiltersQuery,
  markerStyleForPoint,
  nasaTileUrl,
  parseSoilPointsList,
} from './core/mapUtils.js';

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
  return phColorHex(c);
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
  const query = buildSoilFiltersQuery({
    phMin: document.getElementById('filter-ph-min')?.value,
    phMax: document.getElementById('filter-ph-max')?.value,
    soilType: document.getElementById('filter-soil-type')?.value,
  });
  const data = await SigSolsAPI.api('/points/?' + query);
  markersLayer.clearLayers();
  parseSoilPointsList(data).forEach((props) => {
    const coords = [props.lon, props.lat];
    const style = markerStyleForPoint(props);
    const marker = L.circleMarker([coords[1], coords[0]], style);
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
      nasaTileUrl(window.location.origin, product, today),
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
