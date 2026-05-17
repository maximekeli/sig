export function formatMlF1(f1Macro) {
  if (f1Macro == null || f1Macro === undefined) return '—';
  return `${(f1Macro * 100).toFixed(1)}% (F1)`;
}

export function formatSmapCorrelation(smap) {
  if (!smap) return '—';
  if (smap.r_squared != null) {
    return `R² = ${smap.r_squared} (n=${smap.sample_size})`;
  }
  return smap.message || '—';
}

export function renderSoilTypeRows(stats) {
  return (stats.by_soil_type || []).map((row) => ({
    label: `${row.soil_type}: ${row.count}`,
    soil_type: row.soil_type,
    count: row.count,
  }));
}
