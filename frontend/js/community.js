/**
 * Communauté — fil d’abonnements, profils publics, favoris, recherche utilisateurs.
 */

const API = () => window.SigSolsAPI;
const ORIGIN = () => window.location.origin;

const CATEGORY_LABELS = {
  sols: 'Sols & agriculture',
  nasa: 'NASA & satellite',
  sig: 'SIG & cartographie',
  formation: 'Formation',
  autre: 'Autre',
};

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

function mediaUrl(path) {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${ORIGIN()}${path.startsWith('/') ? '' : '/'}${path}`;
}

function avatarHtml(photoUrl, name, size = 48) {
  const initial = (name?.[0] || '?').toUpperCase();
  const src = photoUrl ? mediaUrl(photoUrl) : '';
  if (src) {
    return `<img class="community-avatar" src="${src}" alt="" width="${size}" height="${size}" />`;
  }
  return `<span class="community-avatar community-avatar--ph" style="width:${size}px;height:${size}px">${escapeHtml(initial)}</span>`;
}

export async function toggleFavorite(targetType, targetId) {
  if (!API().isAuthenticated()) {
    alert('Connectez-vous pour enregistrer un favori.');
    return false;
  }
  const body = JSON.stringify({ target_type: targetType, target_id: targetId });
  try {
    await API().api('/auth/favorites/', { method: 'POST', body });
    return true;
  } catch (e) {
    if (/already|200/.test(String(e.message))) return true;
    throw e;
  }
}

export async function removeFavorite(targetType, targetId) {
  await API().api('/auth/favorites/', {
    method: 'DELETE',
    body: JSON.stringify({ target_type: targetType, target_id: targetId }),
  });
}

export async function isFavorite(targetType, targetId) {
  if (!API().isAuthenticated()) return false;
  const data = await API().api('/auth/favorites/');
  return (data.results || []).some(
    (f) => f.target_type === targetType && f.target_id === targetId,
  );
}

function navigateToView(viewName) {
  const btn = document.querySelector(`.nav-btn[data-view="${viewName}"]`);
  if (btn) btn.click();
  else {
    document.querySelectorAll('.view').forEach((v) => v.classList.remove('active'));
    document.getElementById(`view-${viewName}`)?.classList.add('active');
  }
}

export function openPublicProfile(username) {
  if (!username) return;
  const params = new URLSearchParams(window.location.search);
  params.set('view', 'community');
  params.set('user', username);
  const url = `${window.location.pathname}?${params}`;
  window.history.replaceState({}, '', url);
  navigateToView('community');
  loadPublicProfile(username);
}

function renderFeedPost(post) {
  const cat = CATEGORY_LABELS[post.category] || post.category || '';
  const src = mediaUrl(post.file_url);
  const thumb = post.thumbnail_url ? mediaUrl(post.thumbnail_url) : '';
  const poster = thumb ? ` poster="${thumb}"` : '';
  const authorLink = post.author_username
    ? `<button type="button" class="btn-link community-author-link" data-username="${escapeHtml(post.author_username)}">${escapeHtml(post.author_display)}</button>`
    : escapeHtml(post.author_display);
  return `
    <article class="community-feed-card" data-post-id="${post.id}">
      <div class="community-feed-media">
        <video controls preload="metadata" src="${src}"${poster}></video>
      </div>
      <div class="community-feed-body">
        <h3>${escapeHtml(post.title)}</h3>
        ${cat ? `<span class="video-cat-badge">${escapeHtml(cat)}</span>` : ''}
        <p class="video-meta">${authorLink} · ${post.view_count ?? 0} vues</p>
        <div class="community-feed-actions">
          <button type="button" class="btn-auth-outline btn-sm" data-share-video="${post.id}">Partager</button>
          <button type="button" class="btn-auth-outline btn-sm" data-fav-video="${post.id}">☆ Favori</button>
        </div>
      </div>
    </article>`;
}

async function loadFollowingFeed() {
  const box = document.getElementById('community-feed');
  if (!box) return;
  if (!API().isAuthenticated()) {
    box.innerHTML = '<p class="panel-lead">Connectez-vous pour voir le fil de vos abonnements.</p>';
    return;
  }
  window.SigSolsAnimations?.setLoadingState?.(box, true);
  box.innerHTML = '<p class="panel-lead">Chargement du fil…</p>';
  try {
    const data = await API().api('/auth/feed/');
    const posts = data.results || [];
    box.innerHTML = posts.length
      ? posts.map(renderFeedPost).join('')
      : '<p class="panel-lead">Aucune publication — suivez des membres via la recherche.</p>';
    box.classList.add('animate-stagger');
    window.SigSolsAnimations?.refreshStagger?.(box);
    bindCommunityActions(box);
    window.SigSolsAnimations?.setLoadingState?.(box, false);
  } catch (e) {
    box.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

async function loadFavoritesList() {
  const box = document.getElementById('community-favorites');
  if (!box) return;
  if (!API().isAuthenticated()) {
    box.innerHTML = '<p class="panel-lead">Connectez-vous pour voir vos favoris.</p>';
    return;
  }
  box.innerHTML = '<p class="panel-lead">Chargement…</p>';
  try {
    const data = await API().api('/auth/favorites/');
    const items = data.results || [];
    if (!items.length) {
      box.innerHTML = '<p class="panel-lead">Aucun favori — ajoutez-en depuis les vidéos ou fiches.</p>';
      return;
    }
    box.innerHTML = items.map((item) => {
      if (item.video) {
        return `<div class="community-fav-item">
          <strong>Vidéo</strong> — ${escapeHtml(item.video.title)}
          <button type="button" class="btn-link" data-open-video="${item.video.id}">Voir</button>
          <button type="button" class="btn-link" data-unfav="video" data-id="${item.target_id}">Retirer</button>
        </div>`;
      }
      if (item.sheet) {
        return `<div class="community-fav-item">
          <strong>Fiche</strong> — ${escapeHtml(item.sheet.title)}
          <button type="button" class="btn-link" data-open-sheets="1">Fiches</button>
          <button type="button" class="btn-link" data-unfav="sheet" data-id="${item.target_id}">Retirer</button>
        </div>`;
      }
      return '';
    }).join('');
    bindFavoritesActions(box);
  } catch (e) {
    box.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

async function searchUsers(q) {
  const box = document.getElementById('community-search-results');
  if (!box) return;
  if (!q || q.length < 2) {
    box.innerHTML = '<p class="panel-lead">Saisissez au moins 2 caractères.</p>';
    return;
  }
  box.innerHTML = '<p class="panel-lead">Recherche…</p>';
  try {
    const data = await API().api(`/auth/users/search/?q=${encodeURIComponent(q)}`);
    const rows = data.results || [];
    box.innerHTML = rows.length
      ? `<ul class="community-user-list">${rows.map((u) => `
          <li>
            ${avatarHtml(u.profile_photo_url, u.display_name, 36)}
            <button type="button" class="btn-link community-profile-btn" data-username="${escapeHtml(u.username)}">
              ${escapeHtml(u.display_name)} <small>@${escapeHtml(u.username)}</small>
            </button>
          </li>`).join('')}</ul>`
      : '<p class="panel-lead">Aucun utilisateur trouvé.</p>';
    box.querySelectorAll('.community-profile-btn').forEach((btn) => {
      btn.addEventListener('click', () => openPublicProfile(btn.dataset.username));
    });
  } catch (e) {
    box.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

export async function loadPublicProfile(username) {
  const panel = document.getElementById('community-public-profile');
  const feedPanel = document.getElementById('community-tab-feed');
  if (!panel) return;
  feedPanel?.classList.add('hidden');
  panel.classList.remove('hidden');
  panel.innerHTML = '<p class="panel-lead">Chargement du profil…</p>';
  try {
    const data = await API().api(`/auth/users/${encodeURIComponent(username)}/public/`);
    const u = data.user;
    const stats = data.stats || {};
    const badges = (data.badges || []).map((b) => b.badge).join(', ') || 'Aucun badge';
    const followBtn = API().isAuthenticated() && !data.is_self
      ? `<button type="button" id="btn-follow-user" class="btn-auth-primary" data-username="${escapeHtml(username)}" data-following="${data.is_following}">
          ${data.is_following ? 'Ne plus suivre' : 'Suivre'}
        </button>`
      : '';
    const postsHtml = (data.posts || []).length
      ? data.posts.map(renderFeedPost).join('')
      : '<p class="panel-lead">Aucune publication publiée.</p>';
    panel.innerHTML = `
      <button type="button" class="btn-link" id="btn-back-community">← Retour</button>
      <div class="community-profile-header">
        ${avatarHtml(u.profile_photo_url, u.first_name || u.username, 72)}
        <div>
          <h3>${escapeHtml(u.first_name || u.username)} ${escapeHtml(u.last_name || '')}</h3>
          <p>@${escapeHtml(u.username)}</p>
          ${u.bio ? `<p class="profile-bio">${escapeHtml(u.bio)}</p>` : ''}
          <p class="profile-stats-line">
            ${stats.videos ?? 0} vidéos · ${stats.shorts ?? 0} shorts ·
            ${stats.followers ?? 0} abonnés · ${stats.following ?? 0} abonnements
          </p>
          <p><strong>Badges quiz :</strong> ${escapeHtml(badges)}</p>
          ${followBtn}
        </div>
      </div>
      <h4>Publications</h4>
      <div class="community-profile-posts">${postsHtml}</div>`;
    document.getElementById('btn-back-community')?.addEventListener('click', () => {
      panel.classList.add('hidden');
      feedPanel?.classList.remove('hidden');
      const params = new URLSearchParams(window.location.search);
      params.delete('user');
      window.history.replaceState({}, '', `${window.location.pathname}?${params}`);
    });
    const fbtn = document.getElementById('btn-follow-user');
    fbtn?.addEventListener('click', async () => {
      const un = fbtn.dataset.username;
      const following = fbtn.dataset.following === 'true';
      try {
        if (following) {
          await API().api(`/auth/users/${encodeURIComponent(un)}/follow/`, { method: 'DELETE' });
          fbtn.dataset.following = 'false';
          fbtn.textContent = 'Suivre';
        } else {
          await API().api(`/auth/users/${encodeURIComponent(un)}/follow/`, { method: 'POST', body: '{}' });
          fbtn.dataset.following = 'true';
          fbtn.textContent = 'Ne plus suivre';
        }
      } catch (err) {
        alert(err.message || 'Erreur');
      }
    });
    bindCommunityActions(panel);
  } catch (e) {
    panel.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

function bindCommunityActions(container) {
  container?.querySelectorAll('[data-username]').forEach((btn) => {
    if (btn.classList.contains('community-author-link') || btn.classList.contains('community-profile-btn')) {
      btn.addEventListener('click', () => openPublicProfile(btn.dataset.username));
    }
  });
  container?.querySelectorAll('[data-share-video]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.shareVideo;
      const url = `${ORIGIN()}/?view=videos&video=${id}`;
      navigator.clipboard?.writeText(url).then(
        () => window.SigSolsFeatures?.notifySuccess?.('Lien copié dans le presse-papiers.'),
        () => prompt('Copiez ce lien :', url),
      );
    });
  });
  container?.querySelectorAll('[data-fav-video]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      try {
        await toggleFavorite('video', parseInt(btn.dataset.favVideo, 10));
        btn.textContent = '★ Favori enregistré';
        window.SigSolsFeatures?.notifySuccess?.('Ajouté aux favoris.');
      } catch (e) {
        alert(e.message || 'Erreur');
      }
    });
  });
}

function bindFavoritesActions(container) {
  container?.querySelectorAll('[data-unfav]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await removeFavorite(btn.dataset.unfav, parseInt(btn.dataset.id, 10));
      loadFavoritesList();
    });
  });
  container?.querySelector('[data-open-sheets]')?.addEventListener('click', () => {
    navigateToView('sheets');
  });
  container?.querySelectorAll('[data-open-video]').forEach((btn) => {
    btn.addEventListener('click', () => {
      navigateToView('videos');
      setTimeout(() => {
        document.querySelector(`.video-card[data-id="${btn.dataset.openVideo}"]`)?.scrollIntoView({ behavior: 'smooth' });
      }, 400);
    });
  });
}

function initCommunityTabs() {
  document.querySelectorAll('[data-community-tab]').forEach((tab) => {
    tab.addEventListener('click', () => {
      const name = tab.dataset.communityTab;
      document.querySelectorAll('[data-community-tab]').forEach((t) => {
        t.classList.toggle('active', t.dataset.communityTab === name);
      });
      document.querySelectorAll('[data-community-panel]').forEach((p) => {
        p.classList.toggle('hidden', p.dataset.communityPanel !== name);
      });
      if (name === 'feed') loadFollowingFeed();
      if (name === 'favorites') loadFavoritesList();
      document.getElementById('community-public-profile')?.classList.add('hidden');
    });
  });
}

export function loadCommunity() {
  const user = new URLSearchParams(window.location.search).get('user');
  if (user) {
    loadPublicProfile(user);
    return;
  }
  document.getElementById('community-public-profile')?.classList.add('hidden');
  document.getElementById('community-tab-feed')?.classList.remove('hidden');
  const active = document.querySelector('[data-community-tab].active');
  if (active?.dataset.communityTab === 'favorites') loadFavoritesList();
  else loadFollowingFeed();
}

document.addEventListener('click', (e) => {
  const mapLink = e.target.closest('.map-profile-link');
  if (mapLink?.dataset.username) {
    openPublicProfile(mapLink.dataset.username);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  initCommunityTabs();
  document.getElementById('btn-community-search')?.addEventListener('click', () => {
    const q = document.getElementById('community-search-input')?.value?.trim();
    searchUsers(q);
  });
  document.getElementById('community-search-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      searchUsers(e.target.value?.trim());
    }
  });
});

window.SigSolsCommunity = {
  loadCommunity,
  loadPublicProfile,
  openPublicProfile,
  toggleFavorite,
  loadFollowingFeed,
  loadFavoritesList,
  searchUsers,
};
