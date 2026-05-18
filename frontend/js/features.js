/**
 * Fonctionnalités avancées SIG Sols — carte, admin, alertes, offline, WebSocket.
 */

let clusterGroup = null;
let heatLayer = null;
let trajectoryLayer = null;
let ws = null;

export function initMapAdvanced(map, markersLayer) {
  if (typeof L.markerClusterGroup === 'function') {
    clusterGroup = L.markerClusterGroup();
    map.addLayer(clusterGroup);
  }
  map.on('click', (e) => {
    if (!document.getElementById('mode-add-point')?.checked) return;
    if (!SigSolsAPI.isAuthenticated()) {
      alert('Connectez-vous pour ajouter un point.');
      return;
    }
    openAddPointForm(e.latlng.lat, e.latlng.lng);
  });
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
    return;
  }
  const data = await SigSolsAPI.api(`/heatmap/?field=${field}`);
  if (typeof L.heatLayer !== 'function') {
    alert('Plugin heatmap non chargé.');
    return;
  }
  heatLayer = L.heatLayer(data.points, { radius: 25, blur: 18, maxZoom: 12 });
  heatLayer.addTo(map);
}

export async function nearMe(map) {
  if (!navigator.geolocation) return alert('GPS indisponible');
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const { latitude, longitude } = pos.coords;
    map.setView([latitude, longitude], 14);
    const r = await SigSolsAPI.api(
      `/spatial/proximity/?lon=${longitude}&lat=${latitude}&radius_m=5000`,
    );
    alert(`${r.count} point(s) de sol à proximité.`);
  });
}

function openAddPointForm(lat, lon) {
  const ph = prompt('pH (3.5–9.5):', '6.2');
  if (!ph) return;
  const humidity = prompt('Humidité %:', '35');
  const soilType = prompt('Type (limoneux, argileux…):', 'limoneux');
  SigSolsAPI.api('/points/', {
    method: 'POST',
    body: JSON.stringify({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [lon, lat] },
      properties: {
        ph: parseFloat(ph),
        humidity_pct: parseFloat(humidity || 35),
        soil_type: soilType || 'limoneux',
        collected_at: new Date().toISOString().slice(0, 10),
        source: 'terrain',
      },
    }),
  }).then(() => {
    SigSolsMap.loadSoilPoints();
    alert('Point enregistré (en attente de validation).');
  }).catch((e) => alert(e.message));
}

export async function loadNdviChart(pointId, containerId) {
  const data = await SigSolsAPI.api(`/spatial/ndvi-timeseries/${pointId}/`);
  const el = document.getElementById(containerId);
  if (!el || !data.series?.length) {
    if (el) el.textContent = 'Pas de série NDVI.';
    return;
  }
  el.innerHTML = data.series.map((s) => `${s.date}: ${s.ndvi}`).join('<br>');
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
  const data = await SigSolsAPI.api('/platform/notifications/');
  el.innerHTML = (data.results || data).map?.((n) => n.title
    ? `<li class="${n.is_read ? '' : 'unread'}"><strong>${n.title}</strong> — ${n.message}</li>`
    : '').join('') || (Array.isArray(data) ? data.map((n) => `<li>${n.title}</li>`).join('') : '');
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
  }
}

export function connectWebSocket() {
  if (!SigSolsAPI.getToken()) return;
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
  for (const item of q) {
    try {
      await SigSolsAPI.api('/points/', { method: 'POST', body: JSON.stringify(item.body) });
    } catch {
      remaining.push(item);
    }
  }
  localStorage.setItem('sig_sols_offline_queue', JSON.stringify(remaining));
  if (q.length !== remaining.length) SigSolsMap.loadSoilPoints();
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
  showTrajectory,
  connectWebSocket,
  queueOfflinePoint,
  syncOfflineQueue,
  applyPublicMode,
};
