const API_BASE = window.location.origin + '/api/v1';

let accessToken = localStorage.getItem('sig_sols_token') || '';

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  const res = await fetch(API_BASE + path, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || JSON.stringify(err));
  }
  if (res.status === 204) return null;
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res;
}

async function login(username, password) {
  const data = await api('/auth/token/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  accessToken = data.access;
  localStorage.setItem('sig_sols_token', accessToken);
  return data;
}

function logout() {
  accessToken = '';
  localStorage.removeItem('sig_sols_token');
}

window.SigSolsAPI = { api, login, logout, getToken: () => accessToken };
