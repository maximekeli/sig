import { describe, expect, it } from 'vitest';
import { phColorClass, phColorFromPh, phColorHex } from '../js/core/phColor.js';

describe('phColor', () => {
  it('classifie acide / neutre / basique', () => {
    expect(phColorClass(5.0)).toBe('red');
    expect(phColorClass(5.5)).toBe('yellow');
    expect(phColorClass(6.5)).toBe('yellow');
    expect(phColorClass(7.1)).toBe('green');
  });

  it('retourne une couleur hex', () => {
    expect(phColorFromPh(4.8)).toBe('#c1121f');
    expect(phColorFromPh(7.5)).toBe('#40916c');
  });

  it('fallback gris', () => {
    expect(phColorHex('unknown')).toBe('#666');
  });
});
