/**
 * OpenWeather — météo carte et parcelles.
 */
import { MARITIME_CENTER } from './core/mapUtils.js';
import { notifyError } from './core/ui.js';

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

function getMap() {
  return window.SigSolsMap?.getMap?.();
}

function iconUrl(icon) {
  if (!icon) return '';
  return `https://openweathermap.org/img/wn/${icon}@2x.png`;
}

function formatCurrentBlock(data) {
  const c = data?.current || {};
  const icon = c.icon ? `<img src="${iconUrl(c.icon)}" alt="" width="48" height="48" />` : '';
  const loc = c.location || data?.city || '';
  return `
    <div class="weather-current">
      ${icon}
      <div>
        <strong>${c.temp_c != null ? `${Math.round(c.temp_c)}°C` : '—'}</strong>
        ${c.feels_like_c != null ? `<span class="weather-feels">ressenti ${Math.round(c.feels_like_c)}°C</span>` : ''}
        <p>${escapeHtml(c.description || '—')}${loc ? ` · ${escapeHtml(loc)}` : ''}</p>
        <p class="weather-meta">
          Humidité ${c.humidity_pct ?? '—'}% · Vent ${c.wind_speed_ms ?? '—'} m/s
          ${c.rain_1h_mm ? ` · Pluie ${c.rain_1h_mm} mm/h` : ''}
        </p>
      </div>
    </div>`;
}

function formatForecastList(items) {
  if (!items?.length) return '<p class="weather-empty">Aucune prévision.</p>';
  return `<ul class="weather-forecast-list">
    ${items.map((f) => {
      const when = f.dt ? new Date(f.dt * 1000).toLocaleString('fr-FR', {
        weekday: 'short', hour: '2-digit', minute: '2-digit',
      }) : '—';
      const pop = f.pop != null ? `${Math.round(f.pop * 100)}% pluie` : '';
      return `<li>
        <span>${when}</span>
        <strong>${f.temp_c != null ? `${Math.round(f.temp_c)}°C` : '—'}</strong>
        <em>${escapeHtml(f.description || '')}</em>
        <small>${pop}</small>
      </li>`;
    }).join('')}
  </ul>`;
}

export async function loadWeatherStatus() {
  const statusEl = document.getElementById('weather-status-msg');
  if (!statusEl) return false;
  try {
    const status = await SigSolsAPI.api('/weather/status/');
    statusEl.textContent = status.message || (status.ok ? 'OpenWeather OK' : 'Non configuré');
    statusEl.classList.toggle('weather-status--ok', Boolean(status.ok));
    statusEl.classList.toggle('weather-status--err', !status.ok);
    return Boolean(status.ok);
  } catch (e) {
    statusEl.textContent = e.message || 'OpenWeather indisponible';
    statusEl.classList.add('weather-status--err');
    return false;
  }
}

export async function fetchWeatherAt(lat, lon, kind = 'current') {
  const path = kind === 'forecast'
    ? `/weather/forecast/?lat=${lat}&lon=${lon}`
    : `/weather/current/?lat=${lat}&lon=${lon}`;
  return SigSolsAPI.api(path);
}

export async function refreshWeatherAtMapCenter(kind = 'current') {
  const map = getMap();
  const out = document.getElementById('weather-out');
  if (!map) {
    notifyError({ message: 'Carte non initialisée.' });
    return null;
  }
  const c = map.getCenter();
  const lat = c.lat;
  const lon = c.lng;
  if (out) out.textContent = 'Chargement météo…';
  try {
    const data = await fetchWeatherAt(lat, lon, kind);
    if (out) {
      out.innerHTML = kind === 'forecast'
        ? `<p class="weather-coords">${lat.toFixed(3)}°, ${lon.toFixed(3)}°</p>${formatForecastList(data.forecast)}`
        : `<p class="weather-coords">${lat.toFixed(3)}°, ${lon.toFixed(3)}°</p>${formatCurrentBlock(data)}`;
    }
    const badge = document.getElementById('weather-map-badge');
    if (badge && kind === 'current') {
      const cur = data.current || {};
      badge.classList.remove('hidden');
      badge.textContent = cur.temp_c != null
        ? `Météo : ${Math.round(cur.temp_c)}°C · ${cur.description || ''}`
        : 'Météo chargée';
    }
    return data;
  } catch (e) {
    if (out) out.textContent = e.message || 'Erreur météo';
    notifyError(e);
    return null;
  }
}

export function initWeatherMapTools() {
  document.getElementById('btn-weather-current')?.addEventListener('click', () => {
    refreshWeatherAtMapCenter('current');
  });
  document.getElementById('btn-weather-forecast')?.addEventListener('click', () => {
    refreshWeatherAtMapCenter('forecast');
  });
  document.getElementById('btn-weather-fit-maritime')?.addEventListener('click', () => {
    getMap()?.setView(MARITIME_CENTER, 9);
    refreshWeatherAtMapCenter('current');
  });
}

export function formatWeatherHtml(weather) {
  if (!weather) return '';
  if (weather.configured === false) {
    return '<p class="parcel-weather parcel-weather--warn">OpenWeather non configuré (.env)</p>';
  }
  if (weather.error) {
    return `<p class="parcel-weather parcel-weather--warn">Météo : ${escapeHtml(weather.error)}</p>`;
  }
  const c = weather.current || {};
  if (c.temp_c == null && !c.description) return '';
  const tips = (weather.agro_tips || []).slice(0, 2).map((t) => ` · ${escapeHtml(t)}`).join('');
  return `<p class="parcel-weather">Météo : <strong>${c.temp_c != null ? `${Math.round(c.temp_c)}°C` : '—'}</strong>`
    + `, ${escapeHtml(c.description || '')}`
    + ` · humidité ${c.humidity_pct ?? '—'}%${tips}</p>`;
}
