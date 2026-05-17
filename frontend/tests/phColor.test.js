import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { phColorClass, phColorFromPh, phColorHex } from '../js/core/phColor.js';

describe('phColor', () => {
  it('classifie acide / neutre / basique', () => {
    assert.equal(phColorClass(5.0), 'red');
    assert.equal(phColorClass(5.5), 'yellow');
    assert.equal(phColorClass(7.1), 'green');
  });

  it('retourne une couleur hex', () => {
    assert.equal(phColorFromPh(4.8), '#c1121f');
    assert.equal(phColorFromPh(7.5), '#40916c');
  });

  it('fallback gris', () => {
    assert.equal(phColorHex('unknown'), '#666');
  });
});
