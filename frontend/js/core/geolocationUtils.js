/** Utilitaires géolocalisation navigateur + positions utilisateurs. */

export const DEFAULT_TRACK_OPTIONS = {
  enableHighAccuracy: true,
  maximumAge: 5000,
  timeout: 15000,
};

/**
 * @param {GeolocationPosition} pos
 * @returns {{ lat: number, lon: number, accuracy_m: number | null, heading: number | null }}
 */
export function positionToPayload(pos) {
  const { latitude, longitude, accuracy, heading } = pos.coords;
  return {
    lat: latitude,
    lon: longitude,
    accuracy_m: Number.isFinite(accuracy) ? accuracy : null,
    heading: Number.isFinite(heading) ? heading : null,
  };
}

/**
 * @param {Array<{ user_id: number, lat: number, lon: number, display_name?: string, role?: string }>} users
 */
export function parseLiveUsers(data) {
  return (data?.users || []).map((u) => ({
    id: u.user_id,
    username: u.username,
    displayName: u.display_name || u.username,
    role: u.role,
    profilePhotoUrl: u.profile_photo_url || null,
    lat: u.lat,
    lon: u.lon,
    accuracy_m: u.accuracy_m,
    updatedAt: u.updated_at,
  }));
}

/** Style Leaflet — position de l'utilisateur courant. */
export function selfLocationStyle() {
  return {
    radius: 9,
    color: '#1d4ed8',
    fillColor: '#3b82f6',
    fillOpacity: 0.85,
    weight: 3,
  };
}

/** Style Leaflet — autres utilisateurs. */
export function peerLocationStyle(role) {
  const color = role === 'admin' ? '#b45309' : '#059669';
  return {
    radius: 7,
    color: '#fff',
    fillColor: color,
    fillOpacity: 0.9,
    weight: 2,
  };
}
