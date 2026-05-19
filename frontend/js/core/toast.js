/** Notifications toast non bloquantes. */
let container = null;

export function initToast() {
  if (container) return;
  container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container';
  container.setAttribute('aria-live', 'polite');
  container.setAttribute('aria-atomic', 'false');
  document.body.appendChild(container);
}

export function toast(message, type = 'info', duration = 4200) {
  initToast();
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.setAttribute('role', 'status');
  el.textContent = message;
  container.appendChild(el);
  requestAnimationFrame(() => el.classList.add('toast-visible'));
  const remove = () => {
    el.classList.remove('toast-visible');
    setTimeout(() => el.remove(), 320);
  };
  el.addEventListener('click', remove);
  setTimeout(remove, duration);
}
