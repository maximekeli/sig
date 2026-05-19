/**
 * Fonctionnalités avancées SIG Sols — carte, admin, alertes, offline, WebSocket.
 */
import { toast } from './core/toast.js';
import { notifyError, notifySuccess, openModal, closeModal } from './core/ui.js';

let clusterGroup = null;
let heatLayer = null;
let trajectoryLayer = null;
let nearMeLayer = null;
let ws = null;
let pendingAddCoords = null;

export function initMapAdvanced(map, markersLayer) {
  if (typeof L.markerClusterGroup === 'function') {
    clusterGroup = L.markerClusterGroup();
    map.addLayer(clusterGroup);
  }
  map.on('click', (e) => {
    if (!document.getElementById('mode-add-point')?.checked) return;
    if (!SigSolsAPI.isAuthenticated()) {
      toast('Connectez-vous pour ajouter un point.', 'warning');
      return;
    }
    openAddPointForm(e.latlng.lat, e.latlng.lng);
  });
  document.getElementById('btn-add-point-save')?.addEventListener('click', submitAddPoint);
}

export function addMarkerToCluster(marker) {
  if (clusterGroup) clusterGroup.addLayer(marker);
}

export function clearClusters() {
  clusterGroup?.clearLayers();
}

export async function toggleHeatmap(map, field = 'ph') {
  if (heatLayer) {
    map.removeLayer(heatLayer);
    heatLayer = null;
    toast('Carte de chaleur désactivée.', 'info');
    return;
  }
  const data = await SigSolsAPI.api(`/heatmap/?field=${field}`);
  if (typeof L.heatLayer !== 'function') {
    toast('Plugin heatmap non chargé.', 'error');
    return;
  }
  heatLayer = L.heatLayer(data.points, { radius: 25, blur: 18, maxZoom: 12 });
  heatLayer.addTo(map);
  toast(`Carte de chaleur ${field} activée.`, 'success');
}

export async function nearMe(map) {
  if (!navigator.geolocation) {
    toast('GPS indisponible sur cet appareil.', 'error');
    return;
  }
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const { latitude, longitude } = pos.coords;
    map.setView([latitude, longitude], 14);
    const r = await SigSolsAPI.api(
      `/spatial/proximity/?lon=${longitude}&lat=${latitude}&radius_m=5000`,
    );
    if (nearMeLayer) map.removeLayer(nearMeLayer);
    nearMeLayer = L.layerGroup().addTo(map);
    L.circleMarker([latitude, longitude], {
      radius: 10,
      color: '#3b82f6',
      fillColor: '#3b82f6',
      fillOpacity: 0.8,
    }).bindPopup('<strong>Vous</strong>').addTo(nearMeLayer);
    (r.features || r.results || []).slice(0, 50).forEach((f) => {
      const coords = f.geometry?.coordinates || [f.lon, f.lat];
      if (!coords) return;
      L.circleMarker([coords[1], coords[0]], {
        radius: 6,
        color: '#c9a962',
        fillOpacity: 0.7,
      })
        .bindPopup(`Point #${f.properties?.id || f.id}`)
        .addTo(nearMeLayer);
    });
    toast(`${r.count ?? 0} point(s) à proximité (5 km).`, 'success', 5000);
  }, () => toast('Impossible d\'obtenir la position.', 'error'));
}

function openAddPointForm(lat, lon) {
  pendingAddCoords = { lat, lon };
  const coordsEl = document.getElementById('add-point-coords');
  if (coordsEl) coordsEl.textContent = `Coordonnées : ${lat.toFixed(5)}, ${lon.toFixed(5)}`;
  openModal('add-point-modal');
}

async function submitAddPoint() {
  if (!pendingAddCoords) return;
  const { lat, lon } = pendingAddCoords;
  const body = {
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [lon, lat] },
    properties: {
      ph: parseFloat(document.getElementById('ap-ph')?.value || '6.2'),
      humidity_pct: parseFloat(document.getElementById('ap-humidity')?.value || '35'),
      soil_type: document.getElementById('ap-soil-type')?.value || 'limoneux',
      collected_at: new Date().toISOString().slice(0, 10),
      source: 'terrain',
    },
  };
  try {
    if (!navigator.onLine) {
      queueOfflinePoint({ body });
      notifySuccess('Point en file d\'attente (hors ligne).');
    } else {
      await SigSolsAPI.api('/points/', { method: 'POST', body: JSON.stringify(body) });
      notifySuccess('Point enregistré (validation en attente).');
    }
    closeModal('add-point-modal');
    pendingAddCoords = null;
    document.getElementById('mode-add-point').checked = false;
    SigSolsMap.loadSoilPoints();
  } catch (e) {
    notifyError(e);
  }
}

export async function loadNdviChart(pointId, containerId) {
  const data = await SigSolsAPI.api(`/spatial/ndvi-timeseries/${pointId}/`);
  const el = document.getElementById(containerId);
  if (!el || !data.series?.length) {
    if (el) el.textContent = 'Pas de série NDVI.';
    return;
  }
  if (typeof Chart !== 'undefined' && el.tagName === 'DIV') {
    el.innerHTML = '<canvas></canvas>';
    const canvas = el.querySelector('canvas');
    new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.series.map((s) => s.date),
        datasets: [{
          label: 'NDVI',
          data: data.series.map((s) => s.ndvi),
          borderColor: '#2d8a52',
          tension: 0.3,
        }],
      },
      options: { responsive: true, plugins: { legend: { display: false } } },
    });
  } else {
    el.innerHTML = data.series.map((s) => `${s.date}: ${s.ndvi}`).join('<br>');
  }
}

export async function loadAlerts() {
  const list = document.getElementById('alerts-list');
  if (!list) return;
  try {
    const data = await SigSolsAPI.api('/platform/alerts/drought/');
    list.innerHTML = data.results?.length
      ? data.results.map((a) => `<li class="alert-${a.severity}">${a.message}</li>`).join('')
      : '<li>Aucune alerte active.</li>';
  } catch {
    list.innerHTML = '<li>Connectez-vous pour voir les alertes.</li>';
  }
}

export async function loadNotifications() {
  const el = document.getElementById('notifications-list');
  if (!el || !SigSolsAPI.isAuthenticated()) return;
  try {
    const data = await SigSolsAPI.api('/platform/notifications/');
    const items = data.results || (Array.isArray(data) ? data : []);
    el.innerHTML = items.length
      ? items.map((n) => `<li class="${n.is_read ? '' : 'unread'}">
          <strong>${n.title}</strong> — ${n.message}
          ${!n.is_read ? `<div class="notification-actions"><button type="button" class="btn-tiny" data-mark-read="${n.id}">Marquer lu</button></div>` : ''}
        </li>`).join('')
      : '<li>Aucune notification.</li>';
    el.querySelectorAll('[data-mark-read]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        await SigSolsAPI.api(`/platform/notifications/${btn.dataset.markRead}/read/`, { method: 'POST' });
        loadNotifications();
      });
    });
  } catch {
    el.innerHTML = '<li>Notifications indisponibles.</li>';
  }
}

export async function loadPendingValidation() {
  const el = document.getElementById('adm-pending-list');
  if (!el) return;
  try {
    const data = await SigSolsAPI.api('/validation/pending/');
    el.innerHTML = (data.results || []).map(
      (p) => `<li>#${p.id} pH ${p.ph} — ${p.soil_type}
        <button type="button" data-validate="${p.id}" data-action="validate">Valider</button>
        <button type="button" data-validate="${p.id}" data-action="reject">Rejeter</button></li>`,
    ).join('') || '<li>Aucun point en attente.</li>';
    el.querySelectorAll('[data-validate]').forEach((btn) => {
      btn.addEventListener('click', () => validatePoint(+btn.dataset.validate, btn.dataset.action));
    });
  } catch {
    el.innerHTML = '<li>Accès réservé aux administrateurs.</li>';
  }
}

export async function validatePoint(id, action) {
  try {
    await SigSolsAPI.api(`/points/${id}/validate_point/`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
    notifySuccess(action === 'validate' ? 'Point validé.' : 'Point rejeté.');
    loadPendingValidation();
    loadAdminDashboard();
    SigSolsMap.loadSoilPoints();
  } catch (e) {
    notifyError(e);
  }
}

export async function loadAdminDashboard() {
  if (!SigSolsAPI.isAuthenticated()) return;
  try {
    const d = await SigSolsAPI.api('/platform/admin/dashboard/');
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    set('adm-users', d.users_total);
    set('adm-points', d.soil_points);
    set('adm-pending', d.pending_validation);
    set('adm-agents', d.live_agents);
    set('adm-alerts', d.active_alerts);
    const audit = document.getElementById('adm-audit');
    if (audit) {
      audit.innerHTML = (d.recent_audit || []).map(
        (a) => `<li>${a.created_at?.slice(0, 16)} — ${a.username || '?'} — ${a.action} ${a.resource}</li>`,
      ).join('');
    }
  } catch (e) {
    console.warn('Admin dashboard', e);
  }
}

export async function showTrajectory(map, userId) {
  if (!SigSolsAPI.isAuthenticated()) return;
  const uid = userId || SigSolsAPI.getUser()?.id;
  const data = await SigSolsAPI.api(`/auth/trajectory/${uid ? `${uid}/` : ''}?hours=24`);
  if (trajectoryLayer) map.removeLayer(trajectoryLayer);
  const latlngs = data.points.map((p) => [p.lat, p.lon]);
  if (latlngs.length) {
    trajectoryLayer = L.polyline(latlngs, { color: '#7c3aed', weight: 3, dashArray: '6' });
    trajectoryLayer.addTo(map);
    map.fitBounds(trajectoryLayer.getBounds());
    toast(`${latlngs.length} point(s) de trajectoire (24 h).`, 'info');
  } else {
    toast('Aucune trajectoire enregistrée.', 'info');
  }
}

export function connectWebSocket() {
  if (!SigSolsAPI.getToken()) return;
  if (ws?.readyState === WebSocket.OPEN) return;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws/live/`);
  ws.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'location' && window.SigSolsMap?.onWsLocation) {
        SigSolsMap.onWsLocation(msg);
      }
    } catch { /* ignore */ }
  };
  ws.onclose = () => {
    setTimeout(() => {
      if (SigSolsAPI.isAuthenticated()) connectWebSocket();
    }, 5000);
  };
}

export function queueOfflinePoint(payload) {
  const q = JSON.parse(localStorage.getItem('sig_sols_offline_queue') || '[]');
  q.push({ ...payload, queued_at: Date.now() });
  localStorage.setItem('sig_sols_offline_queue', JSON.stringify(q));
}

export async function syncOfflineQueue() {
  const q = JSON.parse(localStorage.getItem('sig_sols_offline_queue') || '[]');
  if (!q.length || !navigator.onLine || !SigSolsAPI.isAuthenticated()) return;
  const remaining = [];
  let synced = 0;
  for (const item of q) {
    try {
      await SigSolsAPI.api('/points/', { method: 'POST', body: JSON.stringify(item.body) });
      synced += 1;
    } catch {
      remaining.push(item);
    }
  }
  localStorage.setItem('sig_sols_offline_queue', JSON.stringify(remaining));
  if (synced) {
    notifySuccess(`${synced} point(s) synchronisé(s).`);
    SigSolsMap.loadSoilPoints();
  }
}

export function applyPublicMode() {
  const isPublic = SigSolsAPI.getUser()?.role === 'public';
  document.body.classList.toggle('public-mode', isPublic);
}

window.SigSolsFeatures = {
  initMapAdvanced,
  addMarkerToCluster,
  clearClusters,
  toggleHeatmap,
  nearMe,
  loadNdviChart,
  loadAlerts,
  loadNotifications,
  loadAdminDashboard,
  loadPendingValidation,
  validatePoint,
  showTrajectory,
  connectWebSocket,
  queueOfflinePoint,
  syncOfflineQueue,
  applyPublicMode,
};
