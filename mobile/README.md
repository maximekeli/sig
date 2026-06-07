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

## Synchronisation offline (points sol)

Comme le site web, l'app peut **enregistrer des points sol hors ligne** et les envoyer à PostGIS à la reconnexion :

1. Carte → activer **Ajouter point** → toucher la carte → remplir pH / humidité / type
2. Hors ligne : le point est mis en file (`sig_sols_offline_queue`, même clé que le navigateur)
3. À la reconnexion (ou tap sur la bannière orange) : envoi automatique via `POST /points/`

Les points créés sur mobile apparaissent sur le site web après synchronisation (validation agent requise).

## Fonctionnalités — parité avec le site web

| Module | Mobile | API |
|--------|--------|-----|
| **Carte** | NDVI NASA/Sentinel, ajout point offline, outils (proximité, heatmap, alertes, comparer, filtres, trajectoire, météo), export GeoJSON/CSV, import agent | `/points/`, `/heatmap/`, `/spatial/` |
| **Dashboard** | KPIs sols, APIs externes | `/dashboard/stats/` |
| **Quiz** | Parcours, badges, défi hebdo, classement | `/education/quiz/` |
| **Fiches** | PDF + favoris | `/education/sheets/`, `/auth/favorites/` |
| **Vidéos / Shorts** | Upload, likes, commentaires, stories | `/videos/` |
| **Communauté** | Fil, recherche, favoris, messages | `/auth/feed/`, `/auth/messages/` |
| **IA** | Chat Gemini | `/assistant/chat/` |
| **Profil** | Édition, mot de passe, photo, trajectoire | `/auth/profile/` |
| **Parcelle** | Zone canton + GPS | `/spatial/parcel/live/` |
| **Menu latéral** | Recherche, notifications (badge), mon espace, admin, aide, thème clair/sombre | `/platform/`, `/auth/notifications/` |
| **Auth** | Login, register, mot de passe oublié | `/auth/token/` |
| **Admin** | KPIs, validation points/vidéos, ML/NASA, exports CSV | `/platform/admin/` |
| **Offline** | File d'attente points sol → sync PostGIS | `POST /points/` |
| **Activité** | Suivi navigation (comme le web) | `POST /platform/activity/` |
| **Positions live** | Partage GPS + marqueurs agents + WebSocket | `/auth/location/`, `/ws/live/?token=…` |
| **i18n** | Français / English (menu latéral) | `LocaleService` |

Les clés API (NASA, Sentinel, OpenWeather, Gemini) restent **côté serveur Django** uniquement.

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
