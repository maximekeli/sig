# L2 — Modèle de données PostGIS

## Entités principales

### User (`accounts_user`)
- `role` : admin | agent | public
- `organization`, `pseudonym` (classement quiz)

### SoilPoint (`soils_soilpoint`)
- `location` : PointField EPSG:4326
- `ph`, `humidity_pct`, `soil_type`, `fertility_class`, `fertility_score`
- `ndvi_3m_avg`, `smap_moisture_avg`, `slope_pct`, `elevation_m`
- Métadonnées : `source`, `producer`, `collected_at`, `is_validated`

### AdministrativeZone (`soils_administrativezone`)
- `geometry` : MultiPolygonField
- `zone_type` : region | prefecture | canton | degraded

### NasaLayerCatalog (`nasa_nasalayercatalog`)
- Produits : MOD13Q1, SMAP, GPM, SRTM, MOD16, MOD11A2, ECOSTRESS

### FertilityModelRun / FertilityPredictionLog
- Métriques F1, AUC, matrice de confusion

### QuizQuestion, QuizSession, UserBadge, UserQuizProfile
- Gamification OS6

## Index spatiaux
- GIST sur `location`, `geometry`
- Index B-tree sur `ph`, `collected_at`, `product`
