/**
 * Panneau administration (IDs dédiés adm-* pour éviter les conflits avec la carte).
 */
import { notifyError, notifySuccess } from './core/ui.js';
import { showLoading } from './core/ui.js';

export async function trainMlModel() {
  const algo = document.getElementById('adm-ml-algo')?.value || 'RandomForest';
  const msg = document.getElementById('adm-ml-status');
  if (!confirm('Réentraîner le modèle IA ? (peut prendre 1–2 min)')) return;
  showLoading(true);
  try {
    const r = await SigSolsAPI.api('/ml/train/', {
      method: 'POST',
      body: JSON.stringify({ algorithm: algo }),
    });
    if (msg) msg.textContent = `F1 macro : ${r.f1_macro ?? '—'}`;
    notifySuccess('Modèle IA réentraîné.');
    SigSolsDashboard?.loadDashboard?.();
  } catch (e) {
    notifyError(e);
    if (msg) msg.textContent = e.message;
  } finally {
    showLoading(false);
  }
}

export async function triggerNasaIngest() {
  const msg = document.getElementById('adm-nasa-status');
  showLoading(true);
  try {
    const r = await SigSolsAPI.api('/nasa/ingest/', {
      method: 'POST',
      body: JSON.stringify({ enrich_points: true }),
    });
    if (msg) msg.textContent = `Ingestion : ${JSON.stringify(r.ingested || r).slice(0, 120)}…`;
    notifySuccess('Ingestion NASA lancée.');
  } catch (e) {
    notifyError(e);
    if (msg) msg.textContent = e.message;
  } finally {
    showLoading(false);
  }
}

let adminPanelReady = false;

export function initAdminPanel() {
  if (adminPanelReady) return;
  adminPanelReady = true;
  document.getElementById('btn-adm-train-ml')?.addEventListener('click', trainMlModel);
  document.getElementById('btn-adm-nasa-ingest')?.addEventListener('click', triggerNasaIngest);
}

window.SigSolsAdminPanel = { initAdminPanel, trainMlModel, triggerNasaIngest };
