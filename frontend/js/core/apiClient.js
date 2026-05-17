/**
 * Client API REST — testable sans DOM.
 * @param {{ baseUrl: string, storage?: Storage, fetchFn?: typeof fetch }} config
 */
export function createApiClient({ baseUrl, storage, fetchFn = fetch }) {
  const store = storage || {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
  };
  let accessToken = store.getItem('sig_sols_token') || '';

  async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const res = await fetchFn(`${baseUrl}${path}`, { ...options, headers });
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
    store.setItem('sig_sols_token', accessToken);
    return data;
  }

  function logout() {
    accessToken = '';
    store.removeItem('sig_sols_token');
  }

  function getToken() {
    return accessToken;
  }

  function setToken(token) {
    accessToken = token;
  }

  return { api, login, logout, getToken, setToken };
}
