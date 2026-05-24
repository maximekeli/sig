<div align="center">

<!-- Bannière animée (SVG) -->
<img src="docs/assets/readme-hero.svg" width="100%" alt="SIG Sols Togo — bannière animée" />

<br/><br/>

<!-- Badges luxe + stack -->
<img src="https://img.shields.io/badge/Projet-SIG--SOLS--TOGO--2026--01-0d2818?style=for-the-badge&labelColor=c9a962&color=0d2818" alt="Projet"/>
<img src="https://img.shields.io/badge/DUSOL-DISIA-1a3d2e?style=for-the-badge&labelColor=8b6914&color=f5e6c8" alt="DUSOL DISIA"/>
<img src="https://img.shields.io/badge/Région-Maritime_Togo-2d8a52?style=for-the-badge&labelColor=061a12&color=86efac" alt="Maritime Togo"/>

<br/>

<img src="https://img.shields.io/badge/Django-5.x-092e20?style=flat-square&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/PostGIS-3.4-336791?style=flat-square&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Leaflet-carte-199900?style=flat-square&logo=leaflet&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-prêt-2496ED?style=flat-square&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/Licence-MIT-c9a962?style=flat-square"/>

<br/><br/>

### ✦ Système d'Information Géographique intelligent des sols ✦

*Cartographie · NASA Earthdata · Sentinel-2 · OpenWeather · IA fertilité · Éducation & communauté*

**Maître d'ouvrage** — DISIA, Ministère de l'Agriculture (Togo)  
**Maître d'œuvre** — **DUSOL**

<br/>

<!-- GIF-style pulse via shields (animated feel) -->
<img src="https://readme-typing-svg.demolab.com?font=Cormorant+Garamond&weight=600&size=22&duration=3500&pause=900&color=C9A962&center=true&vCenter=true&width=700&lines=Carte+interactive+PostGIS;NDVI+Sentinel-2+temps+r%C3%A9el;M%C3%A9t%C3%A9o+OpenWeather+parcelle;Quiz+%26+fiches+p%C3%A9dagogiques;Pr%C3%A9diction+IA+fertilit%C3%A9" alt="Animation texte"/>

</div>

---

## 🌿 Démarrage express

```bash
cp .env.example .env
# Renseigner OPENWEATHER_API_KEY, SENTINEL_HUB_*, NASA_EARTHDATA_* (voir .env.example)
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| 🌐 **Interface web** | http://localhost:8081 |
| 🔌 **API REST** | http://localhost:8081/api/v1/ |
| ⚙️ **Admin Django** | http://localhost:8081/admin/ |
| 💚 **Santé** | http://localhost:8081/health/ |

<details>
<summary><b>🔐 Comptes démo</b> (après <code>make seed</code>)</summary>

| Utilisateur | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `admin123` | Administrateur |
| `agent1` | `agent123` | Agent terrain |
| `public1` | `public123` | Public |

</details>

```bash
make seed          # Points sol, zones, quiz, NASA, modèle IA
make train-ml      # Réentraîner la fertilité (Random Forest / XGBoost)
make test          # Suite pytest
./scripts/fix-docker-web.sh   # Si API météo/Sentinel en 404 (conteneurs orphelins)
```

---

## ✨ Fonctionnalités phares

<table>
<tr>
<td width="50%" valign="top">

### 🗺️ Carte & parcelles
- Points de sol validés, heatmap pH
- **Parcelles** cantons / zones dégradées
- Analyse live : NASA, **Sentinel NDVI**, **OpenWeather**
- Dessin polygone, export GeoJSON / JSON

</td>
<td width="50%" valign="top">

### 🛰️ Données externes
- **NASA** MODIS, SMAP, STAC CMR
- **Sentinel Hub** — NDVI & couleur vraie
- **OpenWeather** — météo parcelle
- **Gemini** — assistant IA intégré

</td>
</tr>
<tr>
<td valign="top">

### 🎓 Éducation & social
- Quiz 100+ questions, badges, certificats PDF
- Fiches pédagogiques (PDF LaTeX-style)
- Vidéos, shorts, communauté, DM

</td>
<td valign="top">

### 🤖 Intelligence
- Prédiction fertilité (ML)
- Vulnérabilité & recommandations agricoles
- Modération vidéos, analytics admin

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Navigateur · Leaflet · PWA · animations.css (luxury UI)   │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  NGINX :8081  ──►  Django / Daphne  +  DRF  +  Channels WS   │
│                    Celery + Celery Beat                      │
└───────┬─────────────────────┬───────────────────────────────┘
        ▼                     ▼
   PostGIS 15            Redis 7
```

---

## 📦 Modules backend

| App | Rôle |
|-----|------|
| `accounts` | JWT, rôles, profils, GPS live, social |
| `soils` | Points sol, zones, dashboard KPI |
| `spatial` | Parcelles, proximité, buffer, vulnérabilité |
| `nasa` | Catalogue & ingestion Earthdata |
| `sentinel` | OAuth Sentinel Hub, tuiles NDVI |
| `weather` | OpenWeatherMap actuel & prévisions |
| `ml_predict` | Fertilité IA + Celery |
| `education` | Quiz, fiches, parcours, défis |
| `videos` | Communauté, modération |
| `assistant` | Chat Gemini contextuel |
| `sig_platform` | Alertes, exports, analytics |

---

## 🔌 API — extraits

Documentation : [`docs/API.md`](docs/API.md) · Postman : [`docs/postman/`](docs/postman/) · Externes : [`docs/API_EXTERNES.md`](docs/API_EXTERNES.md)

```bash
# Token
curl -s -X POST http://localhost:8081/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"agent1","password":"agent123"}'

# OpenWeather (statut)
curl -s http://localhost:8081/api/v1/weather/status/

# Sentinel Hub (statut)
curl -s http://localhost:8081/api/v1/sentinel/status/

# Parcelle avec Sentinel + météo
curl -s -X POST http://localhost:8081/api/v1/spatial/parcel/live/ \
  -H "Content-Type: application/json" \
  -d '{"zone_code":"CANTON-M01","use_sentinel":true,"use_weather":true,"use_ml":false}'
```

---

## 🎨 Interface — style & animations

Le frontend embarque une couche **luxe / anime-inspired** :

| Fichier | Effet |
|---------|--------|
| [`frontend/css/style.css`](frontend/css/style.css) | Palette émeraude & or, typo Cormorant / Outfit |
| [`frontend/css/animations.css`](frontend/css/animations.css) | `fadeUp`, `shimmer`, `navGlow`, stagger vues, toasts |
| [`frontend/css/enhancements.css`](frontend/css/enhancements.css) | Carte, parcelles, Sentinel, météo |

> Ouvrez la **Carte** → sélectionnez une parcelle → panneaux **Sentinel Hub** & **OpenWeather** avec cartes animées.

---

## 🛰️ Configuration `.env`

```bash
# OpenWeather — https://openweathermap.org/api
OPENWEATHER_API_KEY=

# Sentinel Hub — https://apps.sentinel-hub.com/
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=

# NASA Earthdata
NASA_EARTHDATA_TOKEN=

# Assistant IA
GEMINI_API_KEY=
```

Voir [`.env.example`](.env.example) pour la liste complète.

---

## 📚 Documentation

| Document | Contenu |
|----------|---------|
| [Guide utilisateur](docs/GUIDE_UTILISATEUR.md) | Prise en main interface |
| [API externes](docs/API_EXTERNES.md) | NASA, Sentinel, OpenWeather, OSM… |
| [NASA setup](docs/NASA_SETUP.md) | Ingestion Earthdata |
| [L1 Spécifications](docs/L1_SPECIFICATIONS.md) | Cahier des charges |

---

## 📋 Livrables TdR v3.0

| Code | Livrable | Lien |
|------|----------|------|
| L1 | Spécifications | `docs/L1_SPECIFICATIONS.md` |
| L2 | Modèle de données | `docs/L2_MODELE_DONNEES.md` |
| L3 | API REST | OpenAPI + Postman |
| L4 | Jeu de test | `seed_demo_data` |
| L5 | Module IA | `apps/ml_predict/` |
| L6 | Code source | Ce dépôt |
| L7 | Guide utilisateur | `docs/GUIDE_UTILISATEUR.md` |
| L8 | Déploiement | Docker + nginx |

---

<div align="center">

<br/>

**SIG Sols Togo** — *Intelligence des sols pour l'agriculture togolaise*

<img src="https://img.shields.io/badge/Made_with-♥_DUSOL-c9a962?style=for-the-badge&labelColor=0d2818&color=2d8a52"/>

<br/><sub>MIT · Données terrain DISIA · NASA domaine public · © DUSOL / DISIA</sub>

</div>
