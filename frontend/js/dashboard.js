import { formatMlF1, formatSmapCorrelation, renderSoilTypeRows } from './core/dashboardUtils.js';
import { showLoading } from './core/ui.js';
import { notifyError } from './core/ui.js';

let soilChart = null;
let fertilityChart = null;

function renderSoilChart(stats) {
  const canvas = document.getElementById('chart-soil-types-canvas');
  if (!canvas || typeof Chart === 'undefined') return;
  const rows = renderSoilTypeRows(stats);
  if (soilChart) soilChart.destroy();
  soilChart = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: rows.map((r) => r.label.split(' (')[0]),
      datasets: [{
        data: rows.map((r) => {
          const m = r.label.match(/\((\d+)\)/);
          return m ? parseInt(m[1], 10) : 0;
        }),
        backgroundColor: ['#2d8a52', '#c9a962', '#3b82f6', '#a855f7', '#f97316', '#64748b'],
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
    },
  });
}

function renderFertilityChart(stats) {
  const canvas = document.getElementById('chart-fertility-canvas');
  if (!canvas || typeof Chart === 'undefined' || !stats.fertility_distribution?.length) return;
  if (fertilityChart) fertilityChart.destroy();
  fertilityChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: stats.fertility_distribution.map((r) => r.fertility_class || '?'),
      datasets: [{
        label: 'Points',
        data: stats.fertility_distribution.map((r) => r.count),
        backgroundColor: ['#2d8a52', '#c9a962', '#dc2626'],
      }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
  });
}

async function loadDashboard() {
  showLoading(true);
  try {
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
    renderSoilChart(stats);
    const ul = document.getElementById('chart-soil-types');
    if (ul) {
      ul.innerHTML = '';
      renderSoilTypeRows(stats).forEach((row) => {
        const li = document.createElement('li');
        li.textContent = row.label;
        ul.appendChild(li);
      });
    }
    document.getElementById('smap-corr').textContent = formatSmapCorrelation(smap);
    renderFertilityChart(stats);
  } catch (e) {
    notifyError(e);
  } finally {
    showLoading(false);
  }
}

window.SigSolsDashboard = { loadDashboard };
