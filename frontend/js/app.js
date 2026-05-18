document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach((b) => b.classList.remove('active'));
    const views = document.querySelectorAll('.view');
    views.forEach((v) => {
      v.classList.remove('active');
      v.style.animation = 'none';
    });
    btn.classList.add('active');
    const target = document.getElementById('view-' + btn.dataset.view);
    target.classList.add('active');
    void target.offsetWidth;
    target.style.animation = '';
    if (btn.dataset.view === 'dashboard') SigSolsDashboard.loadDashboard();
    if (btn.dataset.view === 'quiz') {
      SigSolsQuiz.loadLeaderboard();
      SigSolsQuiz.loadBadges();
    }
    if (btn.dataset.view === 'sheets') SigSolsQuiz.loadSheets();
    if (btn.dataset.view === 'admin') {
      SigSolsFeatures.loadAdminDashboard();
      SigSolsFeatures.loadPendingValidation?.();
    }
  });
});

document.getElementById('btn-apply-filters')?.addEventListener('click', () => SigSolsMap.loadSoilPoints());
document.getElementById('btn-export-geojson')?.addEventListener('click', () => {
  window.open('/api/v1/points/geojson/', '_blank');
});
document.getElementById('btn-export-csv')?.addEventListener('click', () => {
  window.open('/api/v1/points/export-csv/', '_blank');
});
document.getElementById('btn-predict')?.addEventListener('click', () => SigSolsMap.runPrediction());
document.getElementById('btn-location-toggle')?.addEventListener('click', () => SigSolsMap.toggleLiveLocation());
document.getElementById('share-location')?.addEventListener('change', (e) => {
  if (e.target.checked && SigSolsAPI.isAuthenticated()) SigSolsMap.startLiveLocation();
  else if (!e.target.checked) SigSolsMap.stopLiveLocation();
});
document.getElementById('btn-heatmap')?.addEventListener('click', () => {
  const m = SigSolsMap.getMap?.();
  if (m) SigSolsFeatures.toggleHeatmap(m, 'ph');
});
document.getElementById('btn-near-me')?.addEventListener('click', () => {
  const m = SigSolsMap.getMap?.();
  if (m) SigSolsFeatures.nearMe(m);
});
document.getElementById('btn-trajectory')?.addEventListener('click', () => {
  const m = SigSolsMap.getMap?.();
  if (m) SigSolsFeatures.showTrajectory(m);
});
document.getElementById('btn-zone-report')?.addEventListener('click', () => {
  const code = document.getElementById('adm-zone-code')?.value?.trim();
  if (code) window.open(`/api/v1/platform/reports/zone/${encodeURIComponent(code)}/`, '_blank');
});
document.getElementById('btn-quiz-start')?.addEventListener('click', () => SigSolsQuiz.startQuiz());
document.getElementById('btn-quiz-finish')?.addEventListener('click', () => SigSolsQuiz.finishQuiz());

window.addEventListener('online', () => SigSolsFeatures.syncOfflineQueue());

document.addEventListener('DOMContentLoaded', async () => {
  SigSolsMap.initMap();
  await SigSolsAuth.initAuth();
  SigSolsFeatures.applyPublicMode();
  if (SigSolsAPI.isAuthenticated()) {
    SigSolsMap.loadSoilPoints();
    SigSolsFeatures.loadAlerts();
    SigSolsFeatures.loadNotifications();
    SigSolsFeatures.connectWebSocket();
    SigSolsFeatures.syncOfflineQueue();
  }
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/frontend/sw.js').catch(() => {});
  }
});
