/**
 * Vidéos communauté & Shorts — upload, lecture, modération admin.
 */

const API = () => window.SigSolsAPI;
const ORIGIN = () => window.location.origin;

function mediaUrl(path) {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${ORIGIN()}${path.startsWith('/') ? '' : '/'}${path}`;
}

function statusLabel(status) {
  const map = {
    pending: 'En attente',
    published: 'Publié',
    rejected: 'Refusé',
  };
  return map[status] || status;
}

function statusClass(status) {
  return `video-status video-status--${status}`;
}

async function fetchPosts(kind) {
  const params = new URLSearchParams({
    kind,
    ordering: '-created_at',
  });
  const data = await API().api(`/videos/posts/?${params}`);
  return data.results ?? data;
}

function renderModerationActions(post) {
  if (!post.can_moderate || post.status !== 'pending') return '';
  return `
    <div class="video-mod-actions">
      <button type="button" class="btn-auth-primary btn-sm" data-action="approve" data-id="${post.id}">Publier</button>
      <button type="button" class="btn-auth-outline btn-sm" data-action="reject" data-id="${post.id}">Refuser</button>
    </div>`;
}

function renderVideoCard(post) {
  const src = mediaUrl(post.file_url);
  const thumb = post.thumbnail_url ? mediaUrl(post.thumbnail_url) : '';
  const poster = thumb ? ` poster="${thumb}"` : '';
  return `
    <article class="video-card" role="listitem" data-id="${post.id}">
      <div class="video-card-media">
        <video controls preload="metadata" src="${src}"${poster}></video>
        ${post.is_featured ? '<span class="video-badge">À la une</span>' : ''}
      </div>
      <div class="video-card-body">
        <h3>${escapeHtml(post.title)}</h3>
        <p class="video-meta">${escapeHtml(post.author_display)} · ${post.view_count} vues</p>
        <span class="${statusClass(post.status)}">${statusLabel(post.status)}</span>
        ${post.description ? `<p class="video-desc">${escapeHtml(post.description)}</p>` : ''}
        ${post.rejection_reason && post.status === 'rejected'
    ? `<p class="video-reject">${escapeHtml(post.rejection_reason)}</p>` : ''}
        ${renderModerationActions(post)}
      </div>
    </article>`;
}

function renderShortCard(post) {
  const src = mediaUrl(post.file_url);
  return `
    <article class="short-card" role="listitem" data-id="${post.id}">
      <video controls playsinline preload="metadata" src="${src}"></video>
      <div class="short-card-info">
        <strong>${escapeHtml(post.title)}</strong>
        <span>${escapeHtml(post.author_display)}</span>
        <span class="${statusClass(post.status)}">${statusLabel(post.status)}</span>
        ${renderModerationActions(post)}
      </div>
    </article>`;
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

function bindModeration(container) {
  container?.querySelectorAll('[data-action]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const action = btn.dataset.action;
      try {
        if (action === 'approve') {
          await API().api(`/videos/posts/${id}/approve/`, { method: 'POST' });
        } else {
          const reason = prompt('Motif du refus (optionnel) :') || '';
          await API().api(`/videos/posts/${id}/reject/`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
          });
        }
        window.SigSolsVideos.loadVideos();
        window.SigSolsVideos.loadShorts();
        window.SigSolsVideos.loadAdminPending?.();
      } catch (e) {
        alert(e.message || 'Erreur modération');
      }
    });
  });
}

function updateAuthPanels() {
  const authed = API()?.isAuthenticated?.();
  document.querySelectorAll('.auth-required').forEach((el) => {
    el.classList.toggle('hidden', !authed);
  });
  document.getElementById('videos-login-hint')?.classList.toggle('hidden', authed);
  document.getElementById('shorts-login-hint')?.classList.toggle('hidden', authed);
}

async function loadVideos() {
  updateAuthPanels();
  const grid = document.getElementById('videos-grid');
  const modBox = document.getElementById('videos-pending-admin');
  if (!grid) return;
  grid.innerHTML = '<p class="panel-lead">Chargement…</p>';
  try {
    const posts = await fetchPosts('video');
    if (!posts.length) {
      grid.innerHTML = '<p class="panel-lead">Aucune vidéo publiée pour le moment.</p>';
    } else {
      grid.innerHTML = posts.map(renderVideoCard).join('');
      bindModeration(grid);
    }
    const user = API().getUser?.();
    if (user?.role === 'admin' && modBox) {
      const pending = await API().api('/videos/posts/pending/');
      const list = pending.results ?? pending;
      modBox.innerHTML = list.length
        ? `<h3>Modération vidéos (${list.length})</h3>${list.map(renderVideoCard).join('')}`
        : '';
      modBox.classList.toggle('hidden', !list.length);
      bindModeration(modBox);
    } else if (modBox) {
      modBox.classList.add('hidden');
    }
  } catch (e) {
    grid.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

async function loadShorts() {
  updateAuthPanels();
  const feed = document.getElementById('shorts-feed');
  if (!feed) return;
  feed.innerHTML = '<p class="panel-lead">Chargement…</p>';
  try {
    const posts = await fetchPosts('short');
    feed.innerHTML = posts.length
      ? posts.map(renderShortCard).join('')
      : '<p class="panel-lead">Aucun short pour le moment.</p>';
    bindModeration(feed);
  } catch (e) {
    feed.innerHTML = `<p class="parcel-status">${escapeHtml(e.message)}</p>`;
  }
}

async function loadAdminPending() {
  const ul = document.getElementById('adm-videos-pending');
  if (!ul || API().getUser?.()?.role !== 'admin') return;
  try {
    const data = await API().api('/videos/posts/pending/');
    const list = data.results ?? data;
    ul.innerHTML = list.length
      ? list.map((p) => `<li>${escapeHtml(p.title)} (${p.kind}) — ${escapeHtml(p.author_username)}
          <button type="button" class="btn-sm" data-adm-approve="${p.id}">OK</button>
          <button type="button" class="btn-sm" data-adm-reject="${p.id}">Refuser</button></li>`).join('')
      : '<li>Aucune vidéo en attente</li>';
    ul.querySelectorAll('[data-adm-approve]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        await API().api(`/videos/posts/${btn.dataset.admApprove}/approve/`, { method: 'POST' });
        loadAdminPending();
      });
    });
    ul.querySelectorAll('[data-adm-reject]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        await API().api(`/videos/posts/${btn.dataset.admReject}/reject/`, {
          method: 'POST',
          body: JSON.stringify({ reason: 'Refusé depuis l’admin' }),
        });
        loadAdminPending();
      });
    });
  } catch {
    ul.innerHTML = '<li>Erreur chargement vidéos</li>';
  }
}

async function handleUpload(form, kind, msgEl) {
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!API().isAuthenticated()) {
      msgEl.textContent = 'Connectez-vous pour publier.';
      return;
    }
    const fd = new FormData();
    fd.append('kind', kind);
    fd.append('title', form.querySelector('[id$="-title"]')?.value?.trim() || 'Sans titre');
    const desc = form.querySelector('[id$="-desc"]')?.value?.trim();
    if (desc) fd.append('description', desc);
    const dur = form.querySelector('[id$="-duration"]')?.value;
    if (dur) fd.append('duration_seconds', dur);
    const fileInput = form.querySelector('input[type="file"][id$="-file"]');
    const thumbInput = form.querySelector('input[type="file"][id$="-thumb"]');
    if (!fileInput?.files?.[0]) {
      msgEl.textContent = 'Choisissez un fichier vidéo.';
      return;
    }
    fd.append('file', fileInput.files[0]);
    if (thumbInput?.files?.[0]) fd.append('thumbnail', thumbInput.files[0]);
    msgEl.textContent = 'Envoi en cours…';
    try {
      const res = await API().upload('/videos/posts/', fd);
      msgEl.textContent = res.status === 'published'
        ? 'Publié !'
        : 'Envoyé — en attente de validation par un admin.';
      form.reset();
      if (kind === 'video') loadVideos();
      else loadShorts();
    } catch (err) {
      msgEl.textContent = err.message || 'Échec de l’envoi';
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  handleUpload(
    document.getElementById('form-video-upload'),
    'video',
    document.getElementById('video-upload-msg'),
  );
  handleUpload(
    document.getElementById('form-short-upload'),
    'short',
    document.getElementById('short-upload-msg'),
  );
  window.addEventListener('sig-auth-changed', updateAuthPanels);
  updateAuthPanels();
});

window.SigSolsVideos = {
  loadVideos,
  loadShorts,
  loadAdminPending,
  updateAuthPanels,
};
