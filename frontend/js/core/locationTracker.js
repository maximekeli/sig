/**
 * Suivi GPS temps réel : watchPosition + envoi API + polling des pairs.
 * @param {{ api: Function, onSelfUpdate?: Function, onPeersUpdate?: Function, onError?: Function }} opts
 */
export function createLocationTracker({
  api,
  onSelfUpdate,
  onPeersUpdate,
  onError,
  updateIntervalMs = 10000,
  pollIntervalMs = 8000,
}) {
  let watchId = null;
  let updateTimer = null;
  let pollTimer = null;
  let lastSent = null;
  let sharing = false;
  let lastPosition = null;

  async function sendPosition(pos) {
    const payload = {
      lat: pos.coords.latitude,
      lon: pos.coords.longitude,
      accuracy_m: pos.coords.accuracy ?? null,
      heading: Number.isFinite(pos.coords.heading) ? pos.coords.heading : null,
      is_sharing: true,
    };
    const key = `${payload.lat.toFixed(5)},${payload.lon.toFixed(5)}`;
    if (lastSent === key) return;
    lastSent = key;
    await api('/auth/location/', { method: 'POST', body: JSON.stringify(payload) });
    if (onSelfUpdate) onSelfUpdate(payload);
  }

  async function pollPeers() {
    const data = await api('/auth/locations/live/');
    if (onPeersUpdate) onPeersUpdate(data);
  }

  function onGeoSuccess(pos) {
    lastPosition = pos;
    sendPosition(pos).catch((e) => onError?.(e));
  }

  function onGeoError(err) {
    onError?.(new Error(err.message || 'Géolocalisation refusée ou indisponible'));
  }

  return {
    isActive: () => sharing,

    async start() {
      if (!navigator.geolocation) {
        throw new Error('Géolocalisation non supportée par ce navigateur.');
      }
      sharing = true;
      watchId = navigator.geolocation.watchPosition(
        onGeoSuccess,
        onGeoError,
        { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 },
      );
      updateTimer = setInterval(() => {
        if (lastPosition) sendPosition(lastPosition).catch((e) => onError?.(e));
      }, updateIntervalMs);
      pollTimer = setInterval(() => {
        pollPeers().catch((e) => onError?.(e));
      }, pollIntervalMs);
      await pollPeers();
    },

    async stop() {
      sharing = false;
      if (watchId != null) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
      }
      if (updateTimer) clearInterval(updateTimer);
      if (pollTimer) clearInterval(pollTimer);
      updateTimer = null;
      pollTimer = null;
      lastSent = null;
      lastPosition = null;
      try {
        await api('/auth/location/', { method: 'DELETE' });
      } catch {
        /* ignore */
      }
    },
  };
}
