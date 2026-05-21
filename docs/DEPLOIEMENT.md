# Déploiement production

## Prérequis

- Docker & Docker Compose
- Domaine avec HTTPS (Let's Encrypt recommandé)
- Variables dans `.env` : `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`

## Lancement

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

## HTTPS (nginx)

Configurer un reverse proxy TLS devant le port 8081 ou adapter `nginx/nginx.conf` pour écouter 443 avec certificats.

## Limitation de débit

- DRF : `THROTTLE_*` dans `.env`
- Middleware global : `MIDDLEWARE_RATE_PER_MIN` (défaut 300 req/min/IP)

## Santé

`GET /health/` — doit retourner 200.
