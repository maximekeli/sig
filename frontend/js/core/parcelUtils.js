/** Libellés et styles partagés — module parcelles. */
export const VULN_COLORS = {
  faible: '#2d8a52',
  moyenne: '#e9a319',
  elevee: '#dc2626',
};

export const ZONE_STYLES = {
  canton: { color: '#c9a962', weight: 2, fillOpacity: 0.08 },
  degraded: { color: '#dc2626', weight: 2, fillOpacity: 0.12, dashArray: '6' },
  default: { color: '#2d8a52', weight: 1.5, fillOpacity: 0.06 },
};

export const NDVI_LABELS = {
  stress_severe: 'Stress sévère',
  stress_modere: 'Stress modéré',
  vegetation_moyenne: 'Végétation moyenne',
  vegetation_vigoureuse: 'Végétation vigoureuse',
  donnees_manquantes: 'Données manquantes',
};

export const SMAP_LABELS = {
  secheresse_probable: 'Sécheresse probable',
  humidite_faible: 'Humidité faible',
  humidite_moyenne: 'Humidité moyenne',
  humidite_bonne: 'Humidité bonne',
  donnees_manquantes: 'Données manquantes',
};

export const PH_COLORS = {
  red: '#dc2626',
  yellow: '#e9a319',
  green: '#2d8a52',
};

export function vulnLabel(level) {
  return { faible: 'Faible', moyenne: 'Moyenne', elevee: 'Élevée' }[level] || level || '—';
}

export function healthClass(index) {
  if (index == null) return 'unknown';
  if (index >= 70) return 'good';
  if (index >= 45) return 'mid';
  return 'low';
}
