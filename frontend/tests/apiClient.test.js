import assert from 'node:assert/strict';
import { describe, it } from 'vitest';
import { createApiClient } from '../js/core/apiClient.js';

function mockStorage() {
  const data = {};
  return {
    getItem: (k) => data[k] ?? null,
    setItem: (k, v) => { data[k] = v; },
    removeItem: (k) => { delete data[k]; },
    _data: data,
  };
}

describe('createApiClient', () => {
  it('ajoute le token JWT', async () => {
    const storage = mockStorage();
    let capturedHeaders;
    const fetchFn = async (url, opts) => {
      capturedHeaders = opts.headers;
      return {
        ok: true,
        status: 200,
        headers: { get: () => 'application/json' },
        json: async () => ({}),
      };
    };
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn });
    client.setToken('abc123');
    await client.api('/dashboard/stats/');
    assert.equal(capturedHeaders.Authorization, 'Bearer abc123');
  });

  it('login stocke le token et refresh', async () => {
    const storage = mockStorage();
    const fetchFn = async () => ({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({
        access: 'token_xyz',
        refresh: 'refresh_xyz',
        user: { username: 'agent1', role: 'agent' },
      }),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn });
    await client.login('agent1', 'pass');
    assert.equal(storage._data.sig_sols_token, 'token_xyz');
    assert.equal(storage._data.sig_sols_refresh, 'refresh_xyz');
    assert.ok(client.isAuthenticated());
  });

  it('logout efface la session', async () => {
    const storage = mockStorage();
    storage.setItem('sig_sols_token', 'x');
    storage.setItem('sig_sols_refresh', 'r');
    const fetchFn = async () => ({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({}),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn });
    await client.logout();
    assert.equal(client.getToken(), '');
    assert.equal(client.isAuthenticated(), false);
  });

  it('register appelle l’API', async () => {
    const fetchFn = async (url, opts) => {
      assert.ok(url.includes('/auth/register/'));
      assert.equal(opts.method, 'POST');
      return {
        ok: true,
        status: 201,
        headers: { get: () => 'application/json' },
        json: async () => ({ user: { username: 'new' } }),
      };
    };
    const client = createApiClient({ baseUrl: 'http://test/api/v1', fetchFn });
    const data = await client.register({
      username: 'new',
      password: 'pass12345',
      password_confirm: 'pass12345',
    });
    assert.equal(data.user.username, 'new');
  });

  it('réponse 204', async () => {
    const fetchFn = async () => ({
      ok: true,
      status: 204,
      headers: { get: () => '' },
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', fetchFn });
    assert.equal(await client.api('/x/'), null);
  });

  it('réponse non JSON', async () => {
    const fetchFn = async () => ({
      ok: true,
      status: 200,
      headers: { get: () => 'text/plain' },
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', fetchFn });
    const res = await client.api('/export/');
    assert.ok(res.headers);
  });

  it('erreur JSON fallback', async () => {
    const fetchFn = async () => ({
      ok: false,
      status: 500,
      statusText: 'Error',
      json: async () => { throw new Error('no json'); },
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', fetchFn });
    await assert.rejects(() => client.api('/x/'), /Error/);
  });

  it('erreur avec detail', async () => {
    const fetchFn = async () => ({
      ok: false,
      status: 400,
      statusText: 'Bad',
      json: async () => ({ detail: 'ph requis' }),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', fetchFn });
    await assert.rejects(() => client.api('/ml/predict/'), /ph requis/);
  });
});
