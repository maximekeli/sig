/**
 * Actions administration : entraînement IA, comparaison points.
 */
import { notifyError, notifySuccess } from './core/ui.js';
import { showLoading } from './core/ui.js';

export async function trainMlModel() {
  const algo = document.getElementById('adm-ml-algo')?.value || 'RandomForest';
  const msg = document.getElementById('adm-ml-status');
  showLoading(true);
  try {
    const r = await SigSolsAPI.api('/ml/train/', {
      method: 'POST',
      body: JSON.stringify({ algorithm: algo }),
    });
    if (msg) {
      msg.textContent = `F1=${r.f1_macro ?? '—'} · entraîné`;
    }
    notifySuccess('Modèle IA réentraîné.');
    SigSolsDashboard?.loadDashboard?.();
  } catch (e) {
    notifyError(e);
    if (msg) msg.textContent = e.message;
  } finally {
    showLoading(false);
  }
}

export async function comparePoints() {
  const raw = document.getElementById('adm-compare-ids')?.value?.trim();
  if (!raw) return;
  const ids = raw.split(/[\s,;]+/).map((x) => parseInt(x, 10)).filter(Boolean);
  if (ids.length < 2) {
    notifyError({ message: 'Indiquez au moins 2 IDs séparés par des virgules.' });
    return;
  }
  const el = document.getElementById('adm-compare-result');
  try {
    const rows = await Promise.all(
      ids.slice(0, 5).map((id) => SigSolsAPI.api(`/points/${id}/compare/`).catch(() => null)),
    );
    el.innerHTML = rows.filter(Boolean).map((r) => `
      <li>#${r.point_id || r.id} — pH ${r.ph} — ${r.soil_type} — fertilité ${r.fertility_class || '—'}</li>
    `).join('') || '<li>Aucune donnée.</li>';
    notifySuccess('Comparaison terminée.');
  } catch (e) {
    notifyError(e);
  }
}

export function initAdminPanel() {
  document.getElementById('btn-train-ml')?.addEventListener('click', trainMlModel);
  document.getElementById('btn-compare-points')?.addEventListener('click', comparePoints);
}

window.SigSolsAdminPanel = { initAdminPanel, trainMlModel, comparePoints };
