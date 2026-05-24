"""Evalscripts Sentinel Hub (Process API v3)."""

NDVI_COLOR = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 4 },
  };
}
function evaluatePixel(s) {
  if (s.dataMask === 0) return [0, 0, 0, 0];
  let ndvi = (s.B08 - s.B04) / (s.B08 + s.B04);
  if (ndvi < 0.1) return [0.65, 0.15, 0.15, 1];
  if (ndvi < 0.3) return [0.9, 0.6, 0.2, 1];
  if (ndvi < 0.5) return [0.95, 0.95, 0.25, 1];
  if (ndvi < 0.7) return [0.5, 0.85, 0.35, 1];
  return [0.1, 0.55, 0.15, 1];
}
"""

TRUE_COLOR = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04", "dataMask"],
    output: { bands: 4 },
  };
}
function evaluatePixel(s) {
  if (s.dataMask === 0) return [0, 0, 0, 0];
  return [2.5 * s.B04, 2.5 * s.B03, 2.5 * s.B02, 1];
}
"""

NDVI_STATS = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: [
      { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
      { id: "dataMask", bands: 1 },
    ],
  };
}
function evaluatePixel(s) {
  if (s.dataMask === 0) return { ndvi: [NaN], dataMask: [0] };
  let ndvi = (s.B08 - s.B04) / (s.B08 + s.B04);
  return { ndvi: [ndvi], dataMask: [1] };
}
"""

LAYER_PRESETS = {
    'ndvi': {
        'title': 'NDVI Sentinel-2 (L2A)',
        'description': 'Vigueur végétale — couleurs indicatives',
        'evalscript': NDVI_COLOR,
    },
    'true_color': {
        'title': 'Couleur vraie Sentinel-2',
        'description': 'Image optique RGB',
        'evalscript': TRUE_COLOR,
    },
}
