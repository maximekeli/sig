import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import {
  buildSoilFiltersQuery,
  markerStyleForPoint,
  nasaTileUrl,
  parseSoilPointsList,
} from '../js/core/mapUtils.js';

describe('parseSoilPointsList', () => {
  it('pagination DRF', () => {
    const list = parseSoilPointsList({ results: [{ id: 1, lon: 1.2, lat: 6.3 }] });
    assert.equal(list.length, 1);
  });

  it('GeoJSON features', () => {
    const list = parseSoilPointsList({
      features: [{ properties: { id: 2, ph: 6 }, geometry: { coordinates: [1.1, 6.2] } }],
    });
    assert.equal(list[0].lon, 1.1);
  });
});

describe('buildSoilFiltersQuery', () => {
  it('construit les paramètres', () => {
    const q = buildSoilFiltersQuery({ phMin: '5', soilType: 'limoneux' });
    assert.ok(q.includes('ph_min=5'));
  });
});

describe('nasaTileUrl', () => {
  it('template tuile NASA', () => {
    const url = nasaTileUrl('http://localhost:8081', 'MOD13Q1', '2026-05-01');
    assert.ok(url.includes('MOD13Q1'));
  });
});
