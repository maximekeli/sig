/** Codage couleur pH — TdR §14.1 */
export function phColorClass(ph) {
  if (ph < 5.5) return 'red';
  if (ph <= 7.0) return 'yellow';
  return 'green';
}

export function phColorHex(colorClass) {
  return { red: '#c1121f', yellow: '#e9c46a', green: '#40916c' }[colorClass] || '#666';
}

export function phColorFromPh(ph) {
  return phColorHex(phColorClass(ph));
}
