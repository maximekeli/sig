import assert from 'node:assert/strict';
import { describe, it } from 'vitest';
import {
  formatMlF1,
  formatSmapCorrelation,
  renderSoilTypeRows,
} from '../js/core/dashboardUtils.js';

describe('dashboardUtils', () => {
  it('formatMlF1', () => {
    assert.equal(formatMlF1(0.752), '75.2% (F1)');
    assert.equal(formatMlF1(null), '—');
    assert.equal(formatMlF1(undefined), '—');
  });

  it('formatSmapCorrelation', () => {
    assert.ok(formatSmapCorrelation({ r_squared: 0.62, sample_size: 80 }).includes('0.62'));
    assert.equal(formatSmapCorrelation({ message: 'Données insuffisantes' }), 'Données insuffisantes');
    assert.equal(formatSmapCorrelation(null), '—');
  });

  it('renderSoilTypeRows', () => {
    const rows = renderSoilTypeRows({
      by_soil_type: [{ soil_type: 'limoneux', count: 42 }],
    });
    assert.equal(rows[0].label, 'limoneux: 42');
    assert.deepEqual(renderSoilTypeRows({}), []);
  });
});
