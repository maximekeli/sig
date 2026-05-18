document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach((b) => b.classList.remove('active'));
    document.querySelectorAll('.view').forEach((v) => v.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('view-' + btn.dataset.view).classList.add('active');
    if (btn.dataset.view === 'dashboard') SigSolsDashboard.loadDashboard();
    if (btn.dataset.view === 'quiz') {
      SigSolsQuiz.loadLeaderboard();
      SigSolsQuiz.loadBadges();
    }
    if (btn.dataset.view === 'sheets') SigSolsQuiz.loadSheets();
  });
});

document.getElementById('btn-login').addEventListener('click', async () => {
  try {
    await SigSolsAPI.login(
      document.getElementById('login-user').value,
      document.getElementById('login-pass').value,
    );
    alert('Connecté.');
    SigSolsMap.loadSoilPoints();
    const share = document.getElementById('share-location')?.checked;
    if (share) SigSolsMap.startLiveLocation();
  } catch (e) {
    alert('Erreur: ' + e.message);
  }
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
  if (e.target.checked && SigSolsAPI.getToken()) SigSolsMap.startLiveLocation();
  else if (!e.target.checked) SigSolsMap.stopLiveLocation();
});
document.getElementById('btn-quiz-start')?.addEventListener('click', () => SigSolsQuiz.startQuiz());
document.getElementById('btn-quiz-finish')?.addEventListener('click', () => SigSolsQuiz.finishQuiz());

document.addEventListener('DOMContentLoaded', () => {
  SigSolsMap.initMap();
  if (SigSolsAPI.getToken()) SigSolsMap.loadSoilPoints();
});
