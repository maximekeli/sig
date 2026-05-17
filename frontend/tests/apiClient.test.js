import { describe, expect, it, vi } from 'vitest';
import { createApiClient } from '../js/core/apiClient.js';

describe('createApiClient', () => {
  it('ajoute le token JWT aux requêtes', async () => {
    const storage = { data: {}, getItem(k) { return this.data[k]; }, setItem(k, v) { this.data[k] = v; }, removeItem(k) { delete this.data[k]; } };
    const fetchFn = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ total_points: 10 }),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn });
    client.setToken('abc123');
    await client.api('/dashboard/stats/');
    expect(fetchFn).toBeenCalledWith(
      'http://test/api/v1/dashboard/stats/',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer abc123' }),
      }),
    );
  });

  it('login stocke le token', async () => {
    const storage = { data: {}, getItem(k) { return this.data[k]; }, setItem(k, v) { this.data[k] = v; }, removeItem(k) { delete this.data[k]; } };
    const fetchFn = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: { get: () => 'application/json' },
      json: async () => ({ access: 'token_xyz', refresh: 'r' }),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn });
    await client.login('agent1', 'pass');
    expect(storage.data.sig_sols_token).toBe('token_xyz');
    expect(client.getToken()).toBe('token_xyz');
  });

  it('logout efface le token', async () => {
    const storage = { data: { sig_sols_token: 'x' }, getItem(k) { return this.data[k]; }, setItem(k, v) { this.data[k] = v; }, removeItem(k) { delete this.data[k]; } };
    const client = createApiClient({ baseUrl: 'http://test/api/v1', storage, fetchFn: vi.fn() });
    client.logout();
    expect(client.getToken()).toBe('');
    expect(storage.data.sig_sols_token).toBeUndefined();
  });

  it('lève une erreur si réponse non OK', async () => {
    const fetchFn = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({ detail: 'ph requis' }),
    });
    const client = createApiClient({ baseUrl: 'http://test/api/v1', fetchFn });
    await expect(client.api('/ml/predict/', { method: 'POST' })).rejects.toThrow('ph requis');
  });
});
