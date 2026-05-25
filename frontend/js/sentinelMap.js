/**
 * Sentinel Hub — intégration carte (couches, sonde, parcelle).
 */
import {
  MARITIME_CENTER,
  bboxFromLeaflet,
  sentinelTileUrl,
} from './core/mapUtils.js';
import { notifyError, notifySuccess } from './core/ui.js';

const MARITIME_BOUNDS = [[6.0, 0.9], [6.8, 1.8]];
let overlays = {};
let sentinelOpacity = 0.55;
let clickProbeEnabled = false;
let clickHandler = null;

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

function summarizeSentinelError(error) {
  const msg = String(error || '').toLowerCase();
  if (msg.includes('nameresolutionerror') || msg.includes('failed to resolve') || msg.includes('dns')) {
    return 'Sentinel Hub indisponible pour le moment (réseau/DNS).';
  }
  if (msg.includes('401') || msg.includes('oauth') || msg.includes('authentification')) {
    return 'Connexion Sentinel Hub refusée. Vérifiez les clés OAuth.';
  }
  if (msg.includes('timeout')) {
    return 'Sentinel Hub répond trop lentement. Réessayez.';
  }
  return `Sentinel : ${error}`;
}

function getMap() {
  return window.SigSolsMap?.getMap?.();
}

function getBasemaps() {
  return window.SigSolsMap?.getBasemaps?.() || {};
}

export function setSentinelOpacity(pct) {
  sentinelOpacity = Math.min(1, Math.max(0.15, pct / 100));
  Object.values(overlays).forEach((layer) => {
    if (layer?.setOpacity) layer.setOpacity(sentinelOpacity);
  });
  const label = document.getElementById('sentinel-opacity-label');
  if (label) label.textContent = `${Math.round(sentinelOpacity * 100)}%`;
}

export function toggleSentinelLayer(layerId, on) {
  const map = getMap();
  if (!map) return;

  if (on && !overlays[layerId]) {
    overlays[layerId] = L.tileLayer(sentinelTileUrl(window.location.origin, layerId), {
      opacity: sentinelOpacity,
      maxZoom: 14,
      zIndex: 450,
    }).addTo(map);
    if (document.getElementById('sentinel-auto-satellite')?.checked) {
      const basemaps = getBasemaps();
      if (basemaps.satellite && !map.hasLayer(basemaps.satellite)) {
        Object.values(basemaps).forEach((b) => { if (map.hasLayer(b)) map.removeLayer(b); });
        basemaps.satellite.addTo(map);
      }
    }
    document.querySelector('.sentinel-ndvi-legend')?.classList.toggle('hidden', layerId !== 'ndvi');
  } else if (!on && overlays[layerId]) {
    map.removeLayer(overlays[layerId]);
    delete overlays[layerId];
    if (layerId === 'ndvi' && !overlays.ndvi) {
      document.querySelector('.sentinel-ndvi-legend')?.classList.add('hidden');
    }
  }
  updateMapBadge();
}

function updateMapBadge() {
  const badge = document.getElementById('sentinel-map-badge');
  if (!badge) return;
  const active = Object.keys(overlays);
  if (!active.length) {
    badge.classList.add('hidden');
    return;
  }
  badge.classList.remove('hidden');
  badge.textContent = `Sentinel-2 : ${active.join(', ')}`;
}

export async function loadSentinelToggles() {
  const container = document.getElementById('sentinel-layers-toggles');
  const statusEl = document.getElementById('sentinel-status-msg');
  if (!container) return;

  try {
    const status = await SigSolsAPI.api('/sentinel/status/');
    if (statusEl) {
      statusEl.textContent = status.ok
        ? 'Sentinel Hub connecté — activez une couche ci-dessous'
        : (status.message || 'Non configuré');
      statusEl.classList.toggle('sentinel-status--ok', Boolean(status.ok));
      statusEl.classList.toggle('sentinel-status--err', !status.ok);
    }
    if (!status.configured || !status.ok) {
      container.innerHTML = '<p class="panel-hint">Vérifiez SENTINEL_HUB_CLIENT_ID et le secret dans .env</p>';
      return;
    }

    const layers = await SigSolsAPI.api('/sentinel/layers/');
    container.innerHTML = '';
    (layers.layers || []).forEach((layer) => {
      const label = document.createElement('label');
      label.className = 'map-layer-toggle';
      label.innerHTML = `<input type="checkbox" data-sentinel-layer="${layer.id}" /> ${escapeHtml(layer.title)}`;
      label.querySelector('input').addEventListener('change', (e) => {
        toggleSentinelLayer(layer.id, e.target.checked);
      });
      container.appendChild(label);
    });
  } catch (err) {
    if (statusEl) statusEl.textContent = err.message || 'Sentinel Hub indisponible';
    container.innerHTML = '';
  }
}

export async function analyzeViewportNdvi() {
  const out = document.getElementById('sentinel-ndvi-out');
  const map = getMap();
  if (!out || !map) return;

  out.textContent = 'Analyse NDVI Sentinel (vue carte)…';
  try {
    const data = await SigSolsAPI.api('/sentinel/analyze/', {
      method: 'POST',
      body: JSON.stringify({ bbox: bboxFromLeaflet(map) }),
    });
    if (data.ndvi_mean == null) {
      out.textContent = 'Pas de pixels valides (nuages ou hors couverture).';
      return;
    }
    out.textContent = `NDVI moyen : ${data.ndvi_mean} (min ${data.ndvi_min}, max ${data.ndvi_max}) — ${data.pixel_count} px`;
    notifySuccess('NDVI Sentinel calculé pour la vue actuelle.');
  } catch (err) {
    out.textContent = err.message || 'Échec analyse Sentinel';
    notifyError(err);
  }
}

export async function analyzeBboxNdvi(bbox, label = '') {
  const out = document.getElementById('sentinel-ndvi-out');
  if (!out) return null;

  const bboxStr = Array.isArray(bbox) ? bbox.join(',') : bbox;
  out.textContent = label ? `${label} — analyse…` : 'Analyse NDVI…';
  try {
    const data = await SigSolsAPI.api('/sentinel/analyze/', {
      method: 'POST',
      body: JSON.stringify({ bbox: bboxStr }),
    });
    if (data.ndvi_mean == null) {
      out.textContent = 'NDVI : pas de données (nuages / hors zone).';
      return data;
    }
    out.textContent = `NDVI ${label ? `(${label}) ` : ''}: ${data.ndvi_mean} [${data.ndvi_min} – ${data.ndvi_max}]`;
    return data;
  } catch (err) {
    out.textContent = err.message || 'Échec NDVI Sentinel';
    return null;
  }
}

function smallBboxAround(lat, lon, delta = 0.02) {
  return [lon - delta, lat - delta, lon + delta, lat + delta];
}

function bindClickProbe() {
  const map = getMap();
  if (!map) return;

  if (clickHandler) {
    map.off('click', clickHandler);
    clickHandler = null;
  }

  if (!clickProbeEnabled) return;

  clickHandler = async (e) => {
    const { lat, lng } = e.latlng;
    const bbox = smallBboxAround(lat, lng);
    const data = await analyzeBboxNdvi(bbox, `${lat.toFixed(4)}°, ${lng.toFixed(4)}°`);
    if (data?.ndvi_mean != null) {
      L.popup()
        .setLatLng(e.latlng)
        .setContent(
          `<strong>NDVI Sentinel-2</strong><br/>`
          + `Moyenne : <strong>${data.ndvi_mean}</strong><br/>`
          + `Min / max : ${data.ndvi_min} / ${data.ndvi_max}`,
        )
        .openOn(map);
    }
  };
  map.on('click', clickHandler);
}

export function setClickProbe(enabled) {
  clickProbeEnabled = Boolean(enabled);
  const map = getMap();
  if (map) {
    map.getContainer().style.cursor = clickProbeEnabled ? 'crosshair' : '';
  }
  bindClickProbe();
}

export function fitMaritimePilot() {
  const map = getMap();
  if (!map) return;
  map.fitBounds(MARITIME_BOUNDS, { padding: [24, 24] });
}

export function initSentinelMapTools() {
  document.getElementById('btn-sentinel-ndvi')?.addEventListener('click', analyzeViewportNdvi);
  document.getElementById('btn-sentinel-fit-maritime')?.addEventListener('click', fitMaritimePilot);

  const opacityInput = document.getElementById('sentinel-opacity');
  opacityInput?.addEventListener('input', () => setSentinelOpacity(Number(opacityInput.value)));

  document.getElementById('sentinel-click-probe')?.addEventListener('change', (e) => {
    setClickProbe(e.target.checked);
  });

  setSentinelOpacity(Number(opacityInput?.value || 55));
}

export function displaySentinelParcelSummary(sentinel, parcelName = '') {
  const out = document.getElementById('sentinel-ndvi-out');
  const badge = document.getElementById('sentinel-map-badge');
  if (!out) return;

  if (!sentinel || sentinel.skipped) {
    out.textContent = '';
    return;
  }
  if (sentinel.configured === false) {
    out.textContent = 'Sentinel Hub non configuré (.env)';
    badge?.classList.add('hidden');
    return;
  }
  if (sentinel.error) {
    out.textContent = summarizeSentinelError(sentinel.error);
    badge?.classList.add('hidden');
    return;
  }
  if (sentinel.ndvi_mean == null) {
    out.textContent = 'Sentinel-2 : pas de pixels valides (nuages)';
    badge?.classList.add('hidden');
    return;
  }
  const label = parcelName ? `parcelle « ${parcelName} »` : 'parcelle';
  out.textContent = `NDVI ${label} : ${sentinel.ndvi_mean} (min ${sentinel.ndvi_min}, max ${sentinel.ndvi_max}) — ${sentinel.pixel_count || '—'} px`;
  if (badge) {
    badge.classList.remove('hidden');
    badge.textContent = `Sentinel-2 NDVI : ${sentinel.ndvi_mean}`;
  }
}

export function clearSentinelParcelSummary() {
  const out = document.getElementById('sentinel-ndvi-out');
  if (out) out.textContent = '';
  document.getElementById('sentinel-map-badge')?.classList.add('hidden');
}

export function formatSentinelHtml(sentinel) {
  if (!sentinel || sentinel.skipped) return '';
  if (sentinel.configured === false) {
    return '<p class="parcel-sentinel parcel-sentinel--warn">Sentinel Hub non configuré (.env)</p>';
  }
  if (sentinel.error) {
    return `<p class="parcel-sentinel parcel-sentinel--warn">${escapeHtml(summarizeSentinelError(sentinel.error))}</p>`;
  }
  if (sentinel.ndvi_mean == null) {
    return '<p class="parcel-sentinel">Sentinel-2 : pas de pixels valides (nuages)</p>';
  }
  return `<p class="parcel-sentinel">Sentinel-2 NDVI : <strong>${sentinel.ndvi_mean}</strong> `
    + `(min ${sentinel.ndvi_min}, max ${sentinel.ndvi_max}) · ${sentinel.pixel_count || '—'} px</p>`;
}
