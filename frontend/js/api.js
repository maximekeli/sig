import { createApiClient } from './core/apiClient.js';

const client = createApiClient({
  baseUrl: window.location.origin + '/api/v1',
  storage: localStorage,
});

window.SigSolsAPI = {
  api: client.api,
  login: client.login,
  register: client.register,
  logout: client.logout,
  fetchProfile: client.fetchProfile,
  updateProfile: client.updateProfile,
  changePassword: client.changePassword,
  refreshAccessToken: client.refreshAccessToken,
  getToken: client.getToken,
  setToken: client.setToken,
  getUser: client.getUser,
  setUser: client.setUser,
  isAuthenticated: client.isAuthenticated,
  clearSession: client.clearSession,
  updateLocation: client.updateLocation,
  getLiveLocations: client.getLiveLocations,
  clearLocation: client.clearLocation,
  download: client.download,
};
