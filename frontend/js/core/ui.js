import { toast } from './toast.js';
import { t } from './i18n.js';

let loadingCount = 0;

export function showLoading(show = true) {
  const el = document.getElementById('global-loading');
  if (!el) return;
  loadingCount += show ? 1 : -1;
  if (loadingCount < 0) loadingCount = 0;
  el.classList.toggle('hidden', loadingCount === 0);
  el.setAttribute('aria-busy', loadingCount > 0 ? 'true' : 'false');
}

export function initConnectionBanner() {
  const banner = document.getElementById('connection-banner');
  if (!banner) return;
  const update = (online) => {
    banner.classList.toggle('hidden', online);
    banner.classList.toggle('offline', !online);
    banner.textContent = online ? t('online.banner') : t('offline.banner');
    if (online) banner.classList.add('flash');
    setTimeout(() => banner.classList.remove('flash'), 3000);
  };
  update(navigator.onLine);
  window.addEventListener('online', () => {
    update(true);
    window.SigSolsFeatures?.syncOfflineQueue?.();
  });
  window.addEventListener('offline', () => update(false));
}

export function initSidebarToggle() {
  const btn = document.getElementById('btn-sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (!btn || !sidebar) return;
  btn.addEventListener('click', () => {
    sidebar.classList.toggle('sidebar-open');
    btn.setAttribute('aria-expanded', sidebar.classList.contains('sidebar-open') ? 'true' : 'false');
  });
}

export function openModal(id) {
  const m = document.getElementById(id);
  if (!m) return;
  m.classList.remove('hidden');
  const focusable = m.querySelector('input, button, select, textarea');
  focusable?.focus();
}

export function closeModal(id) {
  document.getElementById(id)?.classList.add('hidden');
}

export function initModals() {
  document.querySelectorAll('[data-close-modal]').forEach((el) => {
    el.addEventListener('click', () => {
      const id = el.getAttribute('data-close-modal');
      if (id) closeModal(id);
    });
  });
}

export function notifyError(err) {
  toast(err?.message || String(err), 'error', 5500);
}

export function notifySuccess(msg) {
  toast(msg, 'success');
}
