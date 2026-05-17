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
  document.getElementById('kpi-ml').textContent = ml.f1_macro
    ? `${(ml.f1_macro * 100).toFixed(1)}% (F1)`
    : '—';
  const ul = document.getElementById('chart-soil-types');
  ul.innerHTML = '';
  (stats.by_soil_type || []).forEach((row) => {
    const li = document.createElement('li');
    li.textContent = `${row.soil_type}: ${row.count}`;
    ul.appendChild(li);
  });
  document.getElementById('smap-corr').textContent = smap.r_squared != null
    ? `R² = ${smap.r_squared} (n=${smap.sample_size})`
    : smap.message || '—';
}

window.SigSolsDashboard = { loadDashboard };
