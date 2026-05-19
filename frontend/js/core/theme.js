/** Mode clair / sombre persisté. */
const KEY = 'sig_sols_theme';

export function getTheme() {
  return localStorage.getItem(KEY) || 'light';
}

export function applyTheme(theme) {
  const t = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem(KEY, t);
  const btn = document.getElementById('btn-theme');
  if (btn) btn.setAttribute('aria-pressed', t === 'dark' ? 'true' : 'false');
  btn?.classList.toggle('theme-dark-active', t === 'dark');
}

export function toggleTheme() {
  applyTheme(getTheme() === 'dark' ? 'light' : 'dark');
}

export function initTheme() {
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  const stored = localStorage.getItem(KEY);
  applyTheme(stored || (prefersDark ? 'dark' : 'light'));
}
