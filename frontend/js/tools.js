/**
 * Outils terrain : import, recherche proximité, recherche par ID.
 */
import { toast } from './core/toast.js';
import { notifyError, notifySuccess } from './core/ui.js';

let proximityLayer = null;

export async function importGeoJsonFile(file) {
  if (!file) return;
  if (!SigSolsAPI.isAuthenticated()) {
    toast('Connexion agent/admin requise.', 'warning');
    return;
  }
  const form = new FormData();
  form.append('file', file);
  try {
    const token = SigSolsAPI.getToken();
    const res = await fetch(`${window.location.origin}/api/v1/points/import_data/`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || data.detail || res.statusText);
    notifySuccess(`${data.created} point(s) importé(s).`);
    SigSolsMap.loadSoilPoints();
  } catch (e) {
    notifyError(e);
  }
}

export async function searchPointById() {
  const id = document.getElementById('search-point-id')?.value?.trim();
  if (!id) return;
  try {
    const p = await SigSolsAPI.api(`/points/${id}/`);
    const map = SigSolsMap.getMap?.();
    if (map && p.location) {
      const lon = p.location.coordinates?.[0] ?? p.lon;
      const lat = p.location.coordinates?.[1] ?? p.lat;
      map.setView([lat, lon], 15);
      L.circleMarker([lat, lon], { radius: 12, color: '#c9a962', fillOpacity: 0.9 })
        .addTo(map)
        .bindPopup(`#${p.id} pH ${p.ph}`)
        .openPopup();
    }
    notifySuccess(`Point #${id} trouvé.`);
  } catch (e) {
    notifyError(e);
  }
}

export async function runProximitySearch() {
  const map = SigSolsMap.getMap?.();
  if (!map) return;
  const center = map.getCenter();
  const radius = parseInt(document.getElementById('proximity-radius')?.value || '1000', 10);
  try {
    const r = await SigSolsAPI.api(
      `/spatial/proximity/?lon=${center.lng}&lat=${center.lat}&radius_m=${radius}`,
    );
    if (proximityLayer) map.removeLayer(proximityLayer);
    proximityLayer = L.layerGroup().addTo(map);
    L.circle([center.lat, center.lng], {
      radius,
      color: '#2d8a52',
      fillOpacity: 0.05,
      weight: 2,
    }).addTo(proximityLayer);
    (r.results || []).forEach((p) => {
      L.circleMarker([p.lat, p.lon], {
        radius: 7,
        color: '#134e2a',
        fillColor: '#3daf6c',
        fillOpacity: 0.85,
      })
        .bindPopup(`#${p.id} · pH ${p.ph} · ${p.distance_m} m`)
        .addTo(proximityLayer);
    });
    const el = document.getElementById('proximity-result');
    if (el) el.textContent = `${r.count} point(s) dans ${radius} m`;
    notifySuccess(`${r.count} point(s) trouvé(s).`);
  } catch (e) {
    notifyError(e);
  }
}

export function initTools() {
  document.getElementById('import-file')?.addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) importGeoJsonFile(f);
    e.target.value = '';
  });
  document.getElementById('btn-search-point')?.addEventListener('click', searchPointById);
  document.getElementById('btn-proximity')?.addEventListener('click', runProximitySearch);
  document.getElementById('search-point-id')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchPointById();
  });
}

window.SigSolsTools = { initTools, importGeoJsonFile, searchPointById, runProximitySearch };
