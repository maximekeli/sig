# API et services externes — SIG Sols Togo

## Déjà intégrés (obligatoires ou utilisés par défaut)

| Service | Usage | Clé / config | Fichiers |
|---------|--------|-------------|----------|
| **OpenStreetMap** | Fond de carte tuiles | Aucune (usage fair-use + attribution) | `frontend/js/map.js` |
| **Esri World Imagery** | Fond satellite | Aucune (attribution Esri) | `frontend/js/map.js` |
| **OpenTopoMap** | Fond topographique | Aucune | `frontend/js/map.js` |
| **Leaflet** (+ MarkerCluster, Draw, Heat) | Carte interactive | CDN unpkg | `frontend/index.html` |
| **Chart.js** | Graphiques tableau de bord | CDN jsdelivr | `frontend/index.html` |
| **Google Fonts** | Typographie (Cormorant, Outfit) | Aucune | `frontend/css/style.css` |
| **NASA Earthdata / CMR-STAC** | Catalogue MODIS, SMAP, GPM… | `.env` : `NASA_EARTHDATA_USERNAME`, `NASA_EARTHDATA_PASSWORD` ou `NASA_EARTHDATA_TOKEN` | `backend/apps/nasa/` |
| **earthaccess** | Téléchargement granules NASA | Mêmes identifiants Earthdata | `backend/apps/nasa/earthdata.py` |
| **pystac-client** | Recherche STAC CMR | Public (catalogue) | `backend/apps/nasa/stac_client.py` |

Tuiles NASA affichées sur la carte : **placeholder PNG** via l’API interne `/api/v1/nasa/tiles/...` (pas de tuiles raster NASA réelles tant que l’ingestion WMS/XYZ n’est pas branchée).

## Internes (pas externes)

| Composant | Rôle |
|-----------|------|
| **PostGIS** | Base géospatiale |
| **Redis** | Cache, Celery, Channels WebSocket |
| **API REST Django** | Toute la logique métier (`/api/v1/`) |
| **JWT** | Authentification |

## Non intégrés — utiles si vous voulez aller plus loin

| Service | Intérêt possible | Statut |
|---------|------------------|--------|
| **Google Gemini API** | Résumés en langage naturel des rapports parcelle, assistant pédagogique quiz | ❌ Non intégré — à ajouter via `GEMINI_API_KEY` si souhaité |
| **OpenAI / Anthropic** | Même usage que Gemini | ❌ Non intégré |
| **Mapbox / MapTiler** | Fonds carte vectoriels haute qualité | ❌ Non intégré (OSM suffit pour le pilote) |
| **Sentinel Hub** | NDVI temps réel haute résolution | ❌ Non intégré (NASA MODIS utilisé) |
| **Open-Meteo** | Météo locale pour recommandations irrigation | ❌ Non intégré |
| **SMTP (SendGrid, Brevo…)** | Emails réels mot de passe oublié | ⚠️ `send_mail` Django en dev (console) — configurer `EMAIL_*` en production |
| **Sentry / Datadog** | Monitoring erreurs | ❌ Non intégré |

## Variables d’environnement recommandées

Voir `.env.example` pour la liste à jour.

```bash
# NASA (fortement recommandé pour ingestion réelle)
NASA_EARTHDATA_TOKEN=

# Production email
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@sig-sols.tg

# Futur — assistant IA (non câblé dans le code actuel)
# GEMINI_API_KEY=
# OPENAI_API_KEY=
```

## Parcelles et API

Les parcelles utilisent **uniquement l’API interne** :

- `GET /api/v1/spatial/parcel/zones/geojson/`
- `GET|POST /api/v1/spatial/parcel/live/`
- `POST /api/v1/spatial/parcel/analyze/`

Aucune API externe supplémentaire n’est requise pour la sélection et l’analyse temps réel des parcelles.
