/** Internationalisation FR / EN (clés data-i18n sur le DOM). */
const STRINGS = {
  fr: {
    'nav.map': 'Carte',
    'nav.dashboard': 'Tableau de bord',
    'nav.quiz': 'Quiz',
    'nav.sheets': 'Fiches',
    'nav.admin': 'Admin',
    'nav.help': 'Aide',
    'auth.login': 'Connexion',
    'auth.register': 'Inscription',
    'auth.logout': 'Déconnexion',
    'auth.profile': 'Profil',
    'theme.toggle': 'Thème',
    'lang.toggle': 'EN',
    'help.tour': 'Aide',
    'offline.banner': 'Hors ligne — les données seront synchronisées à la reconnexion.',
    'online.banner': 'Connexion rétablie.',
    'welcome.title': 'Bienvenue sur SIG Sols Togo',
    'welcome.sub': 'Cartographie des sols, NASA, IA et quiz pédagogique — Région Maritime.',
    'sidebar.filters': 'Filtres',
    'sidebar.tools': 'Outils carte',
    'loading.map': 'Chargement des points…',
    'shortcut.help': 'Raccourcis : M carte, D tableau de bord, ? aide',
  },
  en: {
    'nav.map': 'Map',
    'nav.dashboard': 'Dashboard',
    'nav.quiz': 'Quiz',
    'nav.sheets': 'Sheets',
    'nav.admin': 'Admin',
    'nav.help': 'Help',
    'auth.login': 'Sign in',
    'nav.register': 'Register',
    'auth.register': 'Register',
    'auth.logout': 'Sign out',
    'auth.profile': 'Profile',
    'theme.toggle': 'Theme',
    'lang.toggle': 'FR',
    'help.tour': 'Help',
    'offline.banner': 'Offline — data will sync when back online.',
    'online.banner': 'Back online.',
    'welcome.title': 'Welcome to SIG Sols Togo',
    'welcome.sub': 'Soil mapping, NASA layers, AI and quizzes — Maritime Region.',
    'sidebar.filters': 'Filters',
    'sidebar.tools': 'Map tools',
    'loading.map': 'Loading points…',
    'shortcut.help': 'Shortcuts: M map, D dashboard, ? help',
  },
};

let lang = localStorage.getItem('sig_sols_lang') || 'fr';

export function getLang() {
  return lang;
}

export function t(key) {
  return STRINGS[lang]?.[key] ?? STRINGS.fr[key] ?? key;
}

export function setLang(next) {
  lang = next === 'en' ? 'en' : 'fr';
  localStorage.setItem('sig_sols_lang', lang);
  applyI18n();
  document.documentElement.lang = lang;
}

export function toggleLang() {
  setLang(lang === 'fr' ? 'en' : 'fr');
}

export function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    const val = t(key);
    if (el.tagName === 'INPUT' && el.placeholder) el.placeholder = val;
    else el.textContent = val;
  });
  const langBtn = document.getElementById('btn-lang');
  if (langBtn) langBtn.textContent = t('lang.toggle');
  document.title = lang === 'en'
    ? 'SIG Sols Togo — DISIA / DUSOL'
    : 'SIG Sols Togo — DISIA / DUSOL';
}

export function initI18n() {
  document.documentElement.lang = lang;
  applyI18n();
}
