/**
 * Micro-interactions : ripple sur boutons, classes de chargement, ré-animation des grilles.
 */

function addRipple(el, ev) {
  if (!el.classList.contains('btn-ripple')) el.classList.add('btn-ripple');
  const rect = el.getBoundingClientRect();
  const dot = document.createElement('span');
  dot.className = 'ripple-dot';
  dot.style.left = `${ev.clientX - rect.left}px`;
  dot.style.top = `${ev.clientY - rect.top}px`;
  el.appendChild(dot);
  dot.addEventListener('animationend', () => dot.remove());
}

function initRipples() {
  const selectors = [
    '.btn-auth-primary',
    '.btn-quiz-start',
    '.btn-parcel-analyze',
    '.nav-btn',
    '.community-tab',
    '.btn-sheet-read',
  ].join(', ');
  document.addEventListener('click', (e) => {
    const btn = e.target.closest(selectors);
    if (btn) addRipple(btn, e);
  });
}

/** Réapplique l’animation d’entrée sur les enfants d’une grille. */
export function refreshStagger(container) {
  if (!container) return;
  container.classList.add('animate-stagger');
  const children = [...container.children];
  children.forEach((child, i) => {
    child.style.animation = 'none';
    void child.offsetWidth;
    child.style.animation = '';
    child.style.animationDelay = `${(i + 1) * 0.06}s`;
  });
}

export function setLoadingState(container, loading) {
  if (!container) return;
  container.classList.toggle('is-loading', loading);
  if (loading && !container.querySelector('.skeleton-card')) {
    const sk = document.createElement('div');
    sk.className = 'skeleton-card';
    sk.setAttribute('aria-hidden', 'true');
    container.dataset.skeleton = '1';
    container.prepend(sk);
  } else if (!loading) {
    container.querySelector('.skeleton-card')?.remove();
    delete container.dataset.skeleton;
  }
}

export function initAnimations() {
  initRipples();
  document.querySelectorAll('.videos-grid, .shorts-feed, #sheets-list, .community-feed, .dashboard-grid')
    .forEach((el) => el.classList.add('animate-stagger'));
}

document.addEventListener('DOMContentLoaded', initAnimations);

window.SigSolsAnimations = {
  initAnimations,
  refreshStagger,
  setLoadingState,
};
