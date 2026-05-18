# Configuration NASA Earthdata — SIG Sols Togo

## 1. Créer un compte

1. Inscription : https://urs.earthdata.nasa.gov/
2. Copier identifiant / mot de passe dans `.env` :

```env
NASA_EARTHDATA_USERNAME=votre_login
NASA_EARTHDATA_PASSWORD=votre_mot_de_passe
# OU token JWT depuis le profil Earthdata (recommandé si OAuth)
NASA_EARTHDATA_TOKEN=votre_token_jwt
```

3. Redémarrer : `docker compose restart web celery`

## 2. Bibliothèques Python (déjà installées)

```bash
pip install earthaccess pystac-client rasterio xarray rioxarray
```

| Outil | Fichier projet | Rôle |
|-------|----------------|------|
| earthaccess | `apps/nasa/earthdata.py` | Téléchargement granules |
| pystac-client | `apps/nasa/stac_client.py` | Catalogue STAC CMR |
| rasterio | `apps/nasa/raster_utils.py` | Extraction au point |
| rioxarray | `apps/nasa/raster_utils.py` | Reprojection WGS84 |

## 3. Lancer l'ingestion

```bash
docker compose exec web python manage.py ingest_nasa
```

Enrichit automatiquement les points de sol (NDVI, SMAP) si des rasters sont en cache.

## 4. API (admin JWT)

```bash
curl -X POST http://localhost:8081/api/v1/nasa/ingest/ \
  -H "Authorization: Bearer <token>"
```

## 5. Crédit scientifique

Toute publication doit citer : *NASA Earth Science Data Systems* et le produit utilisé (MOD13Q1, SPL3SMP, etc.).
