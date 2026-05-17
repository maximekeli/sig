# API REST — SIG-SOLS-TOGO-2026-01

Base URL : `/api/v1/`  
Auth : JWT Bearer (`Authorization: Bearer <token>`), expiration 1 h.

## Auth

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register/` | Inscription (Public par défaut) |
| POST | `/auth/token/` | Obtenir JWT |
| POST | `/auth/token/refresh/` | Rafraîchir token |
| GET/PATCH | `/auth/profile/` | Profil |
| GET | `/auth/users/` | Liste (Admin) |

## Sols

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/POST | `/points/` | CRUD points |
| GET | `/points/?light=1` | Liste légère carte |
| GET | `/points/geojson/` | Export GeoJSON |
| GET | `/points/export-csv/` | Export CSV |
| POST | `/points/import_data/` | Import GeoJSON (Agent) |
| GET/POST | `/zones/` | Zones administratives |
| GET | `/dashboard/stats/` | KPI dashboard |

## Spatial

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/spatial/proximity/?lon=&lat=&radius_m=` | Proximité |
| POST | `/spatial/intersection/` | Intersection polygone |
| POST | `/spatial/buffer/` | Tampon |
| POST | `/spatial/area/` | Surface |
| GET | `/spatial/vulnerability/` | Zonage vulnérabilité |
| GET | `/spatial/ndvi-timeseries/<id>/` | Série NDVI |
| GET | `/spatial/statistics/` | Stats par canton |
| GET | `/spatial/smap-correlation/` | R² SMAP / terrain |

## NASA

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/nasa/layers/` | Catalogue |
| GET | `/nasa/catalog/summary/` | Synthèse |
| POST | `/nasa/ingest/` | Déclencher ingestion (Admin) |
| GET | `/nasa/tiles/<product>/<date>/<z>/<x>/<y>.png` | Tuile overlay |

## ML

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/ml/predict/` | Prédiction fertilité |
| POST | `/ml/train/` | Entraînement (Admin) |
| GET | `/ml/metrics/` | Métriques modèle actif |

## Éducation

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/education/sheets/` | Fiches pédagogiques |
| POST | `/education/quiz/start/` | Démarrer quiz |
| POST | `/education/quiz/<id>/answer/` | Répondre |
| POST | `/education/quiz/<id>/finish/` | Terminer |
| GET | `/education/quiz/leaderboard/` | Top 10 hebdo |
| GET | `/education/quiz/badges/` | Mes badges |
