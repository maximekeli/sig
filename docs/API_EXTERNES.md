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
| **Sentinel Hub** | NDVI / couleur vraie Sentinel-2 (Process API) | `.env` : `SENTINEL_HUB_CLIENT_ID`, `SENTINEL_HUB_CLIENT_SECRET` | `backend/apps/sentinel/` |

Tuiles NASA affichées sur la carte : **placeholder PNG** via l’API interne `/api/v1/nasa/tiles/...` (pas de tuiles raster NASA réelles tant que l’ingestion WMS/XYZ n’est pas branchée).

Couches **Sentinel Hub** : tuiles réelles via `/api/v1/sentinel/tiles/{layer}/{z}/{x}/{y}.png` (NDVI colorisé, couleur vraie).

## Internes (pas externes)

| Composant | Rôle |
|-----------|------|
| **PostGIS** | Base géospatiale |
| **Redis** | Cache, Celery, Channels WebSocket |
| **API REST Django** | Toute la logique métier (`/api/v1/`) |
| **JWT** | Authentification |

## Fiches pédagogiques (PDF)

Les fiches listées via l’API incluent un champ **`pdf_url`** (chemin relatif `/api/v1/education/sheets/<id>/pdf/`) : le site ouvre toujours le PDF avec l’origine du navigateur. **GET** sur cette URL renvoie le PDF (ReportLab, mise en page type article LaTeX : Times, page de titre, résumé encadré, sections numérotées, pieds de page).

## Non intégrés — utiles si vous voulez aller plus loin

| Service | Intérêt possible | Statut |
|---------|------------------|--------|
| **Google Gemini API** | Assistant IA conversationnel (sols, parcelles, quiz, NASA) | ✅ Intégré via `GEMINI_API_KEY` — `POST /api/v1/assistant/chat/` |
| **OpenAI / Anthropic** | Même usage que Gemini | ❌ Non intégré |
| **Mapbox / MapTiler** | Fonds carte vectoriels haute qualité | ❌ Non intégré (OSM suffit pour le pilote) |
| **Sentinel Hub** | NDVI temps réel haute résolution | ✅ Intégré — voir `SENTINEL_HUB_*` dans `.env` |
| **Open-Meteo** | Météo locale pour recommandations irrigation | ❌ Non intégré |
| **SMTP (SendGrid, Brevo…)** | Emails réels mot de passe oublié | ⚠️ `send_mail` Django en dev (console) — configurer `EMAIL_*` en production |
| **Sentry / Datadog** | Monitoring erreurs | ❌ Non intégré |

## Variables d’environnement recommandées

Voir `.env.example` pour la liste à jour.

```bash
# NASA (fortement recommandé pour ingestion réelle)
NASA_EARTHDATA_TOKEN=

# Sentinel Hub (OAuth — dashboard https://apps.sentinel-hub.com/)
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=

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

- **Interne** : `parcel/zones/geojson/`, `parcel/live/`, `parcel/analyze/`.
- **NASA (optionnel, prod)** : lors de l’analyse d’une parcelle, le backend peut interroger le **catalogue STAC CMR** (public) sur la bbox du polygone et retourner un résumé dans `nasa.stac_parcel` (granules MODIS / SMAP récents). **Pas d’appel réseau pendant les tests** (`DJANGO_TEST=1`).

## Données & API gratuites ou ouvertes (suggestions)

| Source | Intérêt |
|--------|---------|
| **NASA Earthdata / STAC CMR** | Déjà utilisés pour MODIS, SMAP, GPM ; suffisent pour NDVI / humidité / pluie. |
| **SoilGrids (ISRIC)** | Propriétés pédologiques globales (résolution relative au produit). |
| **FAO HWSD / SoilInfo** | Contexte pédologique régional. |
| **Copernicus Browser (Sentinel-2)** | NDVI haute résolution (compte gratuit). |
| **Open-Meteo** | Météo locale pour conseils irrigation / stress thermique. |
| **OpenLandMap / OSM** | Occupation du sol, chemins, hydro (déjà OSM en fond carte). |

Clé API **non obligatoire** pour la plupart de ces couches ouvertes (respecter licences et citations).
