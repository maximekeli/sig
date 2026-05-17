import { createApiClient } from './core/apiClient.js';

const client = createApiClient({
  baseUrl: window.location.origin + '/api/v1',
  storage: localStorage,
});

window.SigSolsAPI = {
  api: client.api,
  login: client.login,
  logout: client.logout,
  getToken: client.getToken,
};
