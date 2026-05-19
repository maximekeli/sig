/**
 * Parcelles — sélection sur carte, liste, infos en temps réel.
 */
import { notifyError } from './core/ui.js';

let drawControl = null;
let drawnLayer = null;
let parcelHighlight = null;
let parcelsLayer = null;
let liveDebounce = null;
let selectedParcelCode = null;
let selectedGeometry = null;
let refreshInFlight = false;

const VULN_COLORS = {
  faible: '#2d8a52',
  moyenne: '#e9a319',
  elevee: '#dc2626',
  degraded: '#dc2626',
  canton: '#c9a962',
};

const ZONE_STYLES = {
  canton: { color: '#c9a962', weight: 2, fillOpacity: 0.08 },
  degraded: { color: '#dc2626', weight: 2, fillOpacity: 0.12, dashArray: '6' },
  default: { color: '#2d8a52', weight: 1.5, fillOpacity: 0.06 },
};

function getMap() {
  return window.SigSolsMap?.getMap?.();
}

function isLiveEnabled() {
  return document.getElementById('parcel-live-update')?.checked !== false;
}

function clearParcelLayers() {
  const map = getMap();
  if (!map) return;
  if (parcelHighlight) {
    map.removeLayer(parcelHighlight);
    parcelHighlight = null;
  }
}

function clearDrawnOnly() {
  if (drawnLayer) drawnLayer.clearLayers();
}

function initDrawControl() {
  const map = getMap();
  if (!map || typeof L.Control.Draw === 'undefined') return;

  drawnLayer = new L.FeatureGroup().addTo(map);

  drawControl = new L.Control.Draw({
    draw: {
      polyline: false,
      circle: false,
      circlemarker: false,
      marker: false,
      rectangle: { shapeOptions: { color: '#c9a962', weight: 2 } },
      polygon: {
        allowIntersection: false,
        shapeOptions: { color: '#c9a962', weight: 2, fillOpacity: 0.15 },
      },
    },
    edit: { featureGroup: drawnLayer, remove: true },
  });
  map.addControl(drawControl);

  const onDrawChange = () => {
    selectedParcelCode = null;
    const sel = document.getElementById('parcel-zone-select');
    if (sel) sel.value = '';
    selectedGeometry = getDrawnGeometry();
    setParcelStatus('Parcelle dessinée — mise à jour des indicateurs…');
    scheduleLiveRefresh();
  };

  map.on(L.Draw.Event.CREATED, (e) => {
    drawnLayer.clearLayers();
    drawnLayer.addLayer(e.layer);
    onDrawChange();
  });

  map.on(L.Draw.Event.EDITED, onDrawChange);
  map.on(L.Draw.Event.DELETED, () => {
    selectedGeometry = null;
    hideLivePanel();
    setParcelStatus('Sélection effacée.');
  });
}

function setParcelStatus(msg) {
  const el = document.getElementById('parcel-status');
  if (el) el.textContent = msg;
}

function getDrawnGeometry() {
  if (!drawnLayer) return null;
  const layers = drawnLayer.getLayers();
  if (!layers.length) return null;
  return layers[0].toGeoJSON().geometry;
}

function scheduleLiveRefresh() {
  if (!isLiveEnabled()) return;
  clearTimeout(liveDebounce);
  liveDebounce = setTimeout(() => refreshLiveParcelInfo(false), 600);
}

async function loadZonesSelect() {
  const select = document.getElementById('parcel-zone-select');
  if (!select) return;
  try {
    const data = await SigSolsAPI.api('/spatial/parcel/zones/?zone_type=canton');
    select.innerHTML = '<option value="">— Cliquer sur la carte ou dessiner —</option>';
    (data.zones || []).forEach((z) => {
      const opt = document.createElement('option');
      opt.value = z.code;
      opt.textContent = `${z.name} (${z.code})`;
      select.appendChild(opt);
    });
    const deg = await SigSolsAPI.api('/spatial/parcel/zones/?zone_type=degraded');
    if (deg.zones?.length) {
      const grp = document.createElement('optgroup');
      grp.label = 'Zones dégradées';
      deg.zones.forEach((z) => {
        const opt = document.createElement('option');
        opt.value = z.code;
        opt.textContent = `${z.name} (${z.code})`;
        grp.appendChild(opt);
      });
      select.appendChild(grp);
    }
    renderParcelList();
  } catch {
    select.innerHTML = '<option value="">Zones non chargées</option>';
  }
}

function renderParcelList() {
  const ul = document.getElementById('parcel-list');
  const select = document.getElementById('parcel-zone-select');
  if (!ul || !select) return;
  ul.innerHTML = '';
  [...select.options].forEach((opt) => {
    if (!opt.value) return;
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'parcel-list-btn';
    btn.textContent = opt.textContent;
    btn.dataset.code = opt.value;
    if (opt.value === selectedParcelCode) btn.classList.add('active');
    btn.addEventListener('click', () => selectParcelByCode(opt.value));
    li.appendChild(btn);
    ul.appendChild(li);
  });
}

async function loadParcelsOnMap() {
  const map = getMap();
  if (!map) return;
  const show = document.getElementById('parcel-show-on-map')?.checked !== false;
  if (parcelsLayer) {
    map.removeLayer(parcelsLayer);
    parcelsLayer = null;
  }
  if (!show) return;

  try {
    const geojson = await SigSolsAPI.api('/spatial/parcel/zones/geojson/?types=canton,degraded');
    parcelsLayer = L.geoJSON(geojson, {
      style: (f) => {
        const t = f.properties?.zone_type || 'canton';
        const base = ZONE_STYLES[t] || ZONE_STYLES.default;
        const selected = f.properties?.code === selectedParcelCode;
        return {
          ...base,
          weight: selected ? 4 : base.weight,
          fillOpacity: selected ? 0.28 : base.fillOpacity,
          color: selected ? '#3b82f6' : base.color,
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties || {};
        layer.bindTooltip(`${p.name} (${p.code})`, { sticky: true });
        layer.on('click', (e) => {
          L.DomEvent.stopPropagation(e);
          selectParcelByCode(p.code, feature.geometry);
        });
      },
    }).addTo(map);
  } catch (e) {
    console.warn('Parcelles GeoJSON', e);
  }
}

function selectParcelByCode(code, geometry = null) {
  selectedParcelCode = code;
  selectedGeometry = geometry;
  clearDrawnOnly();
  const sel = document.getElementById('parcel-zone-select');
  if (sel) sel.value = code;
  renderParcelList();
  setParcelStatus(`Parcelle « ${code} » — chargement…`);
  if (parcelsLayer) {
    parcelsLayer.eachLayer((layer) => {
      const c = layer.feature?.properties?.code;
      const t = layer.feature?.properties?.zone_type;
      const base = ZONE_STYLES[t] || ZONE_STYLES.default;
      layer.setStyle({
        ...base,
        weight: c === code ? 4 : base.weight,
        fillOpacity: c === code ? 0.28 : base.fillOpacity,
        color: c === code ? '#3b82f6' : base.color,
      });
    });
  }
  scheduleLiveRefresh();
}

function highlightParcel(geojson, vulnerabilityLevel) {
  const map = getMap();
  if (!map || !geojson) return;
  if (parcelHighlight) map.removeLayer(parcelHighlight);
  const color = VULN_COLORS[vulnerabilityLevel] || VULN_COLORS.moyenne;
  parcelHighlight = L.geoJSON(geojson, {
    style: { color, weight: 3, fillColor: color, fillOpacity: 0.22 },
  }).addTo(map);
  try {
    map.fitBounds(parcelHighlight.getBounds(), { padding: [48, 48], maxZoom: 14 });
  } catch {
    /* ignore */
  }
}

function formatLivePanelHtml(data, { loading = false } = {}) {
  if (loading) {
    return '<p class="parcel-live-loading">Mise à jour en cours…</p>';
  }
  const sp = data.soil_points || {};
  const nasa = data.nasa || {};
  const vuln = data.vulnerability || {};
  const ml = data.ml_prediction || {};
  const ndviLabel = {
    stress_severe: 'Stress sévère',
    stress_modere: 'Stress modéré',
    vegetation_moyenne: 'Végétation moyenne',
    vegetation_vigoureuse: 'Végétation vigoureuse',
    donnees_manquantes: '—',
  };
  const updated = data.analyzed_at
    ? new Date(data.analyzed_at).toLocaleTimeString('fr-FR')
    : '—';

  return `
    <div class="parcel-live-inner parcel-live-inner--${vuln.level || 'moyenne'}">
      <h4>${data.parcel_name || 'Parcelle'}</h4>
      <p class="parcel-live-meta">${data.area?.area_ha ?? '—'} ha · ${sp.count ?? 0} pts sol</p>
      <div class="parcel-live-grid">
        <div><span>pH</span><strong>${sp.avg_ph ?? '—'}</strong></div>
        <div><span>NDVI</span><strong>${sp.avg_ndvi ?? nasa.avg_ndvi ?? '—'}</strong></div>
        <div><span>SMAP</span><strong>${sp.avg_smap ?? nasa.avg_smap ?? '—'}</strong></div>
        <div><span>Vuln.</span><strong>${vuln.level ?? '—'}</strong></div>
      </div>
      <p class="parcel-live-nasa">${ndviLabel[nasa.ndvi_status] || '—'}</p>
      ${ml.predicted_class ? `<p class="parcel-live-ml">IA : <strong>${ml.predicted_class}</strong></p>` : ''}
      <p class="parcel-live-time">Mis à jour : ${updated}</p>
    </div>`;
}

function showLivePanel(html) {
  const panel = document.getElementById('parcel-live-panel');
  const content = document.getElementById('parcel-live-content');
  if (content) content.innerHTML = html;
  panel?.classList.remove('hidden');
}

function hideLivePanel() {
  document.getElementById('parcel-live-panel')?.classList.add('hidden');
}

async function refreshLiveParcelInfo(fullAnalysis = false) {
  const zoneCode = selectedParcelCode || document.getElementById('parcel-zone-select')?.value;
  const geometry = zoneCode ? null : (selectedGeometry || getDrawnGeometry());

  if (!zoneCode && !geometry) {
    hideLivePanel();
    return;
  }
  if (refreshInFlight) return;
  refreshInFlight = true;

  showLivePanel(formatLivePanelHtml({}, { loading: true }));

  const useMl = fullAnalysis || document.getElementById('parcel-use-ml')?.checked === true;

  try {
    let data;
    if (zoneCode && !fullAnalysis && !useMl) {
      data = await SigSolsAPI.api(
        `/spatial/parcel/live/?zone_code=${encodeURIComponent(zoneCode)}&use_ml=0`,
      );
    } else {
      const body = { use_ml: useMl };
      if (zoneCode) body.zone_code = zoneCode;
      else body.geometry = geometry;
      data = await SigSolsAPI.api('/spatial/parcel/live/', {
        method: 'POST',
        body: JSON.stringify(body),
      });
    }

    showLivePanel(formatLivePanelHtml(data));
    highlightParcel(data.geometry_geojson, data.vulnerability?.level);
    renderAnalysisResult(data);
    setParcelStatus(`Parcelle active — ${data.parcel_name || zoneCode || 'dessinée'}`);
  } catch (e) {
    notifyError(e);
    setParcelStatus('Erreur : ' + (e.message || 'impossible'));
    showLivePanel(`<p class="parcel-error">${e.message}</p>`);
  } finally {
    refreshInFlight = false;
  }
}

function renderAnalysisResult(data) {
  const box = document.getElementById('parcel-analysis-result');
  if (!box) return;

  const sp = data.soil_points || {};
  const nasa = data.nasa || {};
  const vuln = data.vulnerability || {};
  const ml = data.ml_prediction || {};

  const ndviLabel = {
    stress_severe: 'Stress sévère',
    stress_modere: 'Stress modéré',
    vegetation_moyenne: 'Végétation moyenne',
    vegetation_vigoureuse: 'Végétation vigoureuse',
    donnees_manquantes: 'Données manquantes',
  };
  const smapLabel = {
    secheresse_probable: 'Sécheresse probable',
    humidite_faible: 'Humidité faible',
    humidite_moyenne: 'Humidité moyenne',
    humidite_bonne: 'Humidité bonne',
    donnees_manquantes: 'Données manquantes',
  };

  box.classList.remove('hidden');
  box.innerHTML = `
    <div class="parcel-report parcel-report--${vuln.level || 'moyenne'}">
      <h4>${data.parcel_name || 'Parcelle'}</h4>
      <p class="parcel-meta">
        ${data.area?.area_ha ?? '—'} ha ·
        ${sp.count ?? 0} point(s) sol ·
        Vulnérabilité <strong>${vuln.level || '—'}</strong>
      </p>
      <div class="parcel-metrics">
        <span>pH moy. <strong>${sp.avg_ph ?? '—'}</strong></span>
        <span>NDVI <strong>${sp.avg_ndvi ?? nasa.avg_ndvi ?? '—'}</strong></span>
        <span>SMAP <strong>${sp.avg_smap ?? nasa.avg_smap ?? '—'}</strong></span>
        <span>Humid. <strong>${sp.avg_humidity_pct ?? '—'}%</strong></span>
      </div>
      <p class="parcel-nasa">
        NASA : ${ndviLabel[nasa.ndvi_status] || '—'} · ${smapLabel[nasa.smap_status] || '—'}
      </p>
      ${ml.predicted_class ? `
        <p class="parcel-ml">
          IA fertilité : <strong>${ml.predicted_class}</strong>
          (confiance ${Math.round((ml.confidence || 0) * 100)}%)
        </p>
      ` : ''}
      ${(data.recommendations || []).length ? `
        <ul class="parcel-recs">
          ${data.recommendations.map((r) => `<li>${r}</li>`).join('')}
        </ul>
      ` : ''}
    </div>
  `;
}

async function runParcelAnalysis() {
  const zoneCode = document.getElementById('parcel-zone-select')?.value;
  if (zoneCode) selectedParcelCode = zoneCode;
  selectedGeometry = zoneCode ? null : getDrawnGeometry();

  if (!selectedParcelCode && !selectedGeometry) {
    notifyError({ message: 'Sélectionnez ou dessinez une parcelle.' });
    return;
  }

  setParcelStatus('Analyse complète en cours…');
  await refreshLiveParcelInfo(true);
}

function onZoneSelectChange() {
  const code = document.getElementById('parcel-zone-select')?.value;
  if (code) selectParcelByCode(code);
  else {
    selectedParcelCode = null;
    hideLivePanel();
    clearParcelLayers();
    setParcelStatus('Sélectionnez une parcelle.');
  }
}

function clearParcelSelection() {
  selectedParcelCode = null;
  selectedGeometry = null;
  document.getElementById('parcel-zone-select').value = '';
  clearDrawnOnly();
  clearParcelLayers();
  hideLivePanel();
  const box = document.getElementById('parcel-analysis-result');
  if (box) {
    box.classList.add('hidden');
    box.innerHTML = '';
  }
  renderParcelList();
  loadParcelsOnMap();
  setParcelStatus('Sélection effacée.');
}

function initParcelTools() {
  initDrawControl();
  loadZonesSelect();
  loadParcelsOnMap();

  document.getElementById('btn-parcel-analyze')?.addEventListener('click', runParcelAnalysis);
  document.getElementById('btn-parcel-clear')?.addEventListener('click', clearParcelSelection);
  document.getElementById('parcel-zone-select')?.addEventListener('change', onZoneSelectChange);
  document.getElementById('parcel-show-on-map')?.addEventListener('change', loadParcelsOnMap);
  document.getElementById('parcel-live-update')?.addEventListener('change', () => {
    if (isLiveEnabled()) scheduleLiveRefresh();
  });
  document.getElementById('parcel-live-close')?.addEventListener('click', hideLivePanel);

  setInterval(() => {
    if (isLiveEnabled() && (selectedParcelCode || selectedGeometry || getDrawnGeometry())) {
      refreshLiveParcelInfo(false);
    }
  }, 45000);

  setParcelStatus('Cliquez sur une parcelle ou dessinez un polygone.');
}

window.SigSolsParcel = {
  initParcelTools,
  loadZonesSelect,
  loadParcelsOnMap,
  runParcelAnalysis,
  clearParcelSelection,
  selectParcelByCode,
  refreshLiveParcelInfo,
};
