/**
 * Sélection de parcelles et analyse automatique (NASA + IA).
 */

let drawControl = null;
let drawnLayer = null;
let parcelHighlight = null;

const VULN_COLORS = {
  faible: '#2d8a52',
  moyenne: '#e9a319',
  elevee: '#dc2626',
};

function getMap() {
  return window.SigSolsMap?.getMap?.();
}

function clearParcelLayers() {
  const map = getMap();
  if (!map) return;
  if (drawnLayer) {
    map.removeLayer(drawnLayer);
    drawnLayer = null;
  }
  if (parcelHighlight) {
    map.removeLayer(parcelHighlight);
    parcelHighlight = null;
  }
}

function initDrawControl() {
  const map = getMap();
  if (!map || typeof L.Control.Draw === 'undefined') return;

  drawnLayer = new L.FeatureGroup().addTo(map);

  drawControl = new L.Control.Draw({
    draw: {
      polyline: false,
      circle: false,
      circlemarker: false,
      marker: false,
      rectangle: { shapeOptions: { color: '#c9a962', weight: 2 } },
      polygon: {
        allowIntersection: false,
        shapeOptions: { color: '#c9a962', weight: 2, fillOpacity: 0.15 },
      },
    },
    edit: { featureGroup: drawnLayer, remove: true },
  });
  map.addControl(drawControl);

  map.on(L.Draw.Event.CREATED, (e) => {
    drawnLayer.clearLayers();
    drawnLayer.addLayer(e.layer);
    document.getElementById('parcel-zone-select').value = '';
    setParcelStatus('Parcelle dessinée — cliquez sur « Analyser ».');
  });

  map.on(L.Draw.Event.DELETED, () => {
    setParcelStatus('Sélection effacée.');
  });
}

function setParcelStatus(msg) {
  const el = document.getElementById('parcel-status');
  if (el) el.textContent = msg;
}

function getDrawnGeometry() {
  if (!drawnLayer) return null;
  const layers = drawnLayer.getLayers();
  if (!layers.length) return null;
  return layers[0].toGeoJSON().geometry;
}

async function loadZonesSelect() {
  const select = document.getElementById('parcel-zone-select');
  if (!select) return;
  try {
    const data = await SigSolsAPI.api('/spatial/parcel/zones/?zone_type=canton');
    select.innerHTML = '<option value="">— Dessiner sur la carte —</option>';
    (data.zones || []).forEach((z) => {
      const opt = document.createElement('option');
      opt.value = z.code;
      opt.textContent = `${z.name} (${z.code})`;
      opt.dataset.zoneId = z.id;
      select.appendChild(opt);
    });
    const deg = await SigSolsAPI.api('/spatial/parcel/zones/?zone_type=degraded');
    if (deg.zones?.length) {
      const grp = document.createElement('optgroup');
      grp.label = 'Zones dégradées';
      deg.zones.forEach((z) => {
        const opt = document.createElement('option');
        opt.value = z.code;
        opt.textContent = `${z.name} (${z.code})`;
        grp.appendChild(opt);
      });
      select.appendChild(grp);
    }
  } catch {
    select.innerHTML = '<option value="">Zones non chargées</option>';
  }
}

function highlightParcel(geojson, vulnerabilityLevel) {
  const map = getMap();
  if (!map || !geojson) return;
  if (parcelHighlight) map.removeLayer(parcelHighlight);
  const color = VULN_COLORS[vulnerabilityLevel] || VULN_COLORS.moyenne;
  parcelHighlight = L.geoJSON(geojson, {
    style: { color, weight: 3, fillColor: color, fillOpacity: 0.2 },
  }).addTo(map);
  try {
    map.fitBounds(parcelHighlight.getBounds(), { padding: [40, 40] });
  } catch {
    /* ignore */
  }
}

function renderAnalysisResult(data) {
  const box = document.getElementById('parcel-analysis-result');
  if (!box) return;

  const sp = data.soil_points || {};
  const nasa = data.nasa || {};
  const vuln = data.vulnerability || {};
  const ml = data.ml_prediction || {};

  const ndviLabel = {
    stress_severe: 'Stress sévère',
    stress_modere: 'Stress modéré',
    vegetation_moyenne: 'Végétation moyenne',
    vegetation_vigoureuse: 'Végétation vigoureuse',
    donnees_manquantes: 'Données manquantes',
  };
  const smapLabel = {
    secheresse_probable: 'Sécheresse probable',
    humidite_faible: 'Humidité faible',
    humidite_moyenne: 'Humidité moyenne',
    humidite_bonne: 'Humidité bonne',
    donnees_manquantes: 'Données manquantes',
  };

  box.classList.remove('hidden');
  box.innerHTML = `
    <div class="parcel-report parcel-report--${vuln.level || 'moyenne'}">
      <h4>${data.parcel_name || 'Parcelle'}</h4>
      <p class="parcel-meta">
        ${data.area?.area_ha ?? '—'} ha ·
        ${sp.count ?? 0} point(s) sol ·
        Vulnérabilité <strong>${vuln.level || '—'}</strong>
      </p>
      <div class="parcel-metrics">
        <span>pH moy. <strong>${sp.avg_ph ?? '—'}</strong></span>
        <span>NDVI <strong>${sp.avg_ndvi ?? nasa.avg_ndvi ?? '—'}</strong></span>
        <span>SMAP <strong>${sp.avg_smap ?? nasa.avg_smap ?? '—'}</strong></span>
        <span>Humid. <strong>${sp.avg_humidity_pct ?? '—'}%</strong></span>
      </div>
      <p class="parcel-nasa">
        NASA : ${ndviLabel[nasa.ndvi_status] || '—'} · ${smapLabel[nasa.smap_status] || '—'}
      </p>
      ${ml.predicted_class ? `
        <p class="parcel-ml">
          IA fertilité : <strong>${ml.predicted_class}</strong>
          (confiance ${Math.round((ml.confidence || 0) * 100)}%)
        </p>
      ` : ''}
      ${(data.recommendations || []).length ? `
        <ul class="parcel-recs">
          ${data.recommendations.map((r) => `<li>${r}</li>`).join('')}
        </ul>
      ` : ''}
    </motion.div>
  `.replace(/<\/?motion\.div>/g, (m) => (m.includes('/') ? '</motion.div>' : '<motion.div>').replace('motion.', ''));

  highlightParcel(data.geometry_geojson, vuln.level);
}

async function runParcelAnalysis() {
  const zoneCode = document.getElementById('parcel-zone-select')?.value;
  const geometry = zoneCode ? null : getDrawnGeometry();
  const useMl = document.getElementById('parcel-use-ml')?.checked !== false;
  const useNasa = document.getElementById('parcel-use-nasa')?.checked !== false;

  if (!zoneCode && !geometry) {
    alert('Dessinez un polygone sur la carte ou sélectionnez une zone administrative.');
    return;
  }

  setParcelStatus('Analyse en cours (NASA + IA)…');
  const box = document.getElementById('parcel-analysis-result');
  if (box) {
    box.classList.remove('hidden');
    box.innerHTML = '<p class="parcel-loading">Analyse automatique…</p>';
  }

  try {
    const body = { use_ml: useMl, use_nasa: useNasa };
    if (zoneCode) body.zone_code = zoneCode;
    else body.geometry = geometry;

    const data = await SigSolsAPI.api('/spatial/parcel/analyze/', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    renderAnalysisResult(data);
    setParcelStatus('Analyse terminée.');
  } catch (e) {
    setParcelStatus('Erreur : ' + (e.message || 'analyse impossible'));
    if (box) box.innerHTML = `<p class="parcel-error">${e.message}</p>`;
  }
}

function onZoneSelectChange() {
  const code = document.getElementById('parcel-zone-select')?.value;
  if (code) {
    clearParcelLayers();
    setParcelStatus(`Zone « ${code} » sélectionnée — cliquez sur Analyser.`);
  }
}

function clearParcelSelection() {
  document.getElementById('parcel-zone-select').value = '';
  if (drawnLayer) drawnLayer.clearLayers();
  clearParcelLayers();
  const box = document.getElementById('parcel-analysis-result');
  if (box) {
    box.classList.add('hidden');
    box.innerHTML = '';
  }
  setParcelStatus('Sélection effacée.');
}

function initParcelTools() {
  initDrawControl();
  loadZonesSelect();
  document.getElementById('btn-parcel-analyze')?.addEventListener('click', runParcelAnalysis);
  document.getElementById('btn-parcel-clear')?.addEventListener('click', clearParcelSelection);
  document.getElementById('parcel-zone-select')?.addEventListener('change', onZoneSelectChange);
  setParcelStatus('Dessinez une parcelle ou choisissez une zone.');
}

window.SigSolsParcel = {
  initParcelTools,
  loadZonesSelect,
  runParcelAnalysis,
  clearParcelSelection,
};
