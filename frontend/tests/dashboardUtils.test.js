import { describe, expect, it } from 'vitest';
import {
  formatMlF1,
  formatSmapCorrelation,
  renderSoilTypeRows,
} from '../js/core/dashboardUtils.js';

describe('dashboardUtils', () => {
  it('formatMlF1', () => {
    expect(formatMlF1(0.752)).toBe('75.2% (F1)');
    expect(formatMlF1(null)).toBe('—');
  });

  it('formatSmapCorrelation', () => {
    expect(formatSmapCorrelation({ r_squared: 0.62, sample_size: 80 })).toContain('0.62');
    expect(formatSmapCorrelation({ message: 'Données insuffisantes' })).toBe('Données insuffisantes');
  });

  it('renderSoilTypeRows', () => {
    const rows = renderSoilTypeRows({
      by_soil_type: [{ soil_type: 'limoneux', count: 42 }],
    });
    expect(rows[0].label).toBe('limoneux: 42');
  });
});
