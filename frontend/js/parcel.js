/**
 * Parcelles — sélection, recherche, points de sol, panneau temps réel enrichi.
 */
import { phColorHex } from './core/phColor.js';
import { notifyError, notifySuccess } from './core/ui.js';
import { trackActivity } from './core/activityTracker.js';
import {
  NDVI_LABELS,
  SMAP_LABELS,
  VULN_COLORS,
  ZONE_STYLES,
  healthClass,
  vulnLabel,
} from './core/parcelUtils.js';
import {
  formatParcelExternalGrid,
  saveLastParcelToStorage,
} from './core/parcelExternal.js';
import {
  clearSentinelParcelSummary,
  displaySentinelParcelSummary,
  formatSentinelHtml,
} from './sentinelMap.js';
import {
  clearWeatherParcelSummary,
  displayWeatherParcelSummary,
  formatWeatherHtml,
} from './weatherMap.js';

let drawControl = null;
let drawnLayer = null;
let parcelHighlight = null;
let parcelsLayer = null;
let parcelSoilLayer = null;
let liveDebounce = null;
let liveInterval = null;
let selectedParcelCode = null;
let selectedGeometry = null;
let liveRequestSeq = 0;
let shouldFitBounds = true;
let lastParcelData = null;
let allZones = [];
let parcelFilter = 'all';
let zonesGeoJsonCache = null;

function getMap() {
  return window.SigSolsMap?.getMap?.();
}

function isLiveEnabled() {
  return document.getElementById('parcel-live-update')?.checked !== false;
}

function showSoilPointsOnMap() {
  return document.getElementById('parcel-show-soil-points')?.checked !== false;
}

function resetParcelDiagnostics() {
  clearSentinelParcelSummary();
  clearWeatherParcelSummary();
  saveLastParcelToStorage(null);
  window.dispatchEvent(new CustomEvent('sig-sols-parcel-cleared'));
}

function clearParcelLayers() {
  const map = getMap();
  if (!map) return;
  if (parcelHighlight) {
    map.removeLayer(parcelHighlight);
    parcelHighlight = null;
  }
  if (parcelSoilLayer) {
    map.removeLayer(parcelSoilLayer);
    parcelSoilLayer = null;
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
    shouldFitBounds = true;
    setParcelStatus('Parcelle dessinée — analyse…');
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
    lastParcelData = null;
    resetParcelDiagnostics();
    hideLivePanel();
    clearParcelLayers();
    const box = document.getElementById('parcel-analysis-result');
    if (box) {
      box.classList.add('hidden');
      box.innerHTML = '';
    }
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
  liveDebounce = setTimeout(() => refreshLiveParcelInfo(false), 500);
}

async function loadZonesSelect() {
  const select = document.getElementById('parcel-zone-select');
  if (!select) return;
  try {
    const [cantons, degraded] = await Promise.all([
      SigSolsAPI.api('/spatial/parcel/zones/?zone_type=canton'),
      SigSolsAPI.api('/spatial/parcel/zones/?zone_type=degraded'),
    ]);
    allZones = [
      ...(cantons.zones || []).map((z) => ({ ...z, zone_type: 'canton' })),
      ...(degraded.zones || []).map((z) => ({ ...z, zone_type: 'degraded' })),
    ];
    rebuildZoneSelect();
    renderParcelList();
  } catch {
    select.innerHTML = '<option value="">Zones non chargées</option>';
  }
}

function rebuildZoneSelect() {
  const select = document.getElementById('parcel-zone-select');
  if (!select) return;
  const current = select.value;
  select.innerHTML = '<option value="">— Cliquer sur la carte ou dessiner —</option>';
  const filtered = allZones.filter((z) => {
    if (parcelFilter === 'all') return true;
    return z.zone_type === parcelFilter;
  });
  const cantons = filtered.filter((z) => z.zone_type === 'canton');
  const degraded = filtered.filter((z) => z.zone_type === 'degraded');
  cantons.forEach((z) => {
    const opt = document.createElement('option');
    opt.value = z.code;
    opt.textContent = `${z.name} (${z.code})`;
    opt.dataset.zoneType = z.zone_type;
    select.appendChild(opt);
  });
  if (degraded.length) {
    const grp = document.createElement('optgroup');
    grp.label = 'Zones dégradées';
    degraded.forEach((z) => {
      const opt = document.createElement('option');
      opt.value = z.code;
      opt.textContent = `${z.name} (${z.code})`;
      opt.dataset.zoneType = z.zone_type;
      grp.appendChild(opt);
    });
    select.appendChild(grp);
  }
  if ([...select.options].some((o) => o.value === current)) select.value = current;
}

function getFilteredZones() {
  const q = document.getElementById('parcel-search')?.value?.trim().toLowerCase() || '';
  return allZones.filter((z) => {
    if (parcelFilter !== 'all' && z.zone_type !== parcelFilter) return false;
    if (!q) return true;
    return z.name.toLowerCase().includes(q) || z.code.toLowerCase().includes(q);
  });
}

function renderParcelList() {
  const ul = document.getElementById('parcel-list');
  if (!ul) return;
  ul.innerHTML = '';
  getFilteredZones().forEach((z) => {
    const li = document.createElement('li');
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'parcel-list-btn';
    if (z.zone_type === 'degraded') btn.classList.add('parcel-list-btn--degraded');
    btn.textContent = `${z.name} (${z.code})`;
    btn.dataset.code = z.code;
    if (z.code === selectedParcelCode) btn.classList.add('active');
    btn.addEventListener('click', () => selectParcelByCode(z.code));
    li.appendChild(btn);
    ul.appendChild(li);
  });
  if (!ul.children.length) {
    ul.innerHTML = '<li class="parcel-empty">Aucune parcelle trouvée</li>';
  }
}

function styleForZoneFeature(f, selected) {
  const t = f.properties?.zone_type || 'canton';
  const base = ZONE_STYLES[t] || ZONE_STYLES.default;
  if (selected) {
    return { color: '#3b82f6', weight: 4, fillOpacity: 0.3, dashArray: null };
  }
  return { ...base };
}

async function loadParcelsOnMap() {
  const map = getMap();
  if (!map) return;
  const show = document.getElementById('parcel-show-on-map')?.checked !== false;
  document.getElementById('parcel-map-legend')?.classList.toggle('hidden', !show);

  if (parcelsLayer) {
    map.removeLayer(parcelsLayer);
    parcelsLayer = null;
  }
  if (!show) return;

  try {
    if (!zonesGeoJsonCache) {
      zonesGeoJsonCache = await SigSolsAPI.api('/spatial/parcel/zones/geojson/?types=canton,degraded');
    }
    const geojson = zonesGeoJsonCache?.features
      ? zonesGeoJsonCache
      : { type: 'FeatureCollection', features: zonesGeoJsonCache || [] };
    parcelsLayer = L.geoJSON(geojson, {
      style: (f) => styleForZoneFeature(f, f.properties?.code === selectedParcelCode),
      onEachFeature: (feature, layer) => {
        const p = feature.properties || {};
        const typeLabel = p.zone_type === 'degraded' ? 'Zone dégradée' : 'Canton';
        layer.bindTooltip(`<strong>${p.name}</strong><br/>${typeLabel} · ${p.code}`, {
          sticky: true,
          className: 'parcel-tooltip',
        });
        layer.on('mouseover', () => {
          if (p.code !== selectedParcelCode) {
            layer.setStyle({ weight: 3, fillOpacity: 0.2 });
          }
        });
        layer.on('mouseout', () => {
          if (p.code !== selectedParcelCode) {
            layer.setStyle(styleForZoneFeature(feature, false));
          }
        });
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

function renderSoilPointsInParcel(points) {
  const map = getMap();
  if (!map || !showSoilPointsOnMap() || !points?.length) return;
  if (parcelSoilLayer) map.removeLayer(parcelSoilLayer);
  parcelSoilLayer = L.layerGroup();
  points.forEach((p) => {
    const color = phColorHex(p.ph_color || 'green');
    L.circleMarker([p.lat, p.lon], {
      radius: 6,
      color: '#333',
      weight: 1,
      fillColor: color,
      fillOpacity: 0.9,
    })
      .bindPopup(`
        <strong>Point #${p.id}</strong><br/>
        pH ${p.ph} · ${p.soil_type}
      `)
      .addTo(parcelSoilLayer);
  });
  parcelSoilLayer.addTo(map);
}

function selectParcelByCode(code, geometry = null) {
  selectedParcelCode = code;
  selectedGeometry = geometry;
  shouldFitBounds = true;
  clearDrawnOnly();
  const sel = document.getElementById('parcel-zone-select');
  if (sel) sel.value = code;
  renderParcelList();
  setParcelStatus(`Parcelle « ${code} » — chargement…`);
  if (parcelsLayer) {
    parcelsLayer.eachLayer((layer) => {
      const f = layer.feature;
      const selected = f?.properties?.code === code;
      layer.setStyle(styleForZoneFeature(f, selected));
    });
  }
  scheduleLiveRefresh();
}

function highlightParcel(geojson, vulnerabilityLevel, fit = true) {
  const map = getMap();
  if (!map || !geojson) return;
  if (parcelHighlight) map.removeLayer(parcelHighlight);
  const color = VULN_COLORS[vulnerabilityLevel] || VULN_COLORS.moyenne;
  parcelHighlight = L.geoJSON(geojson, {
    style: { color, weight: 3, fillColor: color, fillOpacity: 0.18, dashArray: '4 6' },
  }).addTo(map);
  if (fit && shouldFitBounds) {
    try {
      map.fitBounds(parcelHighlight.getBounds(), { padding: [56, 56], maxZoom: 14 });
      shouldFitBounds = false;
    } catch { /* ignore */ }
  }
}

function formatHealthGauge(index) {
  if (index == null) {
    return '<p class="parcel-health parcel-health--unknown">Indice santé : données insuffisantes</p>';
  }
  const cls = healthClass(index);
  return `
    <div class="parcel-health parcel-health--${cls}">
      <span class="parcel-health-label">Indice santé sol</span>
      <div class="parcel-health-bar"><div class="parcel-health-fill" style="width:${index}%"></div></div>
      <strong class="parcel-health-value">${index}/100</strong>
    </div>`;
}

function formatTypesBreakdown(rows) {
  if (!rows?.length) return '';
  const total = rows.reduce((s, r) => s + r.count, 0) || 1;
  return `
    <ul class="parcel-types">
      ${rows.map((r) => {
        const pct = Math.round((r.count / total) * 100);
        return `<li><span>${r.soil_type}</span><em>${r.count}</em><i style="width:${pct}%"></i></li>`;
      }).join('')}
    </ul>`;
}

function formatStacLine(nasa) {
  const st = nasa?.stac_parcel;
  if (!st || st.skipped) return '';
  if (st.note === 'bbox_large') {
    return `<p class="parcel-stac">${st.message || 'Zone trop étendue pour la recherche STAC.'}</p>`;
  }
  if (st.error) {
    return `<p class="parcel-stac parcel-stac--warn">STAC NASA : ${st.error}</p>`;
  }
  const p = st.products || {};
  const m = p.MOD13Q1?.granules_found ?? '—';
  const s = p.SMAP?.granules_found ?? '—';
  return `<p class="parcel-stac">Catalogue STAC (60 j.) : MODIS ~${m} · SMAP ~${s} granule(s) proches</p>`;
}

function formatLivePanelHtml(data, { loading = false } = {}) {
  if (loading) {
    return '<div class="parcel-live-skeleton"><div class="sk-line"></div><div class="sk-grid"></div></div>';
  }
  const sp = data.soil_points || {};
  const nasa = data.nasa || {};
  const vuln = data.vulnerability || {};
  const ml = data.ml_prediction || {};
  const updated = data.analyzed_at
    ? new Date(data.analyzed_at).toLocaleTimeString('fr-FR')
    : '—';

  return `
    <div class="parcel-live-inner parcel-live-inner--${vuln.level || 'moyenne'}">
      <div class="parcel-live-header">
        <h4>${data.parcel_name || 'Parcelle'}</h4>
        <span class="parcel-vuln-badge parcel-vuln-badge--${vuln.level || 'moyenne'}">${vulnLabel(vuln.level)}</span>
      </div>
      ${data.zone_code ? `<p class="parcel-live-code">${data.zone_code}</p>` : ''}
      <p class="parcel-live-meta">${data.area?.area_ha ?? '—'} ha · ${sp.count ?? 0} point(s) sol</p>
      ${formatHealthGauge(data.health_index)}
      <div class="parcel-live-grid">
        <div><span>pH</span><strong>${sp.avg_ph ?? '—'}</strong><small>${sp.min_ph != null ? `${sp.min_ph}–${sp.max_ph}` : ''}</small></div>
        <div><span>NDVI</span><strong>${sp.avg_ndvi ?? nasa.avg_ndvi ?? '—'}</strong></div>
        <div><span>SMAP</span><strong>${sp.avg_smap ?? nasa.avg_smap ?? '—'}</strong></div>
        <div><span>Humid.</span><strong>${sp.avg_humidity_pct ?? '—'}%</strong></div>
      </div>
      <p class="parcel-live-nasa">${NDVI_LABELS[nasa.ndvi_status] || '—'} · ${SMAP_LABELS[nasa.smap_status] || '—'}</p>
      ${formatStacLine(nasa)}
      ${formatParcelExternalGrid(data.sentinel, data.weather)}
      ${formatSentinelHtml(data.sentinel)}
      ${formatWeatherHtml(data.weather)}
      ${formatTypesBreakdown(data.soil_types_breakdown)}
      ${ml?.predicted_class ? `<p class="parcel-live-ml">IA fertilité : <strong>${ml.predicted_class}</strong> (${Math.round((ml.confidence || 0) * 100)}%)</p>` : ''}
      ${(data.recommendations || []).slice(0, 2).map((r) => `<p class="parcel-live-tip">• ${r}</p>`).join('')}
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

function syncParcelDiagnostics(data) {
  if (!data) {
    resetParcelDiagnostics();
    return;
  }
  displaySentinelParcelSummary(data.sentinel, data.parcel_name);
  displayWeatherParcelSummary(data.weather, data.parcel_name);
}

async function refreshLiveParcelInfo(fullAnalysis = false) {
  const selRaw = document.getElementById('parcel-zone-select')?.value;
  const selVal = selRaw && String(selRaw).trim() ? String(selRaw).trim() : '';
  const zoneCode = selectedParcelCode || selVal || null;
  const geometry = zoneCode ? null : (selectedGeometry || getDrawnGeometry());

  if (!zoneCode && !geometry) {
    hideLivePanel();
    clearParcelLayers();
    resetParcelDiagnostics();
    return;
  }

  const requestId = ++liveRequestSeq;
  showLivePanel(formatLivePanelHtml({}, { loading: true }));
  const useMl = fullAnalysis || document.getElementById('parcel-use-ml')?.checked === true;
  const useSentinel = document.getElementById('parcel-use-sentinel')?.checked === true;
  const useWeather = document.getElementById('parcel-use-weather')?.checked !== false;

  try {
    const body = {
      use_ml: useMl,
      use_sentinel: useSentinel,
      use_weather: useWeather,
    };
    if (zoneCode) body.zone_code = zoneCode;
    else body.geometry = geometry;

    const data = await SigSolsAPI.api('/spatial/parcel/live/', {
      method: 'POST',
      body: JSON.stringify(body),
    });

    if (requestId !== liveRequestSeq) return;

    lastParcelData = data;
    saveLastParcelToStorage(data);
    showLivePanel(formatLivePanelHtml(data));
    highlightParcel(data.geometry_geojson, data.vulnerability?.level, shouldFitBounds);
    renderSoilPointsInParcel(data.soil_points_map);
    renderAnalysisResult(data);
    syncParcelDiagnostics(data);
    window.dispatchEvent(new CustomEvent('sig-sols-parcel-analyzed', { detail: data }));
    document.getElementById('parcel-analysis-result')?.scrollIntoView?.({ behavior: 'smooth', block: 'nearest' });
    setParcelStatus(`${data.parcel_name || zoneCode} — ${spCount(data)} pt(s) · vuln. ${vulnLabel(data.vulnerability?.level)}`);
  } catch (e) {
    if (requestId !== liveRequestSeq) return;
    notifyError(e);
    setParcelStatus('Erreur : ' + (e.message || 'impossible'));
    showLivePanel(`<p class="parcel-error">${e.message}</p>`);
    resetParcelDiagnostics();
  }
}

function spCount(data) {
  return data?.soil_points?.count ?? 0;
}

function renderAnalysisResult(data) {
  const box = document.getElementById('parcel-analysis-result');
  if (!box) return;
  const sp = data.soil_points || {};
  const nasa = data.nasa || {};
  const vuln = data.vulnerability || {};
  const ml = data.ml_prediction || {};

  box.classList.remove('hidden');
  box.innerHTML = `
    <div class="parcel-report parcel-report--${vuln.level || 'moyenne'}">
      <h4>${data.parcel_name || 'Parcelle'}</h4>
      <p class="parcel-meta">
        ${data.area?.area_ha ?? '—'} ha · ${sp.count ?? 0} point(s) ·
        Santé <strong>${data.health_index ?? '—'}/100</strong> ·
        Vuln. <strong>${vulnLabel(vuln.level)}</strong>
      </p>
      <div class="parcel-metrics">
        <span>pH <strong>${sp.avg_ph ?? '—'}</strong> (${sp.min_ph ?? '—'} – ${sp.max_ph ?? '—'})</span>
        <span>NDVI <strong>${sp.avg_ndvi ?? nasa.avg_ndvi ?? '—'}</strong></span>
        <span>SMAP <strong>${sp.avg_smap ?? nasa.avg_smap ?? '—'}</strong></span>
        <span>Humid. <strong>${sp.avg_humidity_pct ?? '—'}%</strong></span>
      </div>
      ${formatParcelExternalGrid(data.sentinel, data.weather, { title: 'Imagerie & météo (parcelle)' })}
      ${formatTypesBreakdown(data.soil_types_breakdown)}
      <p class="parcel-nasa">NASA : ${NDVI_LABELS[nasa.ndvi_status] || '—'} · ${SMAP_LABELS[nasa.smap_status] || '—'}</p>
      ${formatStacLine(nasa)}
      ${formatSentinelHtml(data.sentinel)}
      ${formatWeatherHtml(data.weather)}
      ${ml?.predicted_class ? `<p class="parcel-ml">IA : <strong>${ml.predicted_class}</strong> (${Math.round((ml.confidence || 0) * 100)}%)</p>` : ''}
      ${(data.recommendations || []).length ? `<ul class="parcel-recs">${data.recommendations.map((r) => `<li>${r}</li>`).join('')}</ul>` : ''}
    </div>`;
}

function exportParcelReport() {
  if (!lastParcelData) {
    notifyError({ message: 'Sélectionnez une parcelle avant d\'exporter.' });
    return;
  }
  const blob = new Blob([JSON.stringify(lastParcelData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `parcelle-${lastParcelData.zone_code || 'custom'}-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  notifySuccess('Rapport JSON exporté.');
}

function printParcelReport() {
  if (!lastParcelData) {
    notifyError({ message: 'Sélectionnez une parcelle avant d\'imprimer.' });
    return;
  }
  const d = lastParcelData;
  const sp = d.soil_points || {};
  const html = `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>${d.parcel_name}</title>
    <style>body{font-family:sans-serif;padding:2rem}h1{color:#134e2a}table{border-collapse:collapse;width:100%}
    td,th{border:1px solid #ccc;padding:8px}th{background:#f3efe6}</style></head><body>
    <h1>${d.parcel_name}</h1><p>${d.zone_code || ''} · ${d.area?.area_ha ?? '—'} ha · Santé ${d.health_index ?? '—'}/100</p>
    <table><tr><th>pH moy.</th><th>NDVI</th><th>SMAP</th><th>Points sol</th><th>Vulnérabilité</th></tr>
    <tr><td>${sp.avg_ph ?? '—'}</td><td>${sp.avg_ndvi ?? '—'}</td><td>${sp.avg_smap ?? '—'}</td>
    <td>${sp.count ?? 0}</td><td>${d.vulnerability?.level ?? '—'}</td></tr></table>
    <p><em>Données NASA — crédit NASA Earth Science · SIG Sols Togo</em></p>
    <script>window.onload=()=>window.print()</script></body></html>`;
  const w = window.open('', '_blank');
  if (!w) {
    notifyError({ message: 'Pop-up bloquée — autorisez les fenêtres pour imprimer.' });
    return;
  }
  w.document.write(html);
  w.document.close();
}

async function runParcelAnalysis() {
  if (!selectedParcelCode && !getDrawnGeometry()) {
    notifyError({ message: 'Sélectionnez ou dessinez une parcelle.' });
    return;
  }
  trackActivity('parcel_analyze', { parcel: selectedParcelCode || 'drawn' }, 'parcel');
  setParcelStatus('Analyse complète (IA)…');
  await refreshLiveParcelInfo(true);
}

function onZoneSelectChange() {
  const code = document.getElementById('parcel-zone-select')?.value;
  if (code) selectParcelByCode(code);
  else clearParcelSelectionSoft();
}

function clearParcelSelectionSoft() {
  selectedParcelCode = null;
  lastParcelData = null;
  resetParcelDiagnostics();
  hideLivePanel();
  clearParcelLayers();
  const box = document.getElementById('parcel-analysis-result');
  if (box) {
    box.classList.add('hidden');
    box.innerHTML = '';
  }
  renderParcelList();
  loadParcelsOnMap();
  setParcelStatus('Sélectionnez une parcelle.');
}

function clearParcelSelection() {
  selectedParcelCode = null;
  selectedGeometry = null;
  lastParcelData = null;
  shouldFitBounds = true;
  document.getElementById('parcel-zone-select').value = '';
  document.getElementById('parcel-search').value = '';
  clearDrawnOnly();
  clearParcelLayers();
  resetParcelDiagnostics();
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

function startLiveInterval() {
  if (liveInterval) clearInterval(liveInterval);
  liveInterval = setInterval(() => {
    if (isLiveEnabled() && (selectedParcelCode || selectedGeometry || getDrawnGeometry())) {
      refreshLiveParcelInfo(false);
    }
  }, 30000);
}

function initParcelTools() {
  initDrawControl();
  loadZonesSelect();
  loadParcelsOnMap();
  startLiveInterval();

  document.getElementById('btn-parcel-analyze')?.addEventListener('click', runParcelAnalysis);
  document.getElementById('btn-parcel-clear')?.addEventListener('click', clearParcelSelection);
  document.getElementById('btn-parcel-refresh')?.addEventListener('click', () => refreshLiveParcelInfo(false));
  document.getElementById('parcel-live-refresh')?.addEventListener('click', () => refreshLiveParcelInfo(false));
  document.getElementById('btn-parcel-export')?.addEventListener('click', exportParcelReport);
  document.getElementById('btn-parcel-print')?.addEventListener('click', printParcelReport);
  document.getElementById('parcel-zone-select')?.addEventListener('change', onZoneSelectChange);
  document.getElementById('parcel-show-on-map')?.addEventListener('change', loadParcelsOnMap);
  document.getElementById('parcel-show-soil-points')?.addEventListener('change', () => {
    if (lastParcelData) renderSoilPointsInParcel(lastParcelData.soil_points_map);
    else clearParcelLayers();
  });
  document.getElementById('parcel-live-update')?.addEventListener('change', () => {
    if (isLiveEnabled()) scheduleLiveRefresh();
  });
  document.getElementById('parcel-use-sentinel')?.addEventListener('change', () => {
    if (selectedParcelCode || getDrawnGeometry()) scheduleLiveRefresh();
  });
  document.getElementById('parcel-use-weather')?.addEventListener('change', () => {
    if (selectedParcelCode || getDrawnGeometry()) scheduleLiveRefresh();
  });
  document.getElementById('parcel-live-close')?.addEventListener('click', hideLivePanel);
  document.getElementById('parcel-search')?.addEventListener('input', renderParcelList);
  document.querySelectorAll('.parcel-filter-tab').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.parcel-filter-tab').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      parcelFilter = btn.dataset.filter || 'all';
      rebuildZoneSelect();
      renderParcelList();
    });
  });

  setParcelStatus('Cliquez sur une parcelle, cherchez par nom ou dessinez un polygone.');
}

window.SigSolsParcel = {
  initParcelTools,
  loadZonesSelect,
  loadParcelsOnMap,
  runParcelAnalysis,
  clearParcelSelection,
  selectParcelByCode,
  refreshLiveParcelInfo,
  getLastParcelData: () => lastParcelData,
};
