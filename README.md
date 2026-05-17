# SIG Sols Togo — SIG-SOLS-TOGO-2026-01

**Système d'Information Géographique intelligent des sols**  
Maître d'ouvrage : DISIA – Ministère de l'Agriculture (Togo)  
Maître d'œuvre : **DUSOL**  
Stack : GeoDjango · PostGIS · Leaflet · NASA Earthdata · Scikit-learn

## Démarrage rapide

```bash
cp .env.example .env
docker compose up -d --build
```

- **Interface web** : http://localhost:8081  
- **API** : http://localhost:8081/api/v1/  
- **Admin Django** : http://localhost:8081/admin/  
- **Santé** : http://localhost:8081/health/

### Comptes démo (après seed)

| Utilisateur | Mot de passe | Rôle |
|-------------|--------------|------|
| admin | admin123 | Administrateur |
| agent1 | agent123 | Agent |
| public1 | public123 | Public |

```bash
make seed          # 165 points, 10+ zones, quiz, NASA, modèle IA
make train-ml      # Réentraîner le modèle fertilité
make test          # Tests pytest
```

## Architecture

```
Navigateur (Leaflet) → NGINX → Django/GeoDjango + DRF + Celery
                              → PostGIS
                              → Redis
```

## Modules

| App | Rôle |
|-----|------|
| `accounts` | JWT, rôles Admin / Agent / Public |
| `soils` | Points de sol, zones administratives, dashboard |
| `spatial` | Proximité, intersection, buffer, vulnérabilité, NDVI, stats |
| `nasa` | Catalogue MODIS, SMAP, GPM, SRTM, MOD16 + ingestion |
| `ml_predict` | Prédiction fertilité (Random Forest / XGBoost) |
| `education` | Quiz, badges, fiches, classement |

## API (≥20 endpoints)

Voir `docs/API.md` et `docs/postman/SIG-SOLS.postman_collection.json`.

Exemples :

```bash
# Token
curl -X POST http://localhost:8080/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"agent1","password":"agent123"}'

# Points (léger, carte)
curl "http://localhost:8080/api/v1/points/?light=1"

# Prédiction IA
curl -X POST http://localhost:8080/api/v1/ml/predict/ \
  -H "Content-Type: application/json" \
  -d '{"ph":6.2,"humidity_pct":35,"soil_type":"limoneux"}'
```

## NASA Earthdata — bibliothèques intégrées

| Bibliothèque | Rôle |
|--------------|------|
| **earthaccess** | Téléchargement NASA simplifié |
| **pystac-client** | Catalogue satellite STAC (CMR) |
| **rasterio** | Découpe + extraction au point |
| **xarray + rioxarray** | Reprojection WGS84 |

```bash
docker compose exec web python manage.py ingest_nasa
docker compose exec web python manage.py ingest_nasa --enrich-only
```

Renseigner dans `.env` : `NASA_EARTHDATA_USERNAME` et `NASA_EARTHDATA_PASSWORD`.

Sans identifiants : catalogue STAC + démo. Avec identifiants : téléchargement et enrichissement NDVI/SMAP sur les points de sol.

## Livrables projet (TdR v3.0)

| Code | Statut |
|------|--------|
| L1 Spécifications | `docs/L1_SPECIFICATIONS.md` |
| L2 Modèle de données | `docs/L2_MODELE_DONNEES.md` |
| L3 API REST | OpenAPI via DRF + Postman |
| L4 Jeu de test | `seed_demo_data` |
| L5 Module IA | `apps/ml_predict/` |
| L6 Code source | Ce dépôt |
| L7 Guide utilisateur | `docs/GUIDE_UTILISATEUR.md` |
| L8 Déploiement | Docker + nginx |

## Licence

MIT — voir [LICENSE](LICENSE). Données terrain : propriété DISIA. Données NASA : domaine public (crédit requis).
# SIG
