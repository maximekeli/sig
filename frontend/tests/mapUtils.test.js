import { describe, expect, it } from 'vitest';
import {
  buildSoilFiltersQuery,
  markerStyleForPoint,
  nasaTileUrl,
  parseSoilPointsList,
} from '../js/core/mapUtils.js';

describe('parseSoilPointsList', () => {
  it('pagination DRF', () => {
    const list = parseSoilPointsList({ results: [{ id: 1, lon: 1.2, lat: 6.3 }] });
    expect(list).toHaveLength(1);
  });

  it('GeoJSON features', () => {
    const list = parseSoilPointsList({
      features: [{ properties: { id: 2, ph: 6 }, geometry: { coordinates: [1.1, 6.2] } }],
    });
    expect(list[0].lon).toBe(1.1);
    expect(list[0].ph).toBe(6);
  });

  it('tableau vide si null', () => {
    expect(parseSoilPointsList(null)).toEqual([]);
  });
});

describe('buildSoilFiltersQuery', () => {
  it('construit les paramètres', () => {
    const q = buildSoilFiltersQuery({ phMin: '5', phMax: '7', soilType: 'limoneux' });
    expect(q).toContain('light=1');
    expect(q).toContain('ph_min=5');
    expect(q).toContain('soil_type=limoneux');
  });
});

describe('markerStyleForPoint', () => {
  it('utilise la couleur pH', () => {
    const s = markerStyleForPoint({ ph_color: 'red' });
    expect(s.fillColor).toBe('#c1121f');
  });
});

describe('nasaTileUrl', () => {
  it('génère le template tuile', () => {
    const url = nasaTileUrl('http://localhost:8081', 'MOD13Q1', '2026-05-01');
    expect(url).toContain('/api/v1/nasa/tiles/MOD13Q1/2026-05-01/');
  });
});
