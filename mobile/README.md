# SIG Sols Togo — Application mobile Flutter

Application mobile **Flutter** connectée au **même backend Django** que le site web (`/api/v1/`).

## Base de données partagée

Le site web et l'app mobile **n'ont pas de base locale séparée** : ils lisent et écrivent les **mêmes données** via l'API REST Django, qui utilise **PostGIS** (PostgreSQL + extensions spatiales).

| Client | Accès aux données |
|--------|-------------------|
| Site web (`frontend/`) | `fetch` → `http://localhost:8081/api/v1/…` |
| App mobile (`mobile/`) | `SigApi` → même URL |
| Backend | PostGIS `sig_sols` (conteneur Docker `db`) |

Comptes, points sol, parcelles, quiz, vidéos et communauté sont donc **synchronisés automatiquement** dès que les deux clients parlent au même backend.

Vérification : [Santé système](http://localhost:8081/health/?detail=1) ou onglet **Tableau de bord** / **Profil** dans l'app mobile.

## Fonctionnalités — mêmes API que le site web

| Service | Endpoints backend (clés dans `.env`) |
|---------|--------------------------------------|
| **NASA** | `/nasa/catalog/summary/`, tuiles `/nasa/tiles/…` |
| **Sentinel Hub** | `/sentinel/status/`, `/layers/`, `/analyze/`, tuiles |
| **OpenWeather** | `/weather/status/`, `/current/`, `/forecast/` |
| **Gemini IA** | `/assistant/status/`, `/assistant/chat/` |
| **ML** | `/ml/predict/`, `/ml/metrics/` |
| **Parcelle** | `/spatial/parcel/live/` (+ NASA, Sentinel, Météo, ML) |
| **Quiz** | `/education/quiz/start/`, `/answer/`, `/finish/` |
| **Vidéos / Communauté** | `/videos/posts/`, `/auth/feed/` |

Les clés API (NASA, Sentinel, OpenWeather, Gemini) sont **uniquement côté serveur Django** — jamais dans l'app mobile.

## Prérequis

- Flutter SDK 3.7+
- Backend Docker démarré : `http://localhost:8081`

## Tests

```bash
# Tests unitaires (rapides, sans backend)
cd mobile && flutter test --exclude-tags integration

# Tous les tests (+ API si backend actif)
../scripts/test-mobile.sh
```

## Lancer l'app

```bash
cd mobile
flutter pub get

# Linux desktop (même machine que Docker)
flutter run -d linux

# Émulateur Android (10.0.2.2 = localhost hôte)
flutter run -d android

# Téléphone physique (remplacer par l'IP de votre PC)
flutter run --dart-define=API_BASE_URL=http://192.168.1.XX:8081/api/v1
```

## Comptes démo

| Utilisateur | Mot de passe |
|-------------|--------------|
| `admin` | `admin123` |
| `agent1` | `agent123` |

## Configuration API

Fichier : `lib/core/config/env.dart`

| Plateforme | URL par défaut |
|------------|----------------|
| Linux / iOS simulateur | `http://localhost:8081/api/v1` |
| Android émulateur | `http://10.0.2.2:8081/api/v1` |
| Téléphone réel | `--dart-define=API_BASE_URL=http://<IP>:8081/api/v1` |

## Structure

```
lib/
├── app/           # Router, shell navigation
├── core/          # API client JWT, auth, thème
├── features/      # Écrans par module
├── models/        # DTOs
├── services/      # SigApi (façade REST)
└── shared/        # Widgets communs
```

## Développeur

**Maxime Dzidula KELI** · +33 754830039
