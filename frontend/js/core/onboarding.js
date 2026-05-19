const KEY = 'sig_sols_onboarding_done';

const STEPS = [
  { title: 'Carte interactive', text: 'Filtrez les points de sol, superposez les couches NASA et analysez une parcelle.' },
  { title: 'Terrain & GPS', text: 'Agents : partagez votre position et ajoutez des points (même hors ligne).' },
  { title: 'IA & tableau de bord', text: 'Prédisez la fertilité et consultez les indicateurs agricoles.' },
  { title: 'Quiz & fiches', text: 'Formez-vous avec le quiz, les badges et les fiches pédagogiques.' },
];

export function initOnboarding() {
  if (localStorage.getItem(KEY)) return;
  let step = 0;
  const overlay = document.createElement('div');
  overlay.className = 'onboarding-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.innerHTML = `
    <div class="onboarding-card">
      <h2 id="onb-title"></h2>
      <p id="onb-text"></p>
      <motion-div class="onboarding-actions">
        <button type="button" class="btn-auth-outline" id="onb-skip">Passer</button>
        <button type="button" class="btn-auth-primary" id="onb-next">Suivant</button>
      </motion-div>
      <p class="onboarding-step" id="onb-step"></p>
    </div>`;
  document.body.appendChild(overlay);
  const title = overlay.querySelector('#onb-title');
  const text = overlay.querySelector('#onb-text');
  const stepEl = overlay.querySelector('#onb-step');
  const render = () => {
    title.textContent = STEPS[step].title;
    text.textContent = STEPS[step].text;
    stepEl.textContent = `${step + 1} / ${STEPS.length}`;
    overlay.querySelector('#onb-next').textContent = step === STEPS.length - 1 ? 'Terminer' : 'Suivant';
  };
  const close = () => {
    localStorage.setItem(KEY, '1');
    overlay.remove();
  };
  overlay.querySelector('#onb-skip').addEventListener('click', close);
  overlay.querySelector('#onb-next').addEventListener('click', () => {
    if (step >= STEPS.length - 1) close();
    else { step += 1; render(); }
  });
  render();
}
