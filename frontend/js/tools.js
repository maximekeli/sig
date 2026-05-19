/**
 * Outils avancés : import, proximité, recherche point, comparaison.
 */
import { toast } from './core/toast.js';
import { notifyError, notifySuccess, showLoading } from './core/ui.js';

let proximityLayer = null;

export async function importSoilFile(file) {
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  showLoading(true);
  try {
    const r = await SigSolsAPI.upload('/points/import_data/', form);
    notifySuccess(`${r.created} point(s) importé(s).`);
    SigSolsMap.loadSoilPoints();
  } catch (e) {
    notifyError(e);
  } finally {
    showLoading(false);
  }
}

export async function searchProximity(map) {
  if (!navigator.geolocation) {
    toast('GPS indisponible.', 'error');
    return;
  }
  const radius = parseInt(document.getElementById('proximity-radius')?.value || '5000', 10);
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const { latitude, longitude } = pos.coords;
    map.setView([latitude, longitude], 13);
    showLoading(true);
    try {
      const r = await SigSolsAPI.api(
        `/spatial/proximity/?lon=${longitude}&lat=${latitude}&radius_m=${radius}`,
      );
      if (proximityLayer) map.removeLayer(proximityLayer);
      proximityLayer = L.layerGroup().addTo(map);
      L.circleMarker([latitude, longitude], {
        radius: 10, color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.9,
      }).bindPopup('<strong>Vous</strong>').addTo(proximityLayer);
      L.circle([latitude, longitude], {
        radius, color: '#3b82f6', fillOpacity: 0.05, weight: 1, dashArray: '4',
      }).addTo(proximityLayer);
      (r.results || []).forEach((p) => {
        L.circleMarker([p.lat, p.lon], {
          radius: 7, color: '#c9a962', fillOpacity: 0.85,
        })
          .bindPopup(`#${p.id} · pH ${p.ph} · ${p.distance_m} m`)
          .addTo(proximityLayer);
      });
      notifySuccess(`${r.count} point(s) dans ${radius / 1000} km.`);
    } catch (e) {
      notifyError(e);
    } finally {
      showLoading(false);
    }
  }, () => toast('Position refusée.', 'error'));
}

export async function focusPointById() {
  const id = document.getElementById('search-point-id')?.value?.trim();
  if (!id) return;
  showLoading(true);
  try {
    const p = await SigSolsAPI.api(`/points/${id}/`);
    const lon = p.location?.coordinates?.[0] ?? p.lon;
    const lat = p.location?.coordinates?.[1] ?? p.lat;
    const map = SigSolsMap.getMap();
    if (map && lat != null && lon != null) {
      map.setView([lat, lon], 15);
      L.circleMarker([lat, lon], {
        radius: 12, color: '#dc2626', fillColor: '#dc2626', fillOpacity: 0.9,
      })
        .addTo(map)
        .bindPopup(`<strong>Point #${p.id}</strong><br/>pH ${p.ph}`)
        .openPopup();
    }
    notifySuccess(`Point #${id} localisé.`);
  } catch (e) {
    notifyError(e);
  } finally {
    showLoading(false);
  }
}

export async function comparePoints() {
  const a = document.getElementById('compare-id-a')?.value?.trim();
  const b = document.getElementById('compare-id-b')?.value?.trim();
  if (!a || !b) return;
  const el = document.getElementById('compare-result');
  showLoading(true);
  try {
    const data = await SigSolsAPI.api(`/points/compare/?a=${a}&b=${b}`);
    if (el) {
      el.classList.remove('hidden');
      el.innerHTML = `
        <p><strong>#${data.point_a?.id}</strong> pH ${data.point_a?.ph} · NDVI ${data.point_a?.ndvi_3m_avg ?? '—'}</p>
        <p><strong>#${data.point_b?.id}</strong> pH ${data.point_b?.ph} · NDVI ${data.point_b?.ndvi_3m_avg ?? '—'}</p>
        <p>Δ pH : ${data.delta_ph ?? '—'} · Distance : ${data.distance_m ?? '—'} m</p>`;
    }
    notifySuccess('Comparaison terminée.');
  } catch (e) {
    notifyError(e);
  } finally {
    showLoading(false);
  }
}

export function initTools() {
  document.getElementById('import-file')?.addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) importSoilFile(f);
    e.target.value = '';
  });
  document.getElementById('btn-proximity-search')?.addEventListener('click', () => {
    const m = SigSolsMap.getMap?.();
    if (m) searchProximity(m);
  });
  document.getElementById('btn-search-point')?.addEventListener('click', focusPointById);
  document.getElementById('btn-compare-points')?.addEventListener('click', comparePoints);
}

window.SigSolsTools = {
  importSoilFile,
  searchProximity,
  focusPointById,
  comparePoints,
  initTools,
};
