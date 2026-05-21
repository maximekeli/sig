/**
 * Hub fonctionnalités étendues — notifications, recherche, dashboard perso, etc.
 */

const API = () => window.SigSolsAPI;

export async function refreshNotificationBadge() {
  const badge = document.getElementById('notif-badge');
  if (!badge || !API()?.isAuthenticated?.()) {
    badge?.classList.add('hidden');
    return;
  }
  try {
    const d = await API().api('/platform/notifications/unread-count/');
    const n = d.unread_count || 0;
    badge.textContent = n > 99 ? '99+' : String(n);
    badge.classList.toggle('hidden', n === 0);
  } catch {
    badge.classList.add('hidden');
  }
}

export async function loadNotificationPanel() {
  const panel = document.getElementById('notif-panel-list');
  if (!panel) return;
  try {
    const data = await API().api('/platform/notifications/');
    const list = Array.isArray(data) ? data : data.results || [];
    panel.innerHTML = list.length
      ? list.map((n) => `
        <li class="${n.is_read ? '' : 'unread'}">
          <strong>${escapeHtml(n.title)}</strong>
          <p>${escapeHtml(n.message)}</p>
          ${!n.is_read ? `<button type="button" class="btn-tiny" data-notif-read="${n.id}">Lu</button>` : ''}
        </li>`).join('')
      : '<li>Aucune notification</li>';
    panel.querySelectorAll('[data-notif-read]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        await API().api(`/platform/notifications/${btn.dataset.notifRead}/read/`, { method: 'POST' });
        loadNotificationPanel();
        refreshNotificationBadge();
      });
    });
  } catch {
    panel.innerHTML = '<li>Indisponible</li>';
  }
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

export async function runGlobalSearch(q) {
  const box = document.getElementById('global-search-results');
  if (!box) return;
  if (!q || q.length < 2) {
    box.classList.add('hidden');
    return;
  }
  const data = await API().api(`/platform/search/?q=${encodeURIComponent(q)}`);
  box.innerHTML = (data.results || []).map((r) => `
    <button type="button" class="global-search-item" data-link="${escapeHtml(r.link)}">
      <span class="global-search-type">${r.type}</span>
      <strong>${escapeHtml(r.title)}</strong>
      <small>${escapeHtml(r.subtitle || '')}</small>
    </button>`).join('') || '<p class="panel-lead">Aucun résultat</p>';
  box.classList.remove('hidden');
  box.querySelectorAll('[data-link]').forEach((btn) => {
    btn.addEventListener('click', () => {
      window.location.href = btn.dataset.link;
      box.classList.add('hidden');
    });
  });
}

export async function loadPersonalDashboard() {
  const el = document.getElementById('my-dashboard-content');
  if (!el || !API()?.isAuthenticated?.()) return;
  el.innerHTML = '<p class="panel-lead">Chargement…</p>';
  try {
    const d = await API().api('/platform/me/dashboard/');
    el.innerHTML = `
      <div class="my-dash-grid">
        <article class="kpi-card"><h3>Points sol</h3><p>${d.soil_points_submitted}</p></article>
        <article class="kpi-card"><h3>Vidéos publiées</h3><p>${d.videos?.published ?? 0}</p></article>
        <article class="kpi-card"><h3>Quiz terminés</h3><p>${d.quiz?.sessions_completed ?? 0}</p></article>
        <article class="kpi-card"><h3>Meilleur score</h3><p>${d.quiz?.best_score ?? 0}</p></article>
        <article class="kpi-card"><h3>Abonnés</h3><p>${d.social?.followers ?? 0}</p></article>
        <article class="kpi-card"><h3>Abonnements</h3><p>${d.social?.following ?? 0}</p></article>
      </div>
      <p><strong>Badges :</strong> ${(d.quiz?.badges || []).join(', ') || '—'}</p>`;
  } catch (e) {
    el.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

export async function loadLearningPath() {
  const el = document.getElementById('learning-path-steps');
  if (!el || !API()?.isAuthenticated?.()) return;
  const data = await API().api('/education/quiz/learning-path/');
  el.innerHTML = (data.steps || []).map((s) => `
    <li class="${s.done ? 'done' : ''}">${s.done ? '✓' : '○'} ${escapeHtml(s.title)}</li>`).join('');
  const prog = document.getElementById('learning-path-progress');
  if (prog) prog.textContent = `${data.progress_percent}%`;
}

export async function loadWeeklyChallenge() {
  const el = document.getElementById('weekly-challenge-box');
  if (!el || !API()?.isAuthenticated?.()) return;
  const d = await API().api('/education/quiz/weekly-challenge/');
  el.innerHTML = `<p>${escapeHtml(d.challenge)}</p>
    <p>Sessions cette semaine : <strong>${d.sessions_this_week}</strong> / ${d.target_sessions}</p>`;
}

export async function loadModerationJournal() {
  const ul = document.getElementById('adm-mod-journal');
  if (!ul) return;
  const d = await API().api('/platform/moderation/journal/');
  ul.innerHTML = (d.results || []).map((i) => `
    <li>[${i.kind}] ${escapeHtml(i.title)} — ${escapeHtml(i.author)}
      ${i.kind === 'comment' ? `<button class="btn-sm" data-ai-mod="${i.id}">IA</button>` : ''}
    </li>`).join('') || '<li>Rien en attente</li>';
  ul.querySelectorAll('[data-ai-mod]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const r = await API().api(`/videos/comments/${btn.dataset.aiMod}/ai-check/`, { method: 'POST' });
      alert(r.suggested_hide ? `Suggéré masquer : ${r.flags.join(', ')}` : 'OK');
    });
  });
}

export async function loadStories() {
  const strip = document.getElementById('stories-strip');
  if (!strip || !API()?.isAuthenticated?.()) return;
  const list = await API().api('/videos/stories/');
  strip.innerHTML = (list || []).map((s) => `
    <div class="story-bubble" title="${escapeHtml(s.caption)}">
      <strong>${escapeHtml(s.author_display)}</strong>
    </div>`).join('') || '';
}

export function initShortsVertical() {
  const feed = document.getElementById('shorts-feed');
  if (!feed) return;
  feed.classList.add('shorts-feed--vertical');
  let idx = 0;
  const cards = () => [...feed.querySelectorAll('.short-card')];
  feed.addEventListener('wheel', (e) => {
    if (!feed.classList.contains('shorts-feed--vertical')) return;
    const list = cards();
    if (list.length < 2) return;
    e.preventDefault();
    idx = Math.max(0, Math.min(list.length - 1, idx + (e.deltaY > 0 ? 1 : -1)));
    list[idx]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, { passive: false });
}

export async function checkAlertsNearMe(lat, lon) {
  const box = document.getElementById('alerts-near-me');
  if (!box) return;
  const d = await API().api(`/platform/alerts/near/?lat=${lat}&lon=${lon}&radius_km=30`);
  box.innerHTML = d.count
    ? d.alerts.map((a) => `<li>${escapeHtml(a.message)} (${a.distance_km} km)</li>`).join('')
    : '<li>Aucune alerte à proximité</li>';
}

export function initFeaturesHub() {
  document.getElementById('btn-notif-toggle')?.addEventListener('click', () => {
    document.getElementById('notif-panel')?.classList.toggle('hidden');
    loadNotificationPanel();
  });
  document.getElementById('btn-notif-mark-all')?.addEventListener('click', async () => {
    await API().api('/platform/notifications/mark-all-read/', { method: 'POST' });
    loadNotificationPanel();
    refreshNotificationBadge();
  });
  let searchTimer;
  document.getElementById('global-search-input')?.addEventListener('input', (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => runGlobalSearch(e.target.value.trim()), 300);
  });
  document.getElementById('btn-ministry-report')?.addEventListener('click', () => {
    window.open('/api/v1/platform/reports/ministry/?region=Maritime', '_blank');
  });
  document.getElementById('btn-import-users')?.addEventListener('change', async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    const r = await API().upload('/platform/admin/import/users/', fd);
    alert(`${r.created} utilisateur(s) créé(s)`);
  });
  document.getElementById('form-story-upload')?.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.target);
    await API().upload('/videos/stories/', fd);
    loadStories();
    ev.target.reset();
  });
  document.getElementById('form-dm-send')?.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const to = document.getElementById('dm-to')?.value?.trim();
    const text = document.getElementById('dm-text')?.value?.trim();
    await API().api('/auth/messages/', {
      method: 'POST',
      body: JSON.stringify({ to, text }),
    });
    document.getElementById('dm-text').value = '';
    loadDirectMessages();
  });
  document.getElementById('btn-nasa-timeseries')?.addEventListener('click', async () => {
    const id = document.getElementById('nasa-ts-point-id')?.value;
    const out = document.getElementById('nasa-timeseries-out');
    if (!id || !out) return;
    try {
      const d = await API().api(`/spatial/ndvi-timeseries/${id}/`);
      out.textContent = JSON.stringify(d, null, 2);
    } catch (e) {
      out.textContent = e.message || 'Erreur';
    }
  });
  initShortsVertical();
  if (API()?.isAuthenticated?.()) {
    refreshNotificationBadge();
    setInterval(refreshNotificationBadge, 60000);
  }
}

export async function loadDirectMessages() {
  const ul = document.getElementById('dm-thread');
  if (!ul || !API()?.isAuthenticated?.()) return;
  const withUser = document.getElementById('dm-to')?.value?.trim();
  const q = withUser ? `?with=${encodeURIComponent(withUser)}` : '';
  const d = await API().api(`/auth/messages/${q}`);
  ul.innerHTML = (d.messages || []).map((m) => `
    <li class="${m.is_mine ? 'dm-mine' : ''}"><strong>${escapeHtml(m.from)}</strong>: ${escapeHtml(m.text)}</li>`).join('');
}

window.SigSolsFeaturesHub = {
  initFeaturesHub,
  refreshNotificationBadge,
  loadPersonalDashboard,
  loadLearningPath,
  loadWeeklyChallenge,
  loadModerationJournal,
  loadStories,
  loadDirectMessages,
  checkAlertsNearMe,
  runGlobalSearch,
};

document.addEventListener('DOMContentLoaded', initFeaturesHub);
