/**
 * Interface d'authentification — connexion, inscription, profil, déconnexion.
 */

const ROLE_LABELS = {
  admin: 'Administrateur',
  agent: 'Agent',
  public: 'Public',
};

function $(id) {
  return document.getElementById(id);
}

function showAuthTab(tab) {
  const loginForm = $('auth-login-form');
  const registerForm = $('auth-register-form');
  document.querySelectorAll('[data-auth-tab]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.authTab === tab);
  });
  loginForm?.classList.toggle('hidden', tab !== 'login');
  registerForm?.classList.toggle('hidden', tab !== 'register');
}

function renderAuthUI() {
  const guest = $('auth-guest');
  const logged = $('auth-user');
  const user = SigSolsAPI.getUser();
  const authed = SigSolsAPI.isAuthenticated();

  if (authed && user) {
    guest?.classList.add('hidden');
    logged?.classList.remove('hidden');
    const label = $('auth-user-label');
    if (label) {
      label.textContent = `${user.username} · ${ROLE_LABELS[user.role] || user.role}`;
    }
  } else {
    guest?.classList.remove('hidden');
    logged?.classList.add('hidden');
  }
}

async function handleLogin() {
  const msg = $('auth-message');
  try {
    await SigSolsAPI.login(
      $('login-user')?.value?.trim(),
      $('login-pass')?.value,
    );
    if (msg) {
      msg.textContent = '';
      msg.className = 'auth-message';
    }
    renderAuthUI();
    SigSolsMap.loadSoilPoints();
    if ($('share-location')?.checked) SigSolsMap.startLiveLocation();
  } catch (e) {
    if (msg) {
      msg.textContent = e.message;
      msg.className = 'auth-message error';
    }
  }
}

async function handleRegister() {
  const msg = $('auth-message');
  try {
    await SigSolsAPI.register({
      username: $('reg-user')?.value?.trim(),
      email: $('reg-email')?.value?.trim() || '',
      password: $('reg-pass')?.value,
      password_confirm: $('reg-pass2')?.value,
      role: $('reg-role')?.value || 'public',
      organization: $('reg-org')?.value?.trim() || '',
    });
    if (msg) {
      msg.textContent = 'Compte créé — connectez-vous.';
      msg.className = 'auth-message success';
    }
    showAuthTab('login');
    $('login-user').value = $('reg-user')?.value || '';
  } catch (e) {
    if (msg) {
      msg.textContent = e.message;
      msg.className = 'auth-message error';
    }
  }
}

async function handleLogout() {
  await SigSolsMap.stopLiveLocation();
  await SigSolsAPI.logout();
  renderAuthUI();
  $('auth-profile-modal')?.classList.add('hidden');
}

function openProfileModal() {
  const user = SigSolsAPI.getUser();
  if (!user) return;
  $('prof-email').value = user.email || '';
  $('prof-first').value = user.first_name || '';
  $('prof-last').value = user.last_name || '';
  $('prof-org').value = user.organization || '';
  $('prof-phone').value = user.phone || '';
  $('prof-pseudo').value = user.pseudonym || '';
  $('profile-message').textContent = '';
  $('auth-profile-modal')?.classList.remove('hidden');
}

async function saveProfile() {
  const msg = $('profile-message');
  try {
    await SigSolsAPI.updateProfile({
      email: $('prof-email').value,
      first_name: $('prof-first').value,
      last_name: $('prof-last').value,
      organization: $('prof-org').value,
      phone: $('prof-phone').value,
      pseudonym: $('prof-pseudo').value,
    });
    if (msg) {
      msg.textContent = 'Profil enregistré.';
      msg.className = 'auth-message success';
    }
    renderAuthUI();
  } catch (e) {
    if (msg) {
      msg.textContent = e.message;
      msg.className = 'auth-message error';
    }
  }
}

async function savePassword() {
  const msg = $('profile-message');
  try {
    await SigSolsAPI.changePassword(
      $('prof-old-pass').value,
      $('prof-new-pass').value,
      $('prof-new-pass2').value,
    );
    $('prof-old-pass').value = '';
    $('prof-new-pass').value = '';
    $('prof-new-pass2').value = '';
    if (msg) {
      msg.textContent = 'Mot de passe mis à jour.';
      msg.className = 'auth-message success';
    }
  } catch (e) {
    if (msg) {
      msg.textContent = e.message;
      msg.className = 'auth-message error';
    }
  }
}

async function initAuth() {
  document.querySelectorAll('[data-auth-tab]').forEach((btn) => {
    btn.addEventListener('click', () => showAuthTab(btn.dataset.authTab));
  });
  $('btn-login')?.addEventListener('click', handleLogin);
  $('btn-register')?.addEventListener('click', handleRegister);
  $('btn-logout')?.addEventListener('click', handleLogout);
  $('btn-profile')?.addEventListener('click', openProfileModal);
  const closeProfile = () => $('auth-profile-modal')?.classList.add('hidden');
  $('btn-profile-close')?.addEventListener('click', closeProfile);
  $('btn-profile-close-footer')?.addEventListener('click', closeProfile);
  $('btn-profile-save')?.addEventListener('click', saveProfile);
  $('btn-password-save')?.addEventListener('click', savePassword);
  $('login-pass')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleLogin();
  });

  if (SigSolsAPI.isAuthenticated()) {
    try {
      await SigSolsAPI.fetchProfile();
    } catch {
      SigSolsAPI.clearSession();
    }
  }
  renderAuthUI();
  showAuthTab('login');
}

window.SigSolsAuth = { initAuth, renderAuthUI };
