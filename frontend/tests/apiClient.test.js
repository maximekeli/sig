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
});
