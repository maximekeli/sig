/**
 * Affichage Sentinel Hub + OpenWeather (parcelle, carte, tableau de bord).
 */

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

function weatherIconUrl(icon) {
  return icon ? `https://openweathermap.org/img/wn/${icon}@2x.png` : '';
}

function summarizeSentinelError(error) {
  const msg = String(error || '').toLowerCase();
  if (msg.includes('nameresolutionerror') || msg.includes('failed to resolve') || msg.includes('dns')) {
    return 'Service temporairement inaccessible (DNS/réseau). Réessayez dans quelques instants.';
  }
  if (msg.includes('401') || msg.includes('oauth') || msg.includes('authentification')) {
    return 'Connexion Sentinel Hub refusée. Vérifiez les identifiants OAuth dans .env.';
  }
  if (msg.includes('timeout')) {
    return 'Sentinel Hub met trop de temps à répondre. Réessayez.';
  }
  return String(error || 'Erreur Sentinel Hub.');
}

export function formatSentinelCard(sentinel) {
  if (!sentinel || sentinel.skipped) {
    return `
      <article class="parcel-ext-card parcel-ext-card--sentinel parcel-ext-card--empty">
        <h4>Sentinel Hub</h4>
        <p>Non demandé ou indisponible pour cette analyse.</p>
      </article>`;
  }
  if (sentinel.configured === false) {
    return `
      <article class="parcel-ext-card parcel-ext-card--sentinel parcel-ext-card--warn">
        <h4>Sentinel Hub</h4>
        <p>Non configuré — ajoutez <code>SENTINEL_HUB_*</code> dans <code>.env</code></p>
      </article>`;
  }
  if (sentinel.error) {
    return `
      <article class="parcel-ext-card parcel-ext-card--sentinel parcel-ext-card--warn">
        <h4>Sentinel Hub</h4>
        <p>${escapeHtml(summarizeSentinelError(sentinel.error))}</p>
      </article>`;
  }
  if (sentinel.ndvi_mean == null) {
    return `
      <article class="parcel-ext-card parcel-ext-card--sentinel">
        <h4>Sentinel Hub</h4>
        <p>Pas de pixels NDVI valides (nuages ou hors couverture).</p>
      </article>`;
  }
  return `
    <article class="parcel-ext-card parcel-ext-card--sentinel">
      <h4>Sentinel Hub · Sentinel-2</h4>
      <p class="parcel-ext-kpi"><strong>${sentinel.ndvi_mean}</strong> <span>NDVI moyen</span></p>
      <p class="parcel-ext-meta">Min ${sentinel.ndvi_min} · Max ${sentinel.ndvi_max} · ${sentinel.pixel_count || '—'} px</p>
      <p class="parcel-ext-src">${escapeHtml(sentinel.source || 'Sentinel Hub')}</p>
    </article>`;
}

export function formatWeatherCard(weather) {
  if (!weather) {
    return `
      <article class="parcel-ext-card parcel-ext-card--weather parcel-ext-card--empty">
        <h4>OpenWeather</h4>
        <p>Non demandé pour cette analyse.</p>
      </article>`;
  }
  if (weather.configured === false) {
    return `
      <article class="parcel-ext-card parcel-ext-card--weather parcel-ext-card--warn">
        <h4>OpenWeather</h4>
        <p>Non configuré — <code>OPENWEATHER_API_KEY</code> dans <code>.env</code></p>
      </article>`;
  }
  if (weather.error) {
    return `
      <article class="parcel-ext-card parcel-ext-card--weather parcel-ext-card--warn">
        <h4>OpenWeather</h4>
        <p>${escapeHtml(weather.error)}</p>
      </article>`;
  }
  const c = weather.current || {};
  const icon = c.icon ? `<img src="${weatherIconUrl(c.icon)}" alt="" width="40" height="40" />` : '';
  const tips = (weather.agro_tips || []).slice(0, 2)
    .map((t) => `<li>${escapeHtml(t)}</li>`).join('');
  return `
    <article class="parcel-ext-card parcel-ext-card--weather">
      <h4>OpenWeather</h4>
      <div class="parcel-ext-weather-row">
        ${icon}
        <div>
          <p class="parcel-ext-kpi"><strong>${c.temp_c != null ? `${Math.round(c.temp_c)}°C` : '—'}</strong>
            <span>${escapeHtml(c.description || '')}</span></p>
          <p class="parcel-ext-meta">Humidité ${c.humidity_pct ?? '—'}% · Vent ${c.wind_speed_ms ?? '—'} m/s
            ${c.location ? ` · ${escapeHtml(c.location)}` : ''}</p>
        </div>
      </div>
      ${tips ? `<ul class="parcel-ext-tips">${tips}</ul>` : ''}
    </article>`;
}

export function formatParcelExternalGrid(sentinel, weather, { title = '' } = {}) {
  const heading = title ? `<p class="parcel-ext-title">${escapeHtml(title)}</p>` : '';
  return `${heading}<div class="parcel-external-grid">${formatSentinelCard(sentinel)}${formatWeatherCard(weather)}</div>`;
}

export function loadLastParcelFromStorage() {
  try {
    const raw = sessionStorage.getItem('sig_sols_last_parcel');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveLastParcelToStorage(data) {
  if (!data) {
    sessionStorage.removeItem('sig_sols_last_parcel');
    return;
  }
  try {
    sessionStorage.setItem('sig_sols_last_parcel', JSON.stringify({
      saved_at: Date.now(),
      parcel_name: data.parcel_name,
      zone_code: data.zone_code,
      sentinel: data.sentinel,
      weather: data.weather,
      area: data.area,
      health_index: data.health_index,
    }));
  } catch { /* quota */ }
}
