import { formatMlF1, formatSmapCorrelation, renderSoilTypeRows } from './core/dashboardUtils.js';

async function loadDashboard() {
  const [stats, ml, smap] = await Promise.all([
    SigSolsAPI.api('/dashboard/stats/'),
    SigSolsAPI.api('/ml/metrics/').catch(() => ({})),
    SigSolsAPI.api('/spatial/smap-correlation/'),
  ]);
  document.getElementById('kpi-points').textContent = stats.total_points;
  document.getElementById('kpi-ph').textContent = stats.avg_ph;
  document.getElementById('kpi-ndvi').textContent = stats.avg_ndvi;
  document.getElementById('kpi-degraded').textContent = stats.degraded_zones_count;
  document.getElementById('kpi-ml').textContent = formatMlF1(ml.f1_macro);
  const ul = document.getElementById('chart-soil-types');
  ul.innerHTML = '';
  renderSoilTypeRows(stats).forEach((row) => {
    const li = document.createElement('li');
    li.textContent = row.label;
    ul.appendChild(li);
  });
  document.getElementById('smap-corr').textContent = formatSmapCorrelation(smap);
}

window.SigSolsDashboard = { loadDashboard };
