import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
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

  it('login stocke le token', async () => {
    const storage = mockStorage();
    const fetchFn = async () => ({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ access: 'token_xyz' }),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn });
    await client.login('agent1', 'pass');
    assert.equal(storage._data.sig_sols_token, 'token_xyz');
  });

  it('logout efface le token', () => {
    const storage = mockStorage();
    storage.setItem('sig_sols_token', 'x');
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn: async () => ({}) });
    client.logout();
    assert.equal(client.getToken(), '');
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
